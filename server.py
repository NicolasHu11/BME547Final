from flask import Flask, jsonify, request
import matplotlib.image as mpimg
from skimage import exposure
from skimage.util import invert
import base64
import io
import datetime
import numpy as np

app = Flask(__name__)
error_messages = {1: 'Please put post request json in correct format',
                  2: 'Incorrect data types in request',
                  3: 'Username does not exist',
                  4: 'Request ID does not exist'}
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
        decoded_img = decode_b64(base64_string, r['img_format'])
        list_of_decoded_imgs.append(decoded_img)
    # process individual image
    # print(r['procedure'])
    list_of_processed_imgs = process_imgs_with_method(list_of_decoded_imgs, r['procedure'])
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
    metadata = store_new_request(r, new_id, list_of_processed_imgs_encoded, time_received)
    # assemble return data
    data = {'request_id': new_id,
            'processed_img': list_of_processed_imgs_encoded,
            'histograms': [],
            'time_uploaded': metadata['time_uploaded'],
            'time_to_process': metadata['time_to_process'],
            'img_size': metadata['img_size']
            }
    return jsonify(data), 200

def process_imgs_with_method(list_of_decoded_imgs, procedure):
    list_of_processed_imgs = []
    for before_filtering in list_of_decoded_imgs:
        if procedure == 'histogram_eq':
            processed = exposure.equalize_hist(before_filtering)
        elif procedure == 'contrast_str':
            p2, p98 = np.percentile(before_filtering, (2, 98))
            processed = exposure.rescale_intensity(before_filtering, in_range=(p2, p98))
        elif procedure == 'log_compress':
            processed = exposure.adjust_log(before_filtering)
        else:
            processed = invert(before_filtering)
        list_of_processed_imgs.append(processed)
    return list_of_processed_imgs

num_requests = 0
def generate_request_id():
    global num_requests
    new_id = str(num_requests)
    num_requests += 1
    return str(num_requests)


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
    from mongodb import query_by_request_id
    request_file = query_by_request_id(username, request_id)
    if request_file == 0:
        return jsonify(error_messages[3]), 400
    elif request_file == 1:
        return jsonify(error_messages[4]), 400
    data = {
        'original_img': request_file.uploaded,
        'processed_img': request_file.processed,
        'histograms': []
    }
    # return data
    return jsonify(data), 200


@app.route("/api/previous_request/<username>", methods=["GET"])
def previous_request_handler(username):
    user_exists = validate_previous_request(username)
    if not user_exists:
        return jsonify(error_messages[3]), 400
    previous_request_ids = get_previous_requests(username)
    data = previous_request_preview(previous_request_ids)
    # return data
    return jsonify(data), 200

def previous_request_preview(previous_request_ids):
    from mongodb import query_by_request_id
    data = {}
    for id in request_id:
        request_file = query_by_request_id(username, id)

        data[id] = {
                'filename': request_file.filename,
                'procedure': request_file.procedure,
                'time_uploaded': request_file.time_uploaded,
                'time_to_process': request_file.time_to_process,
                'img_size': request_file.img_size
        }
    return data

def get_previous_requests(username):
    from mongodb import query_field
    request_id_list = query_field(username, 'request_id')
    print(request_id_list)
    return request_id_list

@app.route("/api/user_metrics/<username>", methods=["GET"])
def user_metrics_handler(username):
    # query db for user user metrics
    # return data
    pass

def validate_previous_request(username):
    from mongodb import check_user
    user_exists = check_user(username)
    return user_exists


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
    return db_data

def get_img_sizes(list_of_processed_imgs_encoded, img_format):
    img_sizes = []
    for base64_string in list_of_processed_imgs_encoded:
        decoded_img = decode_b64(base64_string, img_format)
        new_tuple = (decoded_img.shape[0], decoded_img.shape[1])
        img_sizes.append(new_tuple)
    return img_sizes


if __name__ == '__main__':
    app.run()  # host="0.0.0.0"
