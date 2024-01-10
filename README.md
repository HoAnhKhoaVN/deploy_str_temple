# Installation
1. Install paddlepaddle
- Without GPU

```sh 
python -m pip install paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple
```
- With GPU
```sh
python -m pip install paddlepaddle-gpu -i https://pypi.tuna.tsinghua.edu.cn/simple
```
SRC: https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_en/quickstart_en.md

2. Install paddleocr
```sh
pip install "paddleocr>=2.0.1" --upgrade PyMuPDF==1.21.1
```
Thanks: https://stackoverflow.com/questions/76379293/how-can-i-fix-the-error-in-pymupdf-when-installing-paddleocr-with-pip

3. Install sklearn
```sh
pip install scikit-learn
```
4. Update libgomp1
```sh
apt-get install libgomp1
```
Thanks: https://stackoverflow.com/questions/43764624/importerror-libgomp-so-1-cannot-open-shared-object-file-no-such-file-or-direc

5. Update ffmpeg libsm6 libxext6 library
```sh
apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
```
Thanks: https://stackoverflow.com/questions/55313610/importerror-libgl-so-1-cannot-open-shared-object-file-no-such-file-or-directo

## Experiment
### Setup tool
```sh
pip install -e .
```

### Blendtext with random backgorund
```sh
source D:/Master/OCR_Nom/deploy/azure/str_vietnam_temple/.venv/Scripts/activate
python my_postprocess/blend_text.py
```

### Blendtext with bbox
```sh
source D:/Master/OCR_Nom/deploy/azure/str_vietnam_temple/.venv/Scripts/activate
python my_postprocess/blend_text_with_bbox.py
```

### Post-process with fill color
```sh
python my_postprocess/_postprocess.py
```


### Post-process with remove text
#### big lama
```sh
source D:/Master/OCR_Nom/deploy/azure/str_vietnam_temple/.venv/Scripts/activate
python my_postprocess/_postprocess_remove_bg.py
```


