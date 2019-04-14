from flask import Flask, jsonify, request

@app.route("/api/process_img", methods=["POST"])
def process_img_handler():
    r = request.get_json()
    validate_process_img(r)
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
    pass
