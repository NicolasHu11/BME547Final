import pytest
from mongodb import Requests, User
from mongodb import query_user, save_a_new_request
from pymodm import connect, MongoModel, fields, EmbeddedMongoModel

# connect to mongodb database
connect("mongodb+srv://bme547:bme547_@cluster0-htwfk.mongodb.net/547")
r_sample = {
        'uploaded': ['afsdfsd'],
        'processed': ['processed iamges'],
        'img_format': 'JPG',
        'time_uploaded': 'time now',
        'time_to_process': '0.001',
        'img_size': (100, 255),
        'procedure': 'histogram_eq',
        'filename': 'img0.jpg',
    }
save_a_new_request('newuser111', '1', r=r_sample)
save_a_new_request('newuser111', '2', r=r_sample)
save_a_new_request('newuser111', '3', r=r_sample)
user001 = query_user("newuser111")  # test user


@pytest.mark.parametrize('username, expected', [
    ('newuser111', user001),
    ('abc', 0),

])
def test_query_user(username, expected):
    from mongodb import query_user

    try:
        user = query_user(username)
        answer = user
    except:
            answer = 0  # user does not exist, return 0

    assert answer == expected


@pytest.mark.parametrize('username, expected', [
    ('newuser111', user001.username),
    ('newuser001', 'newuser001'),
])
def test_create_new_user(username, expected):
    from mongodb import create_new_user
    create_new_user(username)
    answer = query_user(username).username
    assert answer == expected


@pytest.mark.parametrize('field, expected', [
    ('username', user001.username),
    ('request_id', user001.request_id),
])
def test_query_field(field, expected):
    from mongodb import query_field
    answer = query_field('newuser111', field)
    assert answer == expected


def test_save_a_new_request():
    from mongodb import save_a_new_request
    save_a_new_request('newuser002', '1', r=r_sample)
    answer = query_user('newuser002').requests[0]
    assert answer == user001.requests[0]


@pytest.mark.parametrize('request_id, expected', [
    ('1', user001.requests[0]),
    ('2', user001.requests[1]),
    ('9', 1),
])
def test_query_by_request_id(request_id, expected):
    from mongodb import query_by_request_id
    answer = query_by_request_id('newuser111', request_id)
    assert answer == expected


@pytest.mark.parametrize('username, expected', [
    ('newuser111', 1),
    ('2', 0),
    ('9', 0),
])
def test_check_user(username, expected):
    from mongodb import check_user
    answer = check_user(username)
    assert answer == expected


def test_query_user_metrics():
    from mongodb import query_user_metrics
    answer = query_user_metrics('newuser111')
    expected = (user001.num_actions, user001.user_creation_time)
    assert answer == expected


def test_query_request_metadata():
    from mongodb import query_request_metadata
    answer = query_request_metadata('newuser111', '1')
    request = user001.requests[0]
    expected = [
            getattr(request, 'time_uploaded'),
            getattr(request, 'time_to_process'),
            getattr(request, 'img_size')
            ]
    assert answer == expected
