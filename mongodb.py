from pymodm import connect, MongoModel, fields, EmbeddedMongoModel
from datetime import datetime


# connect to mongodb database
connect("mongodb+srv://bme547:bme547_@cluster0-htwfk.mongodb.net/547")


# database module
# database module
# Requests
class Requests(EmbeddedMongoModel):
    """

    """
    uploaded = fields.ListField(blank=True)  # list of strs
    processed = fields.ListField(blank=True)  # list of strs
    img_format = fields.CharField(blank=True)  # str
    time_uploaded = fields.CharField(blank=True)  # a str
    time_to_process = fields.CharField(blank=True)  # a str
    img_size = fields.ListField(blank=True)  # list of tuples. Mongodb does not have tuple
    procedure = fields.CharField(blank=True)  # ONE str. one procedure each time
    filename = fields.ListField(blank=True)  # list of filenames

# User
class User(MongoModel):  # this means a collection in db

    username = fields.CharField(blank=True)
    # metrics
    num_actions = fields.IntegerField(blank=True)
    last_image_uploaded = fields.CharField(blank=True)
    request_id = fields.ListField(blank=True)  # a list of str or int
    
    # embedded documents
    requests = fields.EmbeddedDocumentListField(Requests)
    


def query_user(username):
    return User.objects.raw({"username": username}).first()


def create_new_user(username):

    """
    create a new user
    username must be given

    Args:
        username(str): username

    Returns:

    """
    try:
        query_user(username)
        print('User "{}" already exists.'.format(username))
    except:
        User(
            username,
        ).save()

    pass


def query_field(username, field):
    """
    Args:
        username(string): username to query the User db
        field(string): attribute of the user

    Returns:
        (type depends): one field in for given user

    """
    return getattr(query_user(username), field)


def update_field(username, field, value):
    """not inclduing Images and Actions, value could be None"""
    user = query_user(username)

    old_value = getattr(user, field)
    if isinstance(old_value, list):
        old_value.append(value)
        setattr(user, field, old_value)
    else:
        setattr(user, field, value)
    user.save()
    pass


def query_user_metrics(username):
    user = query_user(username)
    l = ['num_actions', 'last_image_uploaded', 'request_id']
    metrics = []
    for field in l:
        metrics.append(getattr(user, field))
    return metrics


def save_a_new_request(username, request_id, r):
    """
    r(dict): everything needed for Requests Class
    """
    r_class = Requests(
                       uploaded = r['uploaded'],
                       processed = r['processed'],
                       img_format = r['img_format'],
                       time_uploaded = r['time_uploaded'],
                       time_to_process = r['time_to_process'],
                       img_size = r['img_size'],
                       procedure = r['procedure'],
                       filename = r['filename']
            )

    create_new_user(username)
    user = query_user(username)
    user.request_id.append(request_id)
    user.requests.append(r_class)
    user.save()
    pass


def query_by_request_id(username, request_id):
    user = query_user(username)
    index = user.request_id.index(request_id)
    return user.requests[index]
