from flask import Flask, jsonify, request
import matplotlib.image as mpimg
from skimage import exposure
import base64
import io
app = Flask(__name__)
error_messages = {1: 'Please put post request json in correct format',
                  2: 'Incorrect data types in request',
                  3: 'Username or request id does not exist'}
processing_choices = ['histogram_eq', 'contrast_str', 'log_compress', 'reverse_vid']
img_format_choices = ['JPG', 'JPEG', 'PNG', 'TIFF']
@app.route("/api/process_img", methods=["POST"])
def process_img_handler():
    r = request.get_json()
    flag = validate_process_img(r)
    if flag > 0:
        return error_messages[flag], 400
    # decode image
    list_of_decoded_imgs = []
    for base64_string in r['imgs']:
        # Image format should be passed along the request. I hard coded JPG
        decoded_img = decode_b64(base64_string, 'JPG')
        list_of_decoded_imgs.append(decoded_img)
    # process individual image
    list_of_processed_imgs = []
    for before_filtering in list_of_decoded_imgs:
        processed = exposure.equalize_hist(before_filtering)
        list_of_processed_imgs.append(processed)
    # encode image before sending it back
    list_of_processed_imgs_encoded = []
    for before_encoding in list_of_processed_imgs:
        b64_string = encode_b64(before_encoding)
        list_of_processed_imgs_encoded.append(b64_string)
    # convert to desired format
    # calculate histogram for that image
    # Store data to db
    # assemble return data
    data = {'request_id': '1',
            'processed_img': list_of_processed_imgs_encoded,
            'histograms': []}
    return jsonify(data), 200


def decode_b64(base64_string, img_format):
    image_bytes = base64.b64decode(base64_string)
    image_buf = io.BytesIO(image_bytes)
    return mpimg.imread(image_buf, format=img_format)


def encode_b64(image):
    image_buf = io.BytesIO()
    mpimg.imsave(image_buf, image, format='JPG')
    image_buf.seek(0)
    b64_bytes = base64.b64encode(image_buf.read())
    return str(b64_bytes, encoding='utf-8')


@app.route("/api/retrieve_request/<username>/<request_id>", methods=["GET"])
def retrieve_request_handler(username, request_id):
    # Query db given username and request id
    # return data
    pass


@app.route("/api/previous_request/<username>", methods=["GET"])
def previous_request_handler(username):
    # Query db for data
    # return data
    pass


@app.route("/api/user_metrics/<username>", methods=["GET"])
def user_metrics_handler(username):
    # query db for user user metrics
    # return data
    pass


def validate_process_img(r):
    try:
        username = r['username']
        num_img = r['num_img']
        imgs = r['imgs']
        processing = r['processing']
        img_format = r['img_format']
    except KeyError:
        print('here')
        return 1
    if not ((processing in processing_choices) and (img_format in img_format_choices)):
        # print((True and True))
        return 1
    try:
        num_img = int(num_img)
    except ValueError:
        return 2
    return 0


if __name__ == '__main__':
    app.run()  # host="0.0.0.0"
