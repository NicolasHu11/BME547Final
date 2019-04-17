from pymodm import connect, MongoModel, fields, EmbeddedMongoModel
from datetime import datetime


# connect to mongodb database
connect("mongodb+srv://bme547:bme547_@cluster0-htwfk.mongodb.net/547")


# database module
# actions
class Actions(EmbeddedMongoModel):
    actions = fields.ListField(blank=True)


# images
class Images(EmbeddedMongoModel):
    """

    """
    images_uploaded = fields.ListField(blank=True)  # each one is a char
    images_processed = fields.ListField(blank=True)
    images_format = fields.ListField(blank=True)
    images_procedures = fields.ListField(blank=True)
    timestamps = fields.TimestampField(blank=True)


# User
class User(MongoModel):  # this means a collection in db

    username = fields.CharField(blank=True)

    num_actions = fields.IntegerField(blank=True)
    last_image_uploaded = fields.CharField(blank=True)
    request_id = fields.CharField(blank=True)
    # embedded documents
    images = fields.EmbeddedDocumentField(Images)
    actions = fields.EmbeddedDocumentField(Actions)


def create_new_user(d):

    """
    create a new user
    username must be given

    Args:
        d(dict): input dictionary, must contains 'username'

    Returns:

    """
    User(
        d['username'],
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
    user = User.objects.raw({"username": username}).first()
    return getattr(user, field)


def update_field(username, field, value):
    user = Imageset.objects.raw({"_id": key}).first()
    old_value = getattr(user, field)
    if isinstance(old_value, list):
        old_value.append(value)
        setattr(user, field, old_value)
    else:
        setattr(user, field, value)
    user.save()
    pass


def delete_field(username, field):
    user = User.objects.raw({"username": username}).first()
    setattr(user, field, None)
    user.save()
    pass


def query_user_metrics(username):
    l = ['num_actions', 'last_image_uploaded', 'request_id']
    user = User.objects.raw({"username": username}).first()
    metrics = []
    for field in l:
        metrics.append(getattr(user, field))
    return metrics
