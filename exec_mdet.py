import os
#import sys
import time
import pandas as pd
import numpy as np
import multiprocessing
import torch

from image_demo import pw_detect
from PytorchWildlife import utils as pw_utils
from supervision.detection.core import Detections

def process_image_helper(args):
    instance, im_file = args
    return instance.process_image(im_file, None)

class ExecMdet:
    def __init__(self, image_files, threshold, session_root, checkpoint, diff_reasoning, skip, md_model):
        self.image_files = image_files
        self.threshold = threshold
        self.session_root = session_root
        #self.checkpoint = checkpoint
        self.diff_reasoning = diff_reasoning
        self.skip = skip
        self.verbose = False
        
        self.model = md_model



    def save_detection_results(self, results, size, done=False):
        output_dir = self.session_root + "_out"
        #os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.basename(self.session_root)
        output_json_path = os.path.join(output_dir, f"{base_name}_output{self.model}.json")
        output_csv_path = os.path.join(output_dir, f"{base_name}_output_{self.model}.csv")

        pw_utils.save_detection_json(
            results,
            output_json_path,
            categories={
                0: "animal",
                1: "person",
                2: "vehicle",
                3: "false_positive",
            },
            exclude_category_ids=[],
            exclude_file_path=None
        )
        print(f'JSON saved: {output_json_path}, {size} images processed')

        df = pd.DataFrame(results)
        df_obj = df[df['object'] > 0]
        df_obj.to_csv(output_csv_path, index=True)
        print(f'CSV saved: {output_csv_path}, {size} images processed')

        if done:
            df_corrupt = df[df['object'] < 0]
            if not df_corrupt.empty:
                for c in df_corrupt['file']:
                    print(f'{c} was corrupted')
                corrupt_csv_path = os.path.join(output_dir, f"{base_name}_corrupt.csv")
                df_corrupt.to_csv(corrupt_csv_path, index=True)

    def process_image(self, im_file, prev_result):
        det_null = Detections(
            xyxy=np.empty((0, 4), dtype=np.float32),
            mask=None, 
            confidence=np.array([], dtype=np.float32),
            class_id=np.array([], dtype=np.int32),
            tracker_id=None
        )
        try:
            folder = os.path.dirname(self.session_root)
            folderpath = folder + os.path.sep
            new_folder = im_file.replace(folderpath, "")
            ex_file = os.path.basename(new_folder)
            new_file = os.path.join(folder, new_folder.replace(os.path.sep, "_out" + os.path.sep))

            if os.path.exists(new_file) and self.skip:
                return {
                    'img_id': im_file,
                    'detections': det_null,
                    'labels': 'animal',
                    'object': 1,
                    'eventStart': 0,
                    'eventEnd': 0,
                    'Make': None,
                    'deploymentID': os.path.basename(self.session_root),
                    'file': ex_file
                }
            else:
                pre_detects = prev_result['detections'] if prev_result else None
                result = pw_detect(
                    im_file, new_file, self.threshold,
                    pre_detects, self.diff_reasoning, self.verbose, self.model
                )
                result['deploymentID'] = os.path.basename(self.session_root)
                result['file'] = ex_file

                if self.verbose:
                    print(result)
                
                return result

        except Exception as e:
            print(f'Image {im_file} cannot be processed. Exception: {e}')
            return {
                'img_id': im_file,
                'detections': det_null,
                'file': os.path.basename(im_file),
                'object': -1
            }

    def run_detector_with_image_queue(self):
        try:
            cpu_count = max(1, multiprocessing.cpu_count() - 1)
            #manager = multiprocessing.Manager()
            #return_list = manager.list()
            images = self.image_files

            start_time = time.time()

            if torch.cuda.is_available():
                with multiprocessing.Pool(cpu_count) as pool:
                    results = pool.map(process_image_helper, [(self, im_file) for im_file in images])
            else:
                results = []
                for im_file in images:
                    results.append(self.process_image(im_file, None))
                        
            print(f"Finished processing in {time.time() - start_time:.2f} sec")
            self.save_detection_results(results, size=len(results), done=True)
            
        except Exception as e:
            print(f'Exception: {e}')
            raise
