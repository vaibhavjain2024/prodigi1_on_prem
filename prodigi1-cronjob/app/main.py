from cron_job import call_sync_data
from utils.cloudwatch_logs import log_to_cloudwatch
from utils.logger_utility import logger
from datetime import datetime
import time
import asyncio
import uuid
import os
from config.app_config import (
    USER_API_URL
)


# This will run to fetch user data from cloud (SYNC)
async def users_sync_job():
    cron_job_id = f"user_sync_{uuid.uuid4()}"
    current_time = datetime.now()
    await call_sync_data(USER_API_URL, cron_job_id, current_time, method_type="POST")
    log_to_cloudwatch("INFO", f"Task 2 user sync executed at {datetime.now()}")


async def run_task_with_interval(task_name: str, interval_seconds: int = None):
    """
    Run a task continuously with the specified interval.
    
    Args:
        task_name (str): Name of the task to run
        interval_seconds (int, optional): Interval between runs in seconds
    """
    while True:
        try:
            if task_name == "user-sync":
                await users_sync_job()
            else:
                message = "No valid task specified!"
                logger.info(message)
                log_to_cloudwatch("INFO", message)
                break

            if interval_seconds:
                logger.info(f"Waiting {interval_seconds} seconds before next run...")
                await asyncio.sleep(interval_seconds)
            else:
                break  # Exit if no interval specified

        except Exception as e:
            logger.error(f"Error in task {task_name}: {str(e)}")
            if interval_seconds:
                await asyncio.sleep(interval_seconds)
            else:
                raise

if __name__ == "__main__":
    task_name = os.getenv("TASK_NAME")
    interval_seconds = int(os.getenv("INTERVAL_SECONDS", "0"))

    if not task_name:
        message = "No task specified!"
        logger.info(message)
        log_to_cloudwatch("INFO", message)
    else:
        asyncio.run(run_task_with_interval(task_name, interval_seconds))