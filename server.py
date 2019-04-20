from flask import Flask, jsonify, request
import matplotlib.image as mpimg
from skimage import exposure
import base64
import io
import datetime

app = Flask(__name__)
error_messages = {1: 'Please put post request json in correct format',
                  2: 'Incorrect data types in request',
                  3: 'Username or request id does not exist'}
procedure_choices = ['histogram_eq', 'contrast_str', 'log_compress', 'reverse_vid']
img_format_choices = ['JPG', 'JPEG', 'PNG', 'TIFF']
num_requests = 1


@app.route("/api/process_img", methods=["POST"])
def process_img_handler():
    time_received = datetime.datetime.now()
    r = request.get_json()
    # flag is the result of request validation
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
        # Only support equalize_hist for now
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
    new_id = generate_request_id()
    print('New request id is {}'.format(new_id))
    # store_new_request(r, new_id, list_of_processed_imgs_encoded, time_received)
    # assemble return data
    data = {'request_id': new_id,
            'processed_img': list_of_processed_imgs_encoded,
            'histograms': []}
    return jsonify(data), 200

# needs work

num_requests = 0
def generate_request_id():
    global num_requests
    new_id = str(num_requests)
    num_requests += 1
    return num_requests


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
    from mongodb import query_field, query_by_request_id
    # Query db for data
    request_id = query_field(username, 'request_id')
    data = {}
    for id in request_id:
        request_file = query_by_request_id(username, id)

        data[id] = {
                'filename': request_file.filename,
                'procedure': request_file.procedure,
                'upload time': request_file.time_uploaded
        }

    # return data
    return jsonify(data), 200


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
        procedure = r['procedure']
        img_format = r['img_format']
        filename = r['filename']
    except KeyError:
        return 1
    if not ((procedure in procedure_choices) and (img_format in img_format_choices)):
        return 1
    try:
        num_img = int(num_img)
    except ValueError:
        return 2
    return 0


def store_new_request(r, request_id, list_of_processed_imgs_encoded, time_received):
    db_data = {
        'uploaded': r['imgs'],
        'processed': list_of_processed_imgs_encoded,
        'img_format': r['img_format'],
        'time_uploaded': time_received.strftime('%Y-%m-%d %H:%M:%S'),
        'time_to_process': (datetime.datetime.now() - time_received).total_seconds(),
        'img_size': get_img_sizes(list_of_processed_imgs_encoded, r['img_format']),
        'procedure': r['procedure'],
        'filename': r['filename']
    }
    print('')
    from mongodb import save_a_new_request
    save_a_new_request(r['username'], request_id, db_data)


def get_img_sizes(list_of_processed_imgs_encoded, img_format):
    img_sizes = []
    for base64_string in list_of_processed_imgs_encoded:
        decoded_img = decode_b64(base64_string, img_format)
        new_tuple = (decoded_img.shape[0], decoded_img.shape[1])
        img_sizes.append(new_tuple)
    return img_sizes


if __name__ == '__main__':
    app.run()  # host="0.0.0.0"
