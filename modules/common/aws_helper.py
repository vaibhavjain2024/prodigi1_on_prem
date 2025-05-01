import json
import logging
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

aws_access_key_id = os.environ.get("aws_access_key_id")
aws_secret_access_key = os.environ.get("aws_secret_access_key")
region_name = os.environ.get("region_name")


def get_aws_service_client(service):
    """

    :param service:
    :return:
    """
    session = boto3.session.Session()
    aws_client = session.client(
        service,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )
    return aws_client


class AWSSecretManager(object):
    """
        class for making AWS secret key manager operation update and fetching
    """

    def __init__(self, aws_client):
        """

        :param aws_client:
        """
        self.__client = aws_client

        # to store data
        self.__data = dict()

    def update_key(self, key, value):
        """

        :return:
        """
        response = self.__hit_aws(key, value)
        return response

    def __hit_aws(self, key, value=None):
        """
            one place to hit aws api
        :param key:
        :return: response details
        """
        response = None
        if value is None:
            # that mean get call
            try:
                response = self.__client.get_secret_value(SecretId=key)
            except Exception as e:
                logger.error("The fetch request was invalid due to:", str(e), key)
                raise e
            else:
                logger.info("%s key successfully fatched" % key)
        else:
            try:
                response = self.__client.update_secret(
                    SecretId=key,
                    SecretString=value
                )
            except Exception as e:
                logger.error("The update request was invalid due to:", str(e), key, value)
                raise e
            else:
                logger.info("%s key successfully updated" % key)

        return response

    def fetch_key(self, key, force=False):
        """

        :param key:
        :param force:
        :return:
        """
        if self.__data.get(key) is None or force is True:
            response = self.__hit_aws(key=key, value=None)
            key_detail = self.__get_key_detail(response=response)
            self.__data[key] = key_detail

        return self.__data[key]

    @staticmethod
    def __get_key_detail(response):
        """

        :param response:
        :return:
        """
        keys_parms = ['Name', 'VersionId', 'CreatedDate']
        key_detail = {k: response[k] for k in keys_parms}
        key_detail['SecretString'] = json.loads(response['SecretString'])
        return key_detail
    
    
class AwsSsmKey(object):
    """
        aws key that hold keys property
    """

    def __init__(self, key, client, auto_update=False):
        """

        :param key:
        :param client:
        """
        self.key = key
        self.Name = None
        self.__value = None  # this will be always dict
        self.created_time = None
        self.version_id = None
        self.auto_update = auto_update
        self.__ssm_manager = AWSSecretManager(aws_client=client)
        self.refresh()

    def __getitem__(self, item):
        """
            fetch value of specific key
        :param item:
        :return:
        """
        if not self.__value:
            self.refresh()
        return self.__value[item]

    def __setitem__(self, key, value):
        """
            update value dict
        :param key:
        :param value:
        :return:
        """

        if not self.__value:
            self.refresh()
        # todo restrict to add new keys and raise exception
        self.__value[key] = value

        if self.auto_update:
            self.__update()

    def __delitem__(self, key):
        """
            deletion of key is not allowed
        :param key:
        :return:
        """
        raise NotImplementedError()

    def refresh(self):
        """
            method for refresh values manually from aws server
        :return:
        """
        self.__refresh_data(force=True)

    def __refresh_data(self, force=False):
        """

        :return:
        """
        key_data = self.__ssm_manager.fetch_key(key=self.key, force=force)
        self.name = key_data['Name']
        self.__value = key_data['SecretString']
        self.created_time = key_data['CreatedDate']
        self.version_id = key_data['VersionId']

    def __update(self):
        """

        :return:
        """
        self.__ssm_manager.update_key(
            key=self.key,
            value=str(json.dumps(self.__value))
        )

    def update(self):
        """
            if auto update false than thruogh this method can update value on aws
        :return:
        """
        self.__update()
        

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
        
    data['message'] = msg

    _headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Origin, Content-Type, Authorization",
            "Access-Control-Allow-Methods": "POST, PUT, GET, OPTIONS,DELETE"
        }
    
    if headers and isinstance(headers, dict):
        _headers.update(headers)

    return {
        "statusCode": status_code,
        'headers': _headers,
        "body": json.dumps(data)
    }


def get_lambda_arn(lamdba_context, lambda_name):
    """  
        return aws arn
    """
    
    lambda_arn = lamdba_context.invoked_function_arn.split("function")[0] + lambda_name 
    return lambda_arn
