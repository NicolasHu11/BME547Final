import base64
import datetime
import io

import matplotlib.image as mpimg
import numpy as np
from flask import Flask, jsonify, request
from skimage import exposure
from skimage.util import invert

app = Flask(__name__)
error_messages = {1: 'Please put post request json in correct format',
                  2: 'Incorrect data types in request',
                  3: 'Username does not exist',
                  4: 'Request ID does not exist'}
procedure_choices = ['histogram_eq', 'contrast_str', 'log_compress',
                     'reverse_vid']
img_format_choices = ['JPG', 'JPEG', 'PNG', 'TIFF',
                      'jpg', 'jpeg', 'png', 'tiff']
num_requests = 1


@app.route("/api/process_img", methods=["POST"])
def process_img_handler():
    """Request handler for process_img

    Takes in one or multiple images, performs the request procedure and returns
    the processed image along with meta data back. Only one file type and one
    procedure is allowed for each request

    Returns:
        tuple: data in json form and status code
    """
    time_received = datetime.datetime.now()
    r = request.get_json()
    # flag is the result of request validation
    flag = validate_process_img(r)
    if flag > 0:
        return error_messages[flag], 400
    # decode image
    list_of_decoded_imgs = decode_imgs_from_request(r)
    # process individual image
    list_of_processed_imgs = process_imgs_with_method(list_of_decoded_imgs,
                                                      r['procedure'])
    # encode image before sending it back
    list_of_processed_imgs_encoded = encode_imgs_b64(list_of_processed_imgs)
    # calculate histogram for original and processed image
    original_histograms = get_histograms(list_of_decoded_imgs)
    processed_histograms = get_histograms(list_of_processed_imgs)
    # Generate new request id. Request id is unique for every request
    new_id = generate_request_id()
    print('New request id is {}'.format(new_id))
    # Store data to db
    metadata = store_new_request(r, new_id, list_of_processed_imgs_encoded,
                                 time_received)
    # assemble return data
    data = {'request_id': new_id,
            'processed_img': list_of_processed_imgs_encoded,
            'original_histograms': original_histograms,
            'processed_histograms': processed_histograms,
            'time_uploaded': metadata['time_uploaded'],
            'time_to_process': metadata['time_to_process'],
            'img_size': metadata['img_size']
            }
    return jsonify(data), 200


def encode_imgs_b64(list_of_processed_imgs):
    """Takes a list of image matrices and encodes them in b64

    Args:
        list_of_processed_imgs (list): each entry is a matrix image

    Returns:
        list: each entry is a str that corresponds to the image
    """
    list_of_processed_imgs_encoded = []
    for before_encoding in list_of_processed_imgs:
        b64_string = encode_b64(before_encoding, 'JPG')
        list_of_processed_imgs_encoded.append(b64_string)
    return list_of_processed_imgs_encoded


def decode_imgs_from_request(r):
    """Extracts images from process_img POST request

    Args:
        r (dict): request json

    Returns:
        list: all images from the request in matrix form
    """
    list_of_decoded_imgs = []
    for base64_string in r['imgs']:
        decoded_img = decode_b64(base64_string, r['img_format'])
        list_of_decoded_imgs.append(decoded_img)
    return list_of_decoded_imgs


def process_imgs_with_method(list_of_decoded_imgs, procedure):
    """Performs the image processing procedure on a list of images

    Args:
        list_of_decoded_imgs (list): all images from the request in matrix form
        procedure (str): specifies which procedure to perform

    Returns:
        list: all images after applying the procedure
    """
    list_of_processed_imgs = []
    for before_filtering in list_of_decoded_imgs:
        if procedure == 'histogram_eq':
            processed = exposure.equalize_hist(before_filtering)
        elif procedure == 'contrast_str':
            p2, p98 = np.percentile(before_filtering, (2, 98))
            processed = exposure.rescale_intensity(before_filtering,
                                                   in_range=(p2, p98))
        elif procedure == 'log_compress':
            processed = exposure.adjust_log(before_filtering)
        else:
            processed = invert(before_filtering)
        list_of_processed_imgs.append(processed)
    return list_of_processed_imgs


def generate_request_id():
    """Generates a new request ID each time this function is called

    Starts at 1 when the program launches. All subsequent requests will receive
    unique IDs.

    Returns:
        str: new request ID generated
    """
    global num_requests
    new_id = str(num_requests)
    num_requests += 1
    return new_id


def decode_b64(base64_string, img_format):
    """Decodes a single image from b64 format

    Args:
        base64_string (str): image before decoding
        img_format (str): what format the string was encoded in

    Returns:
        ndarray: image in matrix form
    """
    image_bytes = base64.b64decode(base64_string)
    image_buf = io.BytesIO(image_bytes)
    return mpimg.imread(image_buf, format=img_format)


def encode_b64(image, img_format):
    """Encodes a single image with b64

    Args:
        image (ndarray): image in matrix form
        img_format (str): format to encode image

    Returns:
        str: encoded image
    """
    image_buf = io.BytesIO()
    mpimg.imsave(image_buf, image, format=img_format)
    image_buf.seek(0)
    b64_bytes = base64.b64encode(image_buf.read())
    return str(b64_bytes, encoding='utf-8')


@app.route("/api/retrieve_request/<username>/<request_id>", methods=["GET"])
def retrieve_request_handler(username, request_id):
    """Request handler for retrieving a specific past request

    Args:
        username (str): user who initiated the request
        request_id (str): unique request id issued for that request

    Returns:
        tuple: data in json form and status code
    """
    # Query db given username and request id
    from mongodb import query_by_request_id
    request_file = query_by_request_id(username, request_id)
    if request_file == 0:
        return jsonify(error_messages[3]), 400
    elif request_file == 1:
        return jsonify(error_messages[4]), 400
    uploaded_img = []
    processed_img = []
    for img in request_file.uploaded:
        uploaded_img.append(decode_b64(img, 'JPG'))
    for img in request_file.processed:
        processed_img.append(decode_b64(img, 'JPG'))
    original_histograms = get_histograms(uploaded_img)
    processed_histograms = get_histograms(processed_img)
    data = {
        'original_img': request_file.uploaded,
        'processed_img': request_file.processed,
        'original_histograms': original_histograms,
        'processed_histograms': processed_histograms,
        'filename': request_file.filename,
        'procedure': request_file.procedure,
        'time_uploaded': request_file.time_uploaded,
        'time_to_process': request_file.time_to_process,
        'img_size': request_file.img_size
    }
    # return data
    return jsonify(data), 200


@app.route("/api/previous_request/<username>", methods=["GET"])
def previous_request_handler(username):
    """Request handler for previewing all previous requests of a given user

    Args:
        username (str): user who initiated the request

    Returns:
        tuple: data in json form and status code
    """
    user_exists = validate_previous_request(username)
    if not user_exists:
        return jsonify(error_messages[3]), 400
    previous_request_ids = get_previous_requests(username)
    data = previous_request_preview(username, previous_request_ids)
    # return data
    return jsonify(data), 200


def previous_request_preview(username, previous_request_ids):
    """Assembles summary data for each past request for a user

    Used when a user wants to retrieve a past request. Summary info is provided
    for each request they had in the past

    Args:
        username (str): user initiating the request
        previous_request_ids (list): each term is one of their request IDs in
        str format

    Returns:
        dict: Keys are request IDs, each value is another dict with details
            concerning that request
    """
    from mongodb import query_by_request_id
    data = {}
    for id in previous_request_ids:
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
    """Generates a list of previous request IDs given username

    Args:
        username (str): user initiating the request

    Returns:
        list: each term is a request ID in str format
    """
    from mongodb import query_field
    request_id_list = query_field(username, 'request_id')
    print(request_id_list)
    return request_id_list


@app.route("/api/user_metrics/<username>", methods=["GET"])
def user_metrics_handler(username):
    """Request handler for retrieving user metrics

    Args:
        username (str): user who initiated the request

    Returns:
        tuple: data in json form and status code
    """
    user_exists = validate_previous_request(username)
    if not user_exists:
        return jsonify(error_messages[3]), 400
    # query db for user user metrics
    metrics = get_user_metrics(username)
    num_actions = metrics[0]
    user_creation_time = metrics[1]
    data = {'num_actions': num_actions,
            'user_creation_time': user_creation_time
            }
    # return data
    return jsonify(data), 200


def validate_previous_request(username):
    """Validates whether the user had any previous requests

    Args:
        username (str): user initiating the request

    Returns:
        int: 0 if user does not exist in database, 1 otherwise
    """
    from mongodb import check_user
    user_exists = check_user(username)
    return user_exists


def get_user_metrics(username):
    """Retrieves user metrics information given username

    Args:
        username (str): user initiating the request

    Returns:
        tuple: first element corresponds to procedure metrics,
            second element is user creation time
    """
    from mongodb import query_user_metrics
    metrics = query_user_metrics(username)
    return metrics


def validate_process_img(r):
    """Validates request json for process_img

    Verifies that all the required info is provided in the dict. Also confirms
    if the procedure requested is allowed. upload image format is verified to
    see if it is supported. num_imgs is checked to see if it's a number.

    Args:
        r (dict): request json from client

    Returns:
        int: 1 if some information is missing or a non-supported procedure is
            requested
            2 if some of the data type isn't correct
            0 otherwise
    """
    try:
        username = r['username']
        num_img = r['num_img']
        imgs = r['imgs']
        procedure = r['procedure']
        img_format = r['img_format']
        filename = r['filename']
    except KeyError:
        return 1
    if not ((procedure in procedure_choices) and
            (img_format in img_format_choices)):
        return 1
    try:
        num_img = int(num_img)
    except ValueError:
        return 2
    return 0


def store_new_request(r, request_id, list_of_processed_imgs_encoded,
                      time_received):
    """Interfaces with the database to log new request

    Args:
        r (dict): original request json supplied with process_img request
        request_id (str): request id for this request
        list_of_processed_imgs_encoded (list): each term is a b64 processed
            image
        time_received (str): time when the request was received

    Returns:
        dict: copy of the data stored into the database
    """
    db_data = {
        'uploaded': r['imgs'],
        'processed': list_of_processed_imgs_encoded,
        'img_format': r['img_format'],
        'time_uploaded': time_received.strftime('%Y-%m-%d %H:%M:%S'),
        'time_to_process':
            (datetime.datetime.now() - time_received).total_seconds(),
        'img_size': get_img_sizes(list_of_processed_imgs_encoded, 'JPG'),
        'procedure': r['procedure'],
        'filename': r['filename']
    }
    from mongodb import save_a_new_request
    save_a_new_request(r['username'], request_id, db_data)
    return db_data


def get_img_sizes(list_of_processed_imgs_encoded, img_format):
    """Calculates the size of each image from a list

    Args:
        list_of_processed_imgs_encoded (list): list of encoded images
        img_format (str): format of the images

    Returns:
        list: each term is a tuple containing the width and height of each
        image
    """
    img_sizes = []
    for base64_string in list_of_processed_imgs_encoded:
        decoded_img = decode_b64(base64_string, img_format)
        new_tuple = (decoded_img.shape[0], decoded_img.shape[1])
        img_sizes.append(new_tuple)
    return img_sizes


def get_histograms(img_list):
    """creates a histogram for each image in the list

    Args:
        img_list (list): each entry is a decoded image in matrix form

    Returns:
        list: each entry in this list corresponds to a image from the img_list
            each entry is a dict with red, green, blue as keys
            each key corresponds to a tuple that consist of two lists, bins and
            hist
    """
    hist_list = []
    for img in img_list:
        histograms = {}
        for c, c_color in enumerate(('red', 'green', 'blue')):
            img_hist, bins = exposure.histogram(img[..., c])
            histograms[c_color] = (bins.tolist(), img_hist.tolist())
        hist_list.append(histograms)
    return hist_list


if __name__ == '__main__':
    app.run()  # host="0.0.0.0"
