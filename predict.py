import os
import argparse
from main import process
from PIL import Image
from tqdm import tqdm
from typing import Text, List

def predict_folder(
    folder_in_path: Text,
    folder_out_path: Text,
):
    # region 2. Handle folder
    if not os.path.exists(folder_in_path):
        os.makedirs(folder_in_path, exist_ok= True)
    
    if not os.path.exists(folder_out_path):
        os.makedirs(folder_out_path, exist_ok= True)
    # endregion

    # region 3. Get all image in folder and predict sequentially
    avg_time = {
        'ocr': 0.0,
        'translate': 0.0,
        'postprocess': 0.0,
        'length': 0
    }
    for fn in tqdm(os.listdir(folder_in_path), desc= f"Predict image in folder {folder_in_path}"):
        # region 3.1. Get image and process
        img_path = os.path.join(folder_in_path, fn)
        try:
            pil_img_output, time_analysis = process(
                image_input_file= img_path,
                silent= True
            )
        except:
            print(f'Error image: {fn}')
            continue
        # endregion

        # region 3.2: Handle output image
        output_img_path = os.path.join(folder_out_path, fn)
        pil_img_output.save(output_img_path)
        # endregion

        # region 3.3: Handle time
        avg_time['ocr']+= time_analysis['full_ocr_time']
        avg_time['translate'] += time_analysis['translate_time']
        avg_time['postprocess'] += time_analysis['postprocess_time']
        avg_time['length']+=1
        # endregion
    # endregion

    # region 4: Analysis time
    print(f"Predict {avg_time['length']} images")
    print(f"Avg time to OCR: {avg_time['ocr']/avg_time['length']} seconds")
    print(f"Avg time to translate Han-Nom to Vietnamese: {avg_time['translate']/avg_time['length']} seconds")
    print(f"Avg time to postprocess: {avg_time['postprocess']/avg_time['length']} seconds")
    # endregion

if __name__ == '__main__':
    # FODLER_IN_PATH = 'input'
    # FODLER_OUT_PATH = 'output_demo'

    # region 1. Args
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=True,
        help="Path to folder input")
    
    ap.add_argument("-o", "--output", required=True,
        help="Path to folder output")
    args = vars(ap.parse_args())

    FODLER_IN_PATH = args["input"]
    FODLER_OUT_PATH = args["output"]


    # endregion

    # region 2. Handle folder
    if not os.path.exists(FODLER_IN_PATH):
        os.makedirs(FODLER_IN_PATH, exist_ok= True)
    
    if not os.path.exists(FODLER_OUT_PATH):
        os.makedirs(FODLER_OUT_PATH, exist_ok= True)
    # endregion

    # region 3. Get all image in folder and predict sequentially
    avg_time = {
        'ocr': 0.0,
        'translate': 0.0,
        'postprocess': 0.0,
        'length': 0
    }
    for fn in tqdm(os.listdir(FODLER_IN_PATH), desc= f"Predict image in folder {FODLER_IN_PATH}"):
        # region 3.1. Get image and process
        img_path = os.path.join(FODLER_IN_PATH, fn)
        try:
            pil_img_output, time_analysis = process(
                image_input_file= img_path,
                silent= True
            )
        except Exception as e:
            print(f"Error image: {img_path}")
            print(f"Error: {e}")
            continue
        # endregion

        # region 3.2: Handle output image
        output_img_path = os.path.join(FODLER_OUT_PATH, fn)
        pil_img_output.save(output_img_path)
        # endregion

        # region 3.3: Handle time
        avg_time['ocr']+= time_analysis['full_ocr_time']
        avg_time['translate'] += time_analysis['translate_time']
        avg_time['postprocess'] += time_analysis['postprocess_time']
        avg_time['length']+=1
        # endregion
    # endregion

    # region 4: Analysis time
    print(f"Predict {avg_time['length']} images")
    print(f"Avg time to OCR: {avg_time['ocr']/avg_time['length']} seconds")
    print(f"Avg time to translate Han-Nom to Vietnamese: {avg_time['translate']/avg_time['length']} seconds")
    print(f"Avg time to postprocess: {avg_time['postprocess']/avg_time['length']} seconds")
    # endregion


