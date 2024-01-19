import os
from enum import Enum
from google.cloud import vision
from PIL import Image, ImageDraw, ImageFont
from typing import Text, List, Dict
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
        size = 10
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

def get_document_bounds(
    image_file: Text,
    feature: FeatureType
)-> List:
    client = vision.ImageAnnotatorClient()
    res = []
    
    # region 1. Read binary image
    with open(image_file, 'rb') as f:
        content = f.read()

    # endregion
        
    # Call API
    
    image = vision.Image(content = content)
    response = client.text_detection(image)
    texts = response.text_annotations
    description_text = texts[0].description
    print(f'description_text: {description_text}')

    # Collect specified feature bounds by enumerating all document features.


    texts = response.full_text_annotation
    for page in texts.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbols in word.symbols:
                        if feature == FeatureType.SYMBOL:
                            res.append(symbols.bounding_box)
                        
                    if feature == FeatureType.WORD:
                        res.append(word.bounding_box)
                        
                if feature == FeatureType.PARA:
                    res.append(paragraph)
            
            if feature == FeatureType.BLOCK:
                res.append(block.bounding_box)
    
    return res

def get_document_bounds_baseline(image_file, feature):
    """Finds the document bounds given an image and feature type.

    Args:
        image_file: path to the image file.
        feature: feature type to detect.

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
                for word in paragraph.words:
                    for symbol in word.symbols:
                        if feature == FeatureType.SYMBOL:
                            bounds.append(symbol.bounding_box)

                    if feature == FeatureType.WORD:
                        bounds.append(word.bounding_box)

                if feature == FeatureType.PARA:
                    bounds.append(paragraph.bounding_box)


            if feature == FeatureType.BLOCK:
                bounds.append(block.bounding_box)

    # The list `bounds` contains the coordinates of the bounding boxes.
    return bounds, description_text

def detect_text(
    path: Text
)-> List[Dict]:
    # region 1. Constant
    client = vision.ImageAnnotatorClient()
    res = []

    # endregion

    # region 2. Read image
    with open(path, 'rb') as f:
        content = f.read()
    
    # endregion
        
    # region 3. Call API
    image = vision.Image(content = content)
    response = client.text_detection(image = image)
    texts = response.text_annotations

    # endregion
        
    # region 4. Show text and bbox

    # region 4.1: Text
    description_text : Text = texts[0].description
    lst_description_text : List[Text] = description_text.split('\n')
    print(f'description_text: {lst_description_text}')

    # endregion

    # region 4.2: BBox
    for text in texts:
        vertices = [
            [vertex.x, vertex.y] for vertex in text.bounding_poly.vertices
        ]

        print(f'vertices: {vertices}')
        print(f'text: {text.description}')

    # endregion

    # endregion

def process(
    filein: Text,
    fileout: Text
)-> None:
    """"""
    print(f"get_document_bounds")
    bboxes, texts = get_document_bounds_baseline(
        image_file= filein,
        feature= FeatureType.PARA
    )

    print("draw_bbox")
    final_img : Image = draw_bbox(
        image= Image.open(filein),
        bboxes= bboxes,
        texts = texts,
        color= "green"
    )

    final_img.save(fileout)

if __name__ == '__main__':
    FI = "D:/Master/OCR_Nom/experiments/str_vietnam_temple/input/cau_doi_1.jpg"
    FO = "cau_doi_1.png"

    process(
        filein= FI,
        fileout= FO
    )

    # detect_text(path = FI)