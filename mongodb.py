from pymodm import connect, MongoModel, fields, EmbeddedMongoModel
from datetime import datetime


# connect to mongodb database
connect("mongodb+srv://bme547:bme547_@cluster0-htwfk.mongodb.net/547")


# database module
# actions
class Actions(EmbeddedMongoModel):
    actions = fields.ListField()
    processing_types = fields.ListField(blank=True)
    timestamps = fields.TimestampField(blank=True)
    processing_time = fields.IntegerField(blank=True)
    image_size = fields.IntegerField(blank=True)

# images
class Images(EmbeddedMongoModel):
    """

    """
    images_uploaded = fields.CharField()  
    images_processed = fields.CharField()
    images_format = fields.CharField(blank=True)
    images_procedures = fields.ListField(blank=True)
    


# User
class User(MongoModel):  # this means a collection in db

    username = fields.CharField(blank=True)
    # metrics
    num_actions = fields.IntegerField(blank=True)
    last_image_uploaded = fields.CharField(blank=True)
    request_id = fields.CharField(blank=True)
    # embedded documents
    images = fields.EmbeddedDocumentListField(Images)
    actions = fields.EmbeddedDocumentListField(Actions)


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


def upload_images(username, raw_img, pro_img):
    user = query_user(username)
    user.last_image_uploaded = raw_img  # save as the last image
    user.images.append(Images(raw_img,pro_img))
    user.save()
    pass
