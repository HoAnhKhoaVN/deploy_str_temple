from flask import Flask, jsonify, request, send_file
from io import BytesIO
import base64
from PIL import Image
from numpy import array
from main import process
import logging
from log.logger import setup_logger
from numpy.random import uniform
from numpy import uint8
setup_logger()

app = Flask(__name__)

def pil_to_base64(
    image: Image,
    )-> base64:
    image_buffer = BytesIO()
    image.save(image_buffer, format='PNG')
    image_base64 = base64.b64encode(image_buffer.getvalue()).decode('utf-8')
    return image_base64


# Endpoint for receiving image and returning predicted image
@app.route('/predict', methods=['POST'])
def predict():
    logging.info("Processing...")
    # Get the image file from the request
    content_file = request.files['content_img']
    content_image = Image.open(content_file).convert('RGB')

    _input = array(content_image)
    pil_image, _= process(_input)
    response = jsonify({'processed_image': pil_to_base64(pil_image)})
    response.headers.add('Access-Control-Allow-Origin', '*')  # Cho phép truy cập từ domain của frontend
    return response

if __name__ == '__main__':
    # region warm up 10 times
    print(f'Warm up 10 times')
    img = uniform(0, 255, [640, 640, 3]).astype(uint8)
    for i in range(10):
        res, _ = process(img)
    # endregion

    # region Main process
    app.run(debug=True)
    # endregion