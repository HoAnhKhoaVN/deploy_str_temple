source D:/Master/OCR_Nom/deploy/azure/str_vietnam_temple/.venv/Scripts/activate

IMG_PATH='241649023_543306286939449_2854614152112438955_n'
MODE='rm_text'
# MODE='fill_color'

python run.py -i input/$IMG_PATH.jpg \
              -o output/"$IMG_PATH"_"$MODE".jpg 