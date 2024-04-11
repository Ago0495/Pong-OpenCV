from flask import Flask, request, jsonify, send_file
import base64
from PIL import Image
from io import BytesIO
import cv2 as cv
import numpy as np

app = Flask(__name__)

@app.route('/process-image', methods=['POST'])
def process_image():
    data = request.get_json()
    image_data = data['image']

    # Convert base64 image data to numpy array
    decoded_data = base64.b64decode(image_data.split(',')[1])
    nparr = np.frombuffer(decoded_data, np.uint8)
    image_np = cv.imdecode(nparr, cv.IMREAD_COLOR)

    # Example: Perform image recognition (replace with your actual image processing code)
    # result = your_image_recognition_function(image_np)

    # For demonstration, let's just return a simple response
    result = "Image received and processed."

    # Display the image
    cv.imshow('Processed Image', image_np)
    cv.waitKey(0)
    cv.destroyAllWindows()

    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
