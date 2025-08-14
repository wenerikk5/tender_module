# coding: utf-8
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from .exceptions import ETPRequestError

_logger = logging.getLogger(__name__)


class BaseAPI:
    base_url = None
    request_timeout_sec = 30
    access_token = None

    def __init__(self, access_token=None):
        self.access_token = access_token

    def _request(self, method, endpoint, params=None, headers=None, json=None):
        params = params or {}
        headers = headers or {}
        headers.setdefault('Content-Type', 'application/json')
        headers.setdefault('Authorization',
                           'OAuth {access_token}'.format(access_token=self.access_token))

        url = f"{self.base_url.rstrip('/')}/{endpoint}"

        with requests.Session() as session:
            number_of_retries = 3
            retry_strategy = Retry(total=number_of_retries,
                                   status_forcelist=[429, 500, 502, 503, 504,],
                                   # method_whitelist=['GET', 'POST'],
                                   backoff_factor=2)   # 1s, 2s, 4s
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            try:
                response = session.request(method, url, params=params, json=json,
                                           headers=headers, timeout=self.request_timeout_sec)
            except Exception as exc:
                _logger.error('Failed to request %s %s with headers=%s, params=%s json=%s due to %s',
                             method, url, headers, params, json, exc,
                             exc_info=True,
                             extra={'data': {'json': json, 'params': params}})
                raise ETPRequestError

        if not (200 <= response.status_code < 300):
            _logger.error('Failed to request %s %s with headers=%s, params=%s json=%s due to %s',
                         method, url, headers, params, json, response.content,
                         extra={'data': {'json': json, 'params': params}})
            raise ETPRequestError

        return self._data_from_response(response)

    @staticmethod
    def _data_from_response(response):
        try:
            return response.json()
        except Exception as exc:
            _logger.warning('Unable to parse json response due to %s', exc, exc_info=True,
                           extra={'data': {'content': response.content}})
            raise ETPRequestError
