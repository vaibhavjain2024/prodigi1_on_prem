import requests
from logger_common import get_logger
logger = get_logger()
import time

def get_oauth_token(oauth_token_url, client_id, client_secret):
    try:
        response = requests.post(
            oauth_token_url,
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret),
        )
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        logger.error(f"Error obtaining OAuth token: {e}", exc_info=True)
        raise

def post_data_to_api(api_url, access_token, payload, max_retries=3, retry_delay=10):
    """
        Function to post data to the API with retry mechanism.

        :param api_url: URL of the API to post data
        :param access_token: OAuth token to access the API
        :param payload: Data to be sent in the API request
        :param max_retries: Maximum number of retry attempts
        :param retry_delay: Delay between retries in seconds
        :return: Response from the API, or None if failed after retries
    """

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    for attempt in range(1, max_retries + 1):
        try:
            # Make the API call
            response = requests.post(api_url, headers=headers, json=payload)
            # Check if the request was successful
            if response.status_code in [200,201,202]:
                logger.info(f"Data posted successfully to API on attempt {attempt}.")
                return response.json()  # Return the response JSON if the request is successful
            else:
                logger.error(f"Failed to post data on attempt {attempt}. "
                             f"Status code: {response.status_code}, Response: {response.text}")
                response.raise_for_status()  # Raise exception for non-200 responses
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed on attempt {attempt}. Error: {str(e)}")

            if attempt == max_retries:
                logger.error("Max retries reached. Data posting failed.")
                raise e  # Raise the exception if max retries are reached

            logger.info(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)  # Wait for the specified time before retrying

    return None  # Return None if all attempts fail
