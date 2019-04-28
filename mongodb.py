from pymodm import connect, MongoModel, fields, EmbeddedMongoModel


# connect to mongodb database
connect("mongodb+srv://bme547:bme547_@cluster0-htwfk.mongodb.net/547")


# database module
# Requests
class Requests(EmbeddedMongoModel):
    """This class stores one request

    Args:
        uploaded(list): stores the uploaded images as base64 strings
        processed(list): stores the processed images as base64 strings
        img_format(str): stores the image format,in one request, there is one
                         format
        time_uploaded(list): stores the timestamp the images are uploaded
        time_to_process(list): stores the time spent on each image processing
                               procedure
        img_size(list): stores the images' sizes
        procedure(str): stores the procedure in this request
        filename(list): stores the names of the images

    Returns:

    """
    uploaded = fields.ListField(blank=True)  # list of strs
    processed = fields.ListField(blank=True)  # list of strs
    img_format = fields.CharField(blank=True)  # str
    # metadata for each request
    time_uploaded = fields.ListField(blank=True)  # a str
    time_to_process = fields.ListField(blank=True)  # a list
    # list of tuples. Mongodb does not have tuple
    img_size = fields.ListField(blank=True)
    # ONE str. one kind of procedure each time
    procedure = fields.CharField(blank=True)
    filename = fields.ListField(blank=True)  # list of filenames


# User
class User(MongoModel):  # this means a collection in db
    """This class stores all the user information

    Args:
        username(str): the username
        user_creation_time(str): the time when the user is created
        num_actions(dict): statictics on the number of each procedures
        last_image_uploaded(str): the latest image uploaded
        request_id(list): list of request ids
        requests(Rquests): embedded class

    """
    username = fields.CharField(blank=True)
    # metrics for user
    user_creation_time = fields.CharField(blank=True)
    num_actions = fields.DictField(blank=True)  # a dict for each procedure

    last_image_uploaded = fields.CharField(blank=True)
    request_id = fields.ListField(blank=True)  # a list of str or int

    # embedded documents
    requests = fields.EmbeddedDocumentListField(Requests)


def query_user(username):
    """this will query username

    Args:
        username(str): the username

    Returns:
        User: User class if username exists
    """

    return User.objects.raw({"username": username}).first()


def create_new_user(username):
    from datetime import datetime

    """create a new user, username must be given

    Args:
        username(str): username

    Returns:

    """
    procedure_choices = ['histogram_eq', 'contrast_str', 'log_compress',
                         'reverse_vid']

    try:
        query_user(username)
        print('User "{}" already exists.'.format(username))
    except:
        User(
            username,
            user_creation_time=str(datetime.now()),  # new add
            num_actions={
                'histogram_eq': 0,
                'contrast_str': 0,
                'log_compress': 0,
                'reverse_vid': 0,
                           }
        ).save()

    pass


def query_field(username, field):
    """this will query one field of user
    Args:
        username(str): username to query the User db
        field(str): attribute of the user

    Returns:
        type depends: one field for given user

    """
    try:
        user = query_user(username)
        return getattr(user, field)
    except:
        return 0  # user does not exist, return 0


def save_a_new_request(username, request_id, r):
    """save a new request
    Args:
        username(str): the username
        request_id(str): the request id
        r(dict): all info for Requests Class

    """
    r_class = Requests(
                       uploaded=r['uploaded'],
                       processed=r['processed'],
                       img_format=r['img_format'],
                       time_uploaded=r['time_uploaded'],
                       time_to_process=r['time_to_process'],
                       img_size=r['img_size'],
                       procedure=r['procedure'],
                       filename=r['filename']
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
    """query one request by request id
    Args:
        username(str): the username
        request_id(str): the request id
    Returns:
        Request: one request coresponding to request id
    """
    try:
        user = query_user(username)
    except:
        return 0  # user does not exist, return 0

    try:
        index = user.request_id.index(request_id)
        return user.requests[index]
    except ValueError:
        return 1  # request_id does not exist.


def check_user(username):
    """check id username exists
    Args:
        username(str): the username
    Returns:
        Interger: 1 if exists, 0 not

    """
    try:
        user = query_user(username)
        return 1  # username exists
    except:
        return 0  # user does not exist, return 0


def query_user_metrics(username):
    """query user metrics
    Args:
        username(str): the username
    Returns:
        dict: num_actions
        str: user creation time

    """
    try:
        user = query_user(username)
    except:
        return 0  # user does not exist, return 0
    return user.num_actions, user.user_creation_time


def query_request_metadata(username, request_id):
    """query request metadata
    Args:
        username(str): the username
        request_id(str): the request id
    Returns:
        list: [time_uploaded, time_to_process, img_size]

    """
    request = query_by_request_id(username, request_id)

    return [
            getattr(request, 'time_uploaded'),
            getattr(request, 'time_to_process'),
            getattr(request, 'img_size')
            ]
