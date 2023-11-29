import os
import sys
import time
import humanfriendly
from omegaconf import OmegaConf
from multiprocessing import Process
import multiprocessing
from threading import Thread

from image_demo import pw_detect
import visualization.visualization_utils as viz_utils



def create_new_structure(src_dir, dst_dir):
    for dir, _ ,_ in os.walk(src_dir):
        dirs_name = dir.replace(dst_dir, "")
        new_dir = dst_dir + "\\" + dirs_name.replace("\\", "_out\\") + "_out"
        os.makedirs(new_dir, exist_ok=True)

def find_image_files(folder_path):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    image_files = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(root, file))

    return image_files

def process_image(im_file,session_root,threshold):
    #session_root = session_root.replace("\\\\","\\")
    print(session_root)
    try:
        folder = os.path.dirname(session_root)
        folderpath = folder + "\\"
        new_folder = im_file.replace(folderpath,"").replace(".JPG","_bb.JPG")
        ex_file =os.path.basename(new_folder)
        new_file = os.path.join(folder,new_folder.replace("\\","_out\\"))
        if os.path.exists(new_file):
            print(f"{new_file} exists")
            object = 1
            result = {
                'file': im_file,
                'detections': 'exists',
            }
        else:
            pw_detect(im_file, new_file, threshold)

    except Exception as e:
        #if not quiet:
        print('Image {} cannot be processed. Exception: {}'.format(im_file, e))
        result = {
            'file': im_file,
            'failure': "FAILURE_INFER",
            'object': 0
        }
        return result

def producer_func(q,image_files):
    """
    Producer function; only used when using the (optional) image queue.

    Reads up to N images from disk and puts them on the blocking queue for processing.
    """

    if verbose:
        print('Producer starting'); sys.stdout.flush()

    for im_file in image_files:

        try:
            if verbose:
                print('Loading image {}'.format(im_file)); sys.stdout.flush()
            image = viz_utils.load_image(im_file)
        except Exception as e:
            print('Producer process: image {} cannot be loaded. Exception: {}'.format(im_file, e))
            #raise

        if verbose:
            print('Queueing image {}'.format(im_file)); sys.stdout.flush()
        q.put([im_file,image])

    q.put(None)

    print('Finished image loading'); sys.stdout.flush()


def consumer_func(q,return_queue,session_root=None,threshold=None,image_size=None):
    """
    Consumer function; only used when using the (optional) image queue.

    Pulls images from a blocking queue and processes them.
    """

    if verbose:
        print('Consumer starting'); sys.stdout.flush()

    start_time = time.time()
    print(start_time)
    #detector = load_detector(model_file)
    elapsed = time.time() - start_time
    print('Loaded model (before queueing) in {}'.format(humanfriendly.format_timespan(elapsed)))
    sys.stdout.flush()

    results = []

    n_images_processed = 0

    while True:
        r = q.get()
        if r is None:
            q.task_done()
            return_queue.put(results)
            return
        n_images_processed += 1
        im_file = r[0]
        image = r[1]
        if verbose or ((n_images_processed % 10) == 0):
            elapsed = time.time() - start_time
            images_per_second = n_images_processed / elapsed
            print('De-queued image {} ({}/s) ({})'.format(n_images_processed,
                                                          images_per_second,
                                                          im_file));
            sys.stdout.flush()
        process_image(im_file,session_root,threshold)
        if verbose:
            print('Processed image {}'.format(im_file)); sys.stdout.flush()
        q.task_done()

def run_detector_with_image_queue(image_files, threshold, session_root,
                                  quiet=False,image_size=None):
    """
    Driver function for the (optional) multiprocessing-based image queue; only used when --use_image_queue
    is specified.  Starts a reader process to read images from disk, but processes images in the
    process from which this function is called (i.e., does not currently spawn a separate consumer
    process).
    """
    try:
        q = multiprocessing.JoinableQueue(maxsize=max_queue_size)
        return_queue = multiprocessing.Queue(1)

        if use_threads_for_queue:
            producer=Thread(target=producer_func,args=(q,image_files))
            print('Using threads for queue')
        else:
            producer=Process(target=producer_func,args=(q,image_files))
            print('Using processes for queue')
        producer.daemon = False
        producer.start()

        # TODO
        #
        # The queue system is a little more elegant if we start one thread for reading and one
        # for processing, and this works fine on Windows, but because we import TF at module load,
        # CUDA will only work in the main process, so currently the consumer function runs here.
        #
        # To enable proper multi-GPU support, we may need to move the TF import to a separate module
        # that isn't loaded until very close to where inference actually happens.
        run_separate_consumer_process = False

        if run_separate_consumer_process:
            if use_threads_for_queue:
                consumer = Thread(target=consumer_func,args=(q,return_queue, session_root,
                                                            threshold,image_size,))
            else:
                consumer = Process(target=consumer_func,args=(q,return_queue, session_root,
                                                            threshold,image_size,))
            consumer.daemon = True
            consumer.start()
        else:
            consumer_func(q,return_queue,session_root,threshold,image_size,)

        producer.join()
        print('Producer finished')

        if run_separate_consumer_process:
            consumer.join()
            print('Consumer finished')
        else:
            print('Consumer ended')

        q.join()
        print('Queue joined')

        if not return_queue.empty():
            results = return_queue.get()

            return results
        
        else:
            print('Warning: no results returned from queue')
            return []
    except Exception as e:
        print('Exception: {}'.format(e))
        raise


cli_conf = OmegaConf.from_cli()  # command line interface config

session_root = cli_conf.get("session_root")

threshold = cli_conf.get("threshold")

parent_dir = os.path.dirname(session_root) + "\\"
create_new_structure(session_root, parent_dir)
image_files = find_image_files(session_root)

# Number of images to pre-fetch
max_queue_size = 10
use_threads_for_queue = True
verbose = False

run_detector_with_image_queue(image_files, threshold=threshold, session_root=session_root, quiet=False, image_size=None)
