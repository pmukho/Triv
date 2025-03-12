# Logging Features

To add logging to your component, add the following after your import statements in your main.py file

from utils.logging_config import logging, log_request_middleware

There are 5 logging levels that can be used when using FastAPI:

INFO
- API requests being received
- Successful operations/key functions
- Application startup
- e.g. logger.info(f"Starting request for question_id: {question_id}")

DEBUG
- Changes to variable contents and states
- SQL queries
- Flow control information/configuration details
- e.g. logger.debug(f"Raw API response: {response.text}")

ERROR
- Exceptions
- API or authentication failures
- Database connection errors
- e.g. logger.error(f"No question found with id: {question_id}")

WARNING
- Performance issues
- Resource usage approaching limit
- e.g. logger.warning(f"Response time longer than expected: {response_time}s")

CRITICAL
- Database corruption
- Out of memory
- Unrecoverable system states

In general, print statements should be replaced by INFO and DEBUG logging statements.




