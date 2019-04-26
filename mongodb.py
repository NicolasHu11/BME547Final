from pymodm import connect, MongoModel, fields, EmbeddedMongoModel


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
    # metadata for each request
    time_uploaded = fields.ListField(blank=True)  # a str
    time_to_process = fields.ListField(blank=True)  # a str
    img_size = fields.ListField(blank=True)  # list of tuples. Mongodb does not have tuple

    procedure = fields.CharField(blank=True)  # ONE str. one kind of procedure each time
    filename = fields.ListField(blank=True)  # list of filenames

# User
class User(MongoModel):  # this means a collection in db

    username = fields.CharField(blank=True)
    # metrics for user
    user_creation_time = fields.CharField(blank=True)
    num_actions = fields.DictField(blank=True)  # a dict for each kind of procedure

    last_image_uploaded = fields.CharField(blank=True)
    request_id = fields.ListField(blank=True)  # a list of str or int
    
    # embedded documents
    requests = fields.EmbeddedDocumentListField(Requests)
    


def query_user(username):
    return User.objects.raw({"username": username}).first()


def create_new_user(username):
    from datetime import datetime

    """
    create a new user
    username must be given

    Args:
        username(str): username

    Returns:

    """
    procedure_choices = ['histogram_eq', 'contrast_str', 'log_compress', 'reverse_vid']

    try:
        query_user(username)
        print('User "{}" already exists.'.format(username))
    except:
        User(
            username,
            user_creation_time = str(datetime.now()), # new add
            num_actions = {
                'histogram_eq':0,
                'contrast_str':0,
                'log_compress':0,
                'reverse_vid':0,
                           }
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
    try:
        user = query_user(username)
        return getattr(user, field)
    except:
        return 0  # user does not exist, return 0


def update_field(username, field, value):
    """not inclduing Images and Actions, value could be None"""
    try:
        user = query_user(username)
    except:
        return 0  # user does not exist, return 0

    old_value = getattr(user, field)
    if isinstance(old_value, list):
        old_value.append(value)
        setattr(user, field, old_value)
    else:
        setattr(user, field, value)
    user.save()
    pass


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
    # update num_actions by counting the length of the list
    user.num_actions[r_class.procedure] += len(r_class.uploaded)
    user.save()
    pass


def query_by_request_id(username, request_id):
    try:
        user = query_user(username)
    except:
        return 0  # user does not exist, return 0

    try:
        index = user.request_id.index(request_id)
        return user.requests[index]
    except ValueError:
        return 1 # request_id does not exist.


def check_user(username):
    try:
        user = query_user(username)
        return 1 # username exists
    except:
        return 0  # user does not exist, return 0


def query_user_metrics(username):
    
    try:
        user = query_user(username)
    except:
        return 0  # user does not exist, return 0

    return [getattr(user, num_actions), getattr(user, user_creation_time)]


def query_request_metadata(username, request_id):
    request = query_by_request_id(username, request_id)

    return [
            getattr(request, time_uploaded),
            getattr(request, time_processed),
            getattr(request, img_size)
            ]