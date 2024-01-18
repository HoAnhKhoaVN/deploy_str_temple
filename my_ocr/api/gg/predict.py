# ref: https://cloud.google.com/vision/docs/fulltext-annotations#audience

from google.cloud import vision
import os
from typing import Text
from re import findall

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key/apikey.json'
CLIENT = vision.ImageAnnotatorClient()

def is_han_nom(
    text: Text
)-> bool:
    '''
    Hint: https://stackoverflow.com/questions/34587346/python-check-if-a-string-contains-chinese-character
    '''
    return len(findall(r'[\u4e00-\u9fff]+', text)) != 0

def detect_text(path: Text):
    """Detects text in the file."""
    # region 1. Input
    with open(path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    # endregion

    # region 2. Call API
    response = CLIENT.text_detection(image=image)
    texts = response.full_text_annotation
    
    # endregion

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )

    # region 3. Postprocess

    for page in texts.pages:
        for block in page.blocks:
            print(dir(block))
            print(block.bounding_box)
            print(block.paragraphs)
    
    exit()

    res = []
    for text in texts:
        print(f'text: {dir(text)}')
        transcription = text.description
        if not is_han_nom(transcription):
            continue

        # if len(transcription)>1:
        #     continue

        points= [
            [vertex.x, vertex.y] for vertex in text.bounding_poly.vertices
        ]

        _dict = {
            "transcription" : transcription,
            "points" : points,
            "difficult": False,
        }

        res.append(_dict)
    # endregion
    
    # region 4. Output
    res = str(res[1:]).replace("\'", "\"")
    dirname= os.path.dirname(path)
    basename = os.path.basename(path)
    basename_dir= os.path.basename(dirname)
    # endregion
    
    return f"{basename_dir}/{basename}\t{res}\n"
if __name__ == "__main__":
    IMG_PATH = 'D:/Master/OCR_Nom/experiments/str_vietnam_temple/input/13920412_1649559072027394_8604108607913927412_o.jpg'
    print(detect_text(path = IMG_PATH))