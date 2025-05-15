import base64
import json

from json.decoder import JSONDecodeError

def base64_encode_data(data):
    if isinstance(data, str):
        input_data = data
    elif isinstance(data, (int, float, complex, set)):
        input_data = str(data)
    elif isinstance(data, (dict, list, tuple)):
        input_data = json.dumps(data)
    else:
        return None

    string_bytes = input_data.encode("ascii")
    base64_bytes = base64.b64encode(string_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string


def base64_decode_data(base64_string):
    base64_bytes = base64_string.encode("ascii")
    string_bytes = base64.b64decode(base64_bytes)
    string = string_bytes.decode("ascii")
    try:
        return json.loads(string)
    except JSONDecodeError as e:
        return string