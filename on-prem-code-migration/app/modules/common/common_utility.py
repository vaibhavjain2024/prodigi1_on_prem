import json
import logging
import base64

from json.decoder import JSONDecodeError

import constants

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_response(status_code, msg, data: dict, headers=None):
    """

    :param status_code:
    :param msg:
    :param data:
    :param headers:
    :return:
    """
    if not isinstance(msg, str):
        msg = json.dumps(msg)

    data["message"] = msg

    _headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Origin, Content-Type, Authorization",
        "Access-Control-Allow-Methods": "POST, PUT, GET, OPTIONS, DELETE",
    }

    if headers and isinstance(headers, dict):
        _headers.update(headers)

    return {"statusCode": status_code, "headers": _headers, "body": json.dumps(data)}


def prepare_lambda_response(message, status_code):
    if (
        isinstance(message, dict)
        or isinstance(message, list)
        or isinstance(message, str)
    ):
        message = json.dumps(message)
    return {"statusCode": status_code, "body": message}


class MessageAttributes:
    """The getter and setters will always be called even if you do obj.property  , so always
    get and set the values directly"""

    @property
    def request_type(self):
        return self._request_type

    @request_type.setter
    def request_type(self, request_type):
        self._request_type = request_type

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, action):
        self._action = action

    def get_response_dict(self, consumer=False):
        res_dict = {
            "requestType": {"DataType": "String", "StringValue": self.request_type},
            "action": {"DataType": "String", "StringValue": self.action},
            "sender": {
                "DataType": "String",
                "StringValue": self.sender,
            },
            "author": {
                "DataType": "String",
                "StringValue": self.author,
            },
            "target_system": {
                "DataType": "String",
                "StringValue": str(self.target_system),
            },
        }

        return res_dict


class ConsumerMessageAttributes(MessageAttributes):
    def __init__(self, record):
        try:
            self.message_attributes = record["messageAttributes"]
            self.action = self.message_attributes["action"]["stringValue"]
            self.request_type = self.message_attributes["requestType"]["stringValue"]
            self.sender = self.message_attributes.get("sender", {}).get(
                "stringValue", constants.UNKNOWN
            )
            self.author = self.message_attributes.get("author", {}).get(
                "stringValue", constants.UNKNOWN
            )
            self.target_system = self.message_attributes.get("target_system", {}).get(
                "stringValue", "Null"
            )

        except KeyError:
            logger.error(
                "Mandatory key is missing in MessageAttributes, Please check the structure of MessageAttributes"
            )
            raise KeyError

    def prepare_message_response(self):
        message_attributes_dict = self.get_response_dict(consumer=True)
        return message_attributes_dict


def change_dict_key_exist(data, key_map_pair):
    if isinstance(data, list):
        for row in data:
            for old_key, new_key in key_map_pair:
                if old_key in row:
                    row[new_key] = row.pop(old_key)
    if isinstance(data, dict):
        for old_key, new_key in key_map_pair:
            if old_key in data:
                data[new_key] = data.pop(old_key)


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


def generate_batch(lst, batch_size):
    """Yields bacth of specified size"""

    if batch_size <= 0:
        return

    for i in range(0, len(lst), batch_size):
        yield lst[i : i + batch_size]
