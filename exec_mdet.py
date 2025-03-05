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
    def __init__(self, image_files, threshold, session_root, diff_reasoning, skip, md_model, mediainfo=None):
        self.image_files = image_files
        self.threshold = threshold
        self.session_root = session_root
        #self.checkpoint = checkpoint
        self.diff_reasoning = diff_reasoning
        self.skip = skip
        self.verbose = False
        self.model = md_model
        self.mediainfo = mediainfo



    def save_detection_results(self, results, size, done=False):
        output_dir = self.session_root + "_out"
        #os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.basename(self.session_root)
        output_json_path = os.path.join(output_dir, f"{base_name}_output_{self.model}.json")
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
        df_obj = df[df['count'] > 0]
        df_obj.to_csv(output_csv_path, index=True)
        print(f'CSV saved: {output_csv_path}, {size} images processed')

        if done:
            df_corrupt = df[df['count'] < 0]
            if not df_corrupt.empty:
                for c in df_corrupt['img_id']:
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
            im_file = os.path.normpath(im_file)
            ex_file = os.path.basename(im_file)
            meta_folder = os.path.normpath(os.path.dirname(self.session_root)) + os.path.sep
            new_file_base = os.path.normpath(im_file.replace(meta_folder, "").replace(os.path.sep, "_out" + os.path.sep))
            new_file = os.path.normpath(os.path.join(meta_folder, new_file_base))

            if self.verbose:
                print(f"New file base: {new_file_base}")
                print(f"Meta folder: {meta_folder}")
                print(f"Processing {im_file} to {new_file}")
                

            if os.path.exists(new_file) and self.skip:
                print(f"{new_file} already exists. Skipping.")
                result = {
                    'img_id': im_file,
                    'detections': det_null,
                    'labels': 'animal',
                    'count': 1,
                    'bbox': det_null.xyxy,
                }
            else:
                pre_detects = prev_result['detections'] if prev_result else None
                result = pw_detect(
                    im_file, new_file, self.threshold,
                    pre_detects, self.diff_reasoning, self.verbose, self.model
                )
            if self.mediainfo is not None:
                self.mediainfo = pd.DataFrame(self.mediainfo)
                id_df = self.mediainfo[self.mediainfo['filePath'] == im_file]
                #print(f"ID: {id_df}")
                if not id_df.empty:
                    result['deploymentID'] = id_df['deploymentID'].iloc[0]
                    result['mediaID'] = id_df['mediaID'].iloc[0]
                    result['eventStart'] = id_df['timestamp'].iloc[0]
                    result['eventEnd'] = id_df['timestamp'].iloc[0]
                else:
                    print(f"Deployment ID not found for {im_file}")
                    result['deploymentID'] = None
            else:
                result['deploymentID'] = None
                result['mediaID'] = None
                result['eventStart'] = "unknown"
                result['eventEnd'] = "unknown"
            result['file'] = ex_file

                
            return result

        except Exception as e:
            print(f'Image {im_file} cannot be processed. Exception: {e}')
            return {
                'img_id': im_file,
                'detections': det_null,
                'file': os.path.basename(im_file),
                'count': -1,
                'eventStart': "unknown",
                'eventEnd': "unknown",
                'bbox': det_null.xyxy,
                'deploymentID': None,
                'file': ex_file
            }

    def run_detector_with_image_queue(self):
        try:
            cpu_count = max(1, multiprocessing.cpu_count() - 1)

            start_time = time.time()

            if torch.cuda.is_available():
                if self.diff_reasoning:
                    input("Differential reasoning is not supported with parallel processing. Will continue without it. Press Enter to continue.")
                    self.diff_reasoning = False
                    print("Differential reasoning is disabled.")
                with multiprocessing.Pool(cpu_count) as pool:
                    results = pool.map(process_image_helper, [(self, im_file) for im_file in self.image_files])
            else:
                results = []
                for im_file in self.image_files:
                    result = self.process_image(im_file=im_file, prev_result=results[-1] if results else None)
                    results.append(result)
                        
            print(f"Finished processing in {time.time() - start_time:.2f} sec")
            self.save_detection_results(results, size=len(results), done=True)

            
        except Exception as e:
            print(f'Exception: {e}')
            raise
