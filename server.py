from flask import Flask, jsonify, request
error_messages = {1: 'Please put post request json in correct format',
                2: 'Incorrect data types in request',
                3: 'Username or request id does not exist'}
processing_choices = ['histogram_eq', 'contrast_str', 'log_compress', 'reverse_vid']
img_format_choices = ['JPEG', 'PNG', 'TIFF']
@app.route("/api/process_img", methods=["POST"])
def process_img_handler():
    r = request.get_json()
    flag = validate_process_img(r)
    # decode image
    # process individual image
    # convert to desired format
    # calculate histogram for that image
    # Store data to db
    # assemble return data
    pass

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
        return 1
    if ~((processing in processing_choices) and (img_format in img_format_choices)):
        
    try:
        num_img = int(num_img)
    except ValueError:
        return 2
    return flag
