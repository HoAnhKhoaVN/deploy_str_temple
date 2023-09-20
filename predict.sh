source D:/Master/OCR_Nom/deploy/azure/str_vietnam_temple/.venv/Scripts/activate


INPUT='D:\Master\OCR_Nom\fulllow_ocr_temple\dataset\collect_data\collect_image_temple_to_evaluate\data_demo\demo\giay\input\de'
OUTPUT='D:\Master\OCR_Nom\fulllow_ocr_temple\dataset\collect_data\collect_image_temple_to_evaluate\data_demo\demo\giay\output\de'

python predict.py -i $INPUT -o $OUTPUT 