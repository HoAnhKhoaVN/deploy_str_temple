import os
from enum import Enum
from google.cloud import vision
from PIL import Image, ImageDraw, ImageFont
from typing import Text, List, Dict, Tuple
CH_FONT = 'D:/Master/OCR_Nom/experiments/str_vietnam_temple/font/NomKhai.ttf'

class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5

def draw_bbox(
    image: Image,
    bboxes : List[int],
    texts: List[Text],
    color: Text
)->Image:
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(
        font = CH_FONT,
        size = 32
    )
    for text , bb in zip(texts, bboxes):
        draw.polygon(
            xy = [
                bb.vertices[0].x,
                bb.vertices[0].y,
                bb.vertices[1].x,
                bb.vertices[1].y,
                bb.vertices[2].x,
                bb.vertices[2].y,
                bb.vertices[3].x,
                bb.vertices[3].y,
            ],
            fill= None,
            outline= color,
            width= 3
        )

        draw.text(
            xy = (bb.vertices[0].x, bb.vertices[0].y),
            text = text,
            stroke_width= 1,
            fill= 'red',
            font= font,
            align= 'center'
        )

    return image

def get_document_bounds(image_file: Text)-> Tuple:
    """Finds the document bounds given an image and feature type.

    Args:
        image_file: path to the image file.

    Returns:
        List of coordinates for the corresponding feature type.
    """
    client = vision.ImageAnnotatorClient()
    bounds = []

    with open(image_file, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    
    texts = response.text_annotations
    description_text = texts[0].description.split("\n")
    print(f'description_text: {description_text}')

    document = response.full_text_annotation

    # Collect specified feature bounds by enumerating all document features
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                bounds.append(paragraph.bounding_box)

    # The list `bounds` contains the coordinates of the bounding boxes.
    return bounds, description_text

def process(
    filein: Text,
    fileout: Text
)-> None:
    """"""
    print(f"get_document_bounds")
    bboxes, texts = get_document_bounds(image_file= filein)

    print("draw_bbox")
    final_img : Image = draw_bbox(
        image= Image.open(filein),
        bboxes= bboxes,
        texts = texts,
        color= "green"
    )

    final_img.save(fileout)

if __name__ == '__main__':
    # FN = '13895076_1026434584091596_55417407642244028_n'
    # FN = 'cau_doi_1'
    FN = 'err1'

    FI = f"D:/Master/OCR_Nom/experiments/str_vietnam_temple/input/{FN}.jpg"
    FO = f"{FN}.png"

    process(
        filein= FI,
        fileout= FO
    )