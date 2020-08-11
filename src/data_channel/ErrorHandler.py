import json
import logging
import urllib3.exceptions as url_e
from time import sleep


class ErrorHandler():
    def __init__(self):
        super().__init__()

    def handle(self, error):
        timeout = 120
        logging.error('Attempting to handle an error %s' % str(error))
        if isinstance(error, (url_e.MaxRetryError, url_e.ConnectTimeoutError)):
            # Something probably went wrong on the server side.
            # Log this error and timeout the application for a few minutes
            logging.error('Action taken: Timeout for %s seconds' % timeout)
            sleep(timeout)

        elif isinstance(error, StatusCodeException):
            # Handling error codes as shown in the link below:
            # https://www.pathofexile.com/developer/docs/api-errors
            status_code = error.get_status_code()
            logging.error('Status code %s' % status_code)

            if status_code == 400:
                # A Bad Request comes along with an Error code
                # Action: Log and timeout if Error Codes are 4 or 7.
                # Otherwise, shutdown
                error_code = error.get_error_code()
                logging.error('Error code %s' % error_code)
                if error_code in (4, 7):
                    logging.error('Action taken: Timeout for %s seconds' %
                                  timeout)
                    sleep(timeout)
                else:
                    logging.error('Action taken: Raise Exception and Shutdown')
                    raise error

            elif status_code == 404:
                # Resource not found. The application is probably misconfigured
                # Action: Log and shutdown
                logging.error('Action taken: Raise Exception and shutdown')
                raise error

            elif status_code == 429:
                # Too many requests. The application violated x-rate-limits,
                # which means RequestRules.py failed to limit requests.
                # Action: Log and shutdown
                # TODO: Best course of action would be to timeout based on the
                # penalty of the broken rule
                logging.error('Action taken: Raise Exception and shutdown')
                raise error

            elif status_code == 500:
                # Internal Server Error: Something went wrong on the server.
                # Action: Log and timeout
                logging.error('Action taken: Timeout for %s seconds' % timeout)
                sleep(timeout)

            else:
                # Unknown status code
                # Action: Log and shutdown
                logging.error('Not implemented status code. Shutting down')
                raise error
        else:
            # Unkown exception
            # Action: Log and shutdown
            logging.error('Not implemented handling mechanism. Shutting down')
            raise error


class StatusCodeException(Exception):
    def __init__(self, response_object, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = response_object.status_code
        self.response_text = json.loads(response_object.text)

    def get_status_code(self):
        return self.status_code

    def get_error_code(self):
        error_code = None
        try:
            error_code = self.response_text['error']['code']
        except KeyError as e:
            logging.error('Could not retrieve Error Code from ' +
                          'StatusCode Exception')
        finally:
            return error_code
