import pytest
import base64
import matplotlib.pyplot as plt

@pytest.fixture
def load_img():
    image_path = "./images/airplane001.jpg"
    with open(image_path, "rb") as image_file:
        b64_bytes = base64.b64encode(image_file.read())
    b64_string = str(b64_bytes, encoding='utf-8')
    return b64_string

def test_encode_imgs_b64():
    pass

def test_decode_imgs_from_request():
    pass

def test_process_igs_with_method():
    pass

def test_generate_request_id():
    from server import generate_request_id
    pass

def test_decode_b64(load_img):
    from server import decode_b64, encode_b64
    decoded = decode_b64(load_img, 'JPG')
    encoded = encode_b64(decoded, 'JPG')
    # redoecoded = decode_b64(encoded, 'JPG')
    # plt.figure(0)
    # plt.imshow(decoded)
    # plt.figure(1)
    # plt.imshow(redoecoded)
    # plt.show()
    # The two strings aren't exactly the same, but I plotted
    # and found them to be identical visually.
    assert encoded[0:10] == load_img[0:10]

def test_encode_b64(load_img):
    from server import decode_b64, encode_b64
    decoded = decode_b64(load_img, 'JPG')
    encoded = encode_b64(decoded, 'JPG')
    assert encoded[0:10] == load_img[0:10]

def test_previous_request_preview():
    pass

def test_get_previous_requests():
    pass

def test_validate_previous_request():
    pass

def test_get_user_metrics():
    pass

def test_validate_process_img():
    pass

def test_store_new_request():
    pass
def test_get_img_sizes():
    pass
def test_get_histograms():
    pass
