import json
import boto3
import time

from botocore.exceptions import ClientError

from logger_common import get_logger
from datetime import datetime

logger = get_logger()
AWS_SESSION = boto3.Session()


def create_sqs_client():
    return AWS_SESSION.client("sqs")


def create_lambda_client():
    return AWS_SESSION.client("lambda")


def create_s3_generic_client():
    return AWS_SESSION.client("s3")


def create_s3_generic_resource():
    return AWS_SESSION.resource("s3")


def create_dynamodb_generic_client():
    return AWS_SESSION.client("dynamodb")


def create_dynamodb_resource():
    return AWS_SESSION.resource("dynamodb")


def get_sqs_queue_url(queue_name):
    sqs_client = create_sqs_client()
    response = sqs_client.get_queue_url(QueueName=queue_name)
    return response["QueueUrl"]


def s3_upload(s3_client, data, bucket, key, file_path=None):
    try:
        if file_path:
            with open(file_path, "rb") as data:
                s3_client.upload_fileobj(data, bucket, key)
        else:
            s3_client.put_object(Body=data, Bucket=bucket, Key=key)

    except Exception as exception:
        logger.error(
            f"Error occurred while uploading data to S3 bucket {bucket}", exc_info=True
        )
        raise Exception(exception)


def upload_files_to_s3(data, bucket, key, file_path=None, is_dumped=False):
    s3_obj = create_s3_generic_client()

    if is_dumped:
        s3_upload(s3_obj, data, bucket, key, file_path=file_path)
    else:
        s3_upload(s3_obj, json.dumps(data), bucket, key, file_path=file_path)


def read_file_from_s3_bucket(bucket_name, object_key):
    s3_obj = create_s3_generic_client()
    try:
        object_file = s3_obj.get_object(Bucket=bucket_name, Key=object_key)
        body = object_file["Body"].read()
        return body
    except Exception as exception:
        logger.error(
            f"Error occurred while reading file from s3 bucket {bucket_name}, Key: {object_key}",
            exc_info=True,
        )
        raise Exception(exception)


def create_download_presigned_url(bucket_name, object_name, expiration=30):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = create_s3_generic_client()
    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": bucket_name,
                "Key": object_name,
                "ResponseContentType": "binary/octet-stream",
            },
            ExpiresIn=expiration,
        )
    except ClientError as error:
        logger.error(
            f"Error occurred while creating pre-signed url for following: Bucket: {bucket_name}, Path: {object_name}",
            exc_info=True,
        )
        return None

    # The response contains the presigned URL
    return response


def add_item_in_dynamo_table(table, item):
    """
    table: DynamoDB table name
    item: item to be added in DynamoDB table
        i.e. Item is key value pair. e.g. {col_name1: "value1", col_name2: "value2"}
    """

    dynamodb_obj = create_dynamodb_resource()
    dynamodb_table = dynamodb_obj.Table(table)

    try:
        response = dynamodb_table.put_item(Item=item)
        return response
    except ClientError as err:
        logger.error(
            f"Error occurred while adding element in table {table} with item :{item}. Error as follows: {err.response['Error']['Code']}, {err.response['Error']['Message']}",
            exc_info=True,
        )
        raise


def add_items_in_dynamo_table(table, items):
    """
    table: DynamoDB table name
    item: item to be added in DynamoDB table
        i.e. Item is key value pair. e.g. {col_name1: "value1", col_name2: "value2"}
    """

    dynamodb_obj = create_dynamodb_resource()
    dynamodb_table = dynamodb_obj.Table(table)

    try:
        with dynamodb_table.batch_writer() as batch:
            for item in items:
                time.sleep(1)
                batch.put_item(Item=item)
    except ClientError as err:
        logger.error(
            f"Error occurred while adding element in table {table} with items :{items}. Error as follows: {err.response['Error']['Code']}, {err.response['Error']['Message']}",
            exc_info=True,
        )
        raise


def delete_item_in_dynamo_table(table, key):
    """
    table: DynamoDB table name
    key: Its a key value vair of attributes to get an item from table. key = {'shop_id': shop_id, 'version': 1.5}
    """

    dynamodb_obj = create_dynamodb_resource()
    dynamodb_table = dynamodb_obj.Table(table)

    try:
        dynamodb_table.delete_item(Key=key)
    except ClientError as err:
        logger.error(
            f"Error occurred while deleting item from table {table} with key :{key}. Error as follows: {err.response['Error']['Code']}, {err.response['Error']['Message']}",
            exc_info=True,
        )
        raise


def update_item_in_dynamo_table(
    table, key, update_expr, expr_attribute, condition_expr=None
):
    """
    table: DynamoDB table name
    key: key is your primary keys in key value pair (partition_key: "value", short_key:"value")
    update_expr: Its is update expression. e.g. "set info.rating=:r, info.plot=:p"
    condition_expr: conditional expression, e.g. "size(info.actors) > :num"
    expr_attribute: value of variable in update_expr. e.g. {':r': Decimal(str(rating)), ':p': plot}
    """

    dynamodb_obj = create_dynamodb_resource()
    dynamodb_table = dynamodb_obj.Table(table)

    try:
        if condition_expr:
            response = dynamodb_table.update_item(
                Key=key,
                UpdateExpression=update_expr,
                ConditionExpression=condition_expr,
                ExpressionAttributeValues=expr_attribute,
                ReturnValues="UPDATED_NEW",
            )
        else:
            response = dynamodb_table.update_item(
                Key=key,
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_attribute,
                ReturnValues="UPDATED_NEW",
            )
        return response
    except ClientError as err:
        logger.error(
            f"Error occurred while updating element in table {table} with Key={key}, UpdateExpression={update_expr}, ConditionExpression={condition_expr} ExpressionAttributeValues={expr_attribute}. Error as follows: {err.response['Error']['Code']}, {err.response['Error']['Message']}",
            exc_info=True,
        )
        raise


def publish_sqs_message(sqs_url, message_body, message_attributes, delay=10):
    try:
        sqs = create_sqs_client()
        response = sqs.send_message(
            QueueUrl=sqs_url,
            DelaySeconds=delay,
            MessageBody=json.dumps(message_body),
            MessageAttributes=message_attributes,
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            msg = f"Message is delivery failed to SQS {sqs_url} - Response : {response}"
            logger.info(msg)
        return response
    except Exception as error:
        err_msg = f"Exception occurred while publishing message to {sqs_url}"
        logger.error(err_msg, exc_info=True)
        raise error


class SQSMessage:
    def __init__(self, record) -> None:
        from common_utility import ConsumerMessageAttributes

        self.record = record
        self.data = None
        self.record_body = json.loads(record.get("body"))
        self.message_id = record["messageId"]

        self.approximate_receive_count = self.get_receive_count()
        self.sqs_name = self.get_sqs_name_from_record()
        self.get_data()
        self.message_attributes = ConsumerMessageAttributes(record)

    def get_data(self):
        if not self.data:
            self.data = self.record_body

    def get_receive_count(self):
        return int(self.record.get("attributes", {}).get("ApproximateReceiveCount", 0))

    def get_sqs_name_from_record(self):
        return self.record.get("eventSourceARN", "").split(":")[-1]

    def get_receipt_handle(self):
        receipt_handle = self.record["receiptHandle"]
        return receipt_handle

    def delete_sqs_message(self):
        sqs_url = get_sqs_queue_url(self.sqs_name)
        try:
            receipt_handle = self.get_receipt_handle()
            sqs = create_sqs_client()
            sqs.delete_message(QueueUrl=sqs_url, ReceiptHandle=receipt_handle)

        except Exception as error:
            logger.error(f"Message is not deleted : {error}")


def check_file_exists_on_s3(bucket, key):
    s3_obj = create_s3_generic_client()
    try:
        s3_obj.head_object(Bucket=bucket, Key=key)
    except ClientError as e:
        return False
    else:
        return True


def delete_file_on_s3(bucket, key):
    s3 = create_s3_generic_resource()
    try:
        return s3.Object(bucket, key).delete()
    except Exception as exception:
        logger.error(
            f"Error occurred while deleting file from s3 bucket {bucket}, Key: {key}",
            exc_info=True,
        )
        raise Exception(exception)


def search_s3_by_wildcard(bucket, path):
    try:
        get_last_modified = lambda obj: int(obj["LastModified"].strftime("%s"))
        s3 = boto3.client("s3")
        objs = s3.list_objects(Bucket=bucket, Prefix=path)["Contents"]
        return [
            obj["Key"] for obj in sorted(objs, key=get_last_modified, reverse=True)
        ][0]
    except Exception as exception:
        return False


def get_paginated_results(bucket, key=None):
    try:
        s3 = create_s3_generic_client()
        paginator = s3.get_paginator("list_objects")
        operation_parameters = {"Bucket": bucket}
        if key:
            operation_parameters["Prefix"] = key
        return paginator.paginate(**operation_parameters).search(
            "Contents[?Size > `0`][]"
        )
    except Exception as exception:
        logger.error(
            f"Error occurred while getting paginated data from s3 bucket {bucket}, Key: {key}",
            exc_info=True,
        )
        return []


def copy_files_between_s3_buckets(source_obj, dest_bucket, dest_key):
    try:
        s3_resource = create_s3_generic_resource()
        s3_resource.meta.client.copy(source_obj, dest_bucket, dest_key)
    except Exception as exception:
        logger.error(
            f"Error occurred while copying files from s3 bucket {source_obj} to bucket: {dest_bucket} path: {dest_key}",
            exc_info=True,
        )
        raise Exception(exception)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def invoke_lambda_function(function_name, payload):
    lambda_client = create_lambda_client()
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload, cls=DateTimeEncoder)
        )

        # Read the payload and decode
        payload_str = response['Payload'].read().decode('utf-8')

        # Try parsing as JSON directly
        try:
            response_payload = json.loads(payload_str)

            # If response has a 'body' that's a string, try to parse it
            if isinstance(response_payload.get('body'), str):
                try:
                    response_payload['body'] = json.loads(response_payload['body'])
                except (json.JSONDecodeError, TypeError):
                    # If parsing fails, leave as is
                    pass

            return response_payload

        except json.JSONDecodeError:
            # Fallback parsing if direct JSON fails
            logger.warning(f"Failed to parse JSON directly. Payload: {payload_str}")
            return payload_str

    except Exception as exception:
        logger.error(
            f"Error occurred while invoking lambda function {function_name} Payload: {payload}",
            exc_info=True,
        )
        raise Exception(exception)
