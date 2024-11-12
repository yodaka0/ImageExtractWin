import os
import sys
import time
import pandas as pd
import numpy as np
import multiprocessing

from image_demo import pw_detect
from PytorchWildlife import utils as pw_utils
from supervision.detection.core import Detections

class ExecMdet:
    def __init__(self, image_files, threshold, session_root, checkpoint, diff_reasoning, skip, md_model):
        self.image_files = image_files
        self.threshold = threshold
        self.session_root = session_root
        self.checkpoint = checkpoint
        self.diff_reasoning = diff_reasoning
        self.skip = skip
        self.verbose = False
        self.model = md_model


    def save_detection_results(self, results, size, done=False):
        """
        Save detection results in JSON and CSV formats, and print the status of the output.

        :param results: The detection results to be saved.
        :param session_root: The root path for the session.
        """
        output_dir = self.session_root + "_out"
        output_json_path = os.path.join(output_dir, os.path.basename(self.session_root) + "_output" + str(size) + ".json")
        output_csv_path = os.path.join(output_dir, os.path.basename(self.session_root) + "_output" + str(size) + ".csv")
        
        # Save detection results in JSON format
        pw_utils.save_detection_json(
            results, 
            output_json_path,
            categories={
                0: "animal",
                1: "person",
                2: "vehicle",
                3: "false_positive",
            },
            exclude_category_ids=[],  # Category IDs can be found in the definition of each model.
            exclude_file_path=None
        )
        print('Output JSON file saved at {}'.format(output_json_path))
        sys.stdout.flush()  # Ensure the print statement is immediately output

        # Convert results to DataFrame
        results_dataframe = pd.DataFrame(results)
        results_dataframe_object = results_dataframe[results_dataframe['object'] > 0]

        # Save results DataFrame to CSV
        results_dataframe_object.to_csv(output_csv_path, index=True)
        print('Output CSV file saved at {}'.format(output_csv_path))
        sys.stdout.flush()  # Ensure the print statement is immediately output

        # Check for and save corrupt results
        
        if done:
            results_dataframe_corrupt = results_dataframe[results_dataframe['object'] < 0]
            if len(results_dataframe_corrupt) > 0:
                for corrupt in results_dataframe_corrupt['file']:
                    print('{} was corrupted'.format(corrupt))
                output_corrupt_csv_path = os.path.join(output_dir, os.path.basename(self.session_root) + "_corrupt.csv")
                results_dataframe_corrupt.to_csv(output_corrupt_csv_path, index=True)
                sys.stdout.flush()  # Ensure the print statement is immediately output


    def process_image(self, im_file, prev_result):

        det_null = Detections(xyxy=np.empty((0, 4), dtype=np.float32), mask=None, 
                            confidence=np.array([], dtype=np.float32), class_id=np.array([], dtype=np.int32), tracker_id=None)
        try:
            folder = os.path.dirname(self.session_root)
            folderpath = folder + os.path.sep
            new_folder = im_file.replace(folderpath, "")
            ex_file = os.path.basename(new_folder)
            new_file = os.path.join(folder, new_folder.replace(os.path.sep, "_out" + os.path.sep))
            
            if os.path.exists(new_file) and self.skip:
                print(f"{new_file} exists")
                result = {
                    'img_id': im_file,
                    'detections': det_null,
                    'labels': 'animal',
                    'object': 1,
                    'eventStart': 0,
                    'eventEnd': 0,
                    'Make': None,
                }
            else:
                if prev_result is not None:
                    pre_detects = prev_result['detections']
                else:
                    pre_detects = None
                result = pw_detect(im_file, new_file, self.threshold, pre_detects, self.diff_reasoning, self.verbose, self.model)
            result['deploymentID'] = os.path.basename(self.session_root)
            result['file'] = ex_file

        except Exception as e:
            print(f'Image {im_file} cannot be processed. Exception: {e}')
            result = {
                'img_id': im_file,
                'detections': det_null,
                'file': os.path.basename(im_file),
                'object': -1
            }
        
        return result
        

    def producer_func(self, q):
        """
        Producer function; only used when using the (optional) image queue.

        Reads up to N images from disk and puts them on the blocking queue for processing.
        """

        if self.verbose:
            print('Producer starting'); sys.stdout.flush()

        for im_file in self.image_files:

            try:
                if self.verbose:
                    print('Loading image {}'.format(im_file)); sys.stdout.flush()
                #image = viz_utils.load_image(im_file)
            except Exception as e:
                print(f'Producer process: image {im_file} cannot be loaded. Exception: {e}')
                #raise

            if self.verbose:
                print('Queueing image {}'.format(im_file)); sys.stdout.flush()
            q.put(im_file)

        q.put(None)

        print('Finished image loading'); sys.stdout.flush()


    def consumer_func(self, q, return_queue):
        """
        Consumer function; only used when using the (optional) image queue.

        Pulls images from a blocking queue and processes them.
        """

        if self.verbose:
            print('Consumer starting'); sys.stdout.flush()

        start_time = time.time()
        results = []

        n_images_processed = 0

        while True:
            im_file_q = q.get()
            if im_file_q is None:
                q.task_done()
                self.save_detection_results(results, size=len(results), done=True)
                return_queue.put(results)
                return
            n_images_processed += 1
            if self.verbose or ((n_images_processed % 10) == 0):
                time_diff = time.time() - start_time
                images_per_second = n_images_processed / time_diff if time_diff > 0 else float('inf')
                print(f'De-queued image {n_images_processed} ({images_per_second}/s)')
                sys.stdout.flush()
            if self.checkpoint is not None and self.checkpoint > 0 and ((n_images_processed % self.checkpoint) == 0):
                    self.save_detection_results(results, size=n_images_processed, done=False)
            prev_result = None if len(results) == 0 else results[-1]
            result = self.process_image(im_file_q, prev_result)
            results.append(result)
            if self.verbose:
                print('Processed image {}'.format(im_file_q)); sys.stdout.flush()
            q.task_done()
        
        
    def run_detector_with_image_queue(self):

        try:
            q = multiprocessing.JoinableQueue(maxsize=10)
            return_queue = multiprocessing.Queue(1)

            producer = multiprocessing.Process(target=self.producer_func, args=(q,))
            producer.daemon = False
            producer.start()
            print('Producer started')

            consumer = multiprocessing.Process(target=self.consumer_func, args=(q, return_queue))
            consumer.daemon = False
            consumer.start()

            producer.join()
            print('Producer finished')

            q.join()
            print('Queue joined')
                
            return
            
        except Exception as e:
            print('Exception: {}'.format(e))
            raise
