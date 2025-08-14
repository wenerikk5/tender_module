# coding: utf-8
import logging
from datetime import datetime

from .base import BaseAPI
from . import exceptions

_logger = logging.getLogger(__name__)


class ETPApi(BaseAPI):
    base_url = 'http://mock_server:8080'

    def get_procedures(self, published_from: datetime, inn: str) -> dict:
        """
        Get a list of procedures.
        :param published_from: Publish_date of the procedure (no earlier)
        :param inn: inn of the customer
        """
        try:
            response_data = self._request(
                'get',
                f"procedures?inn={inn}&from_date={published_from}",
            )
        except Exception as exc:
            _logger.error('get_procedures request with inn %s and '
                          'published_from %s failed due to %s',
                          inn, published_from, exc, exc_info=True)
            raise exceptions.ETPRequestError

        return response_data

    def get_procedure_details(self, procedure_ids: list) -> dict:
        """
        Get detailed data with a list of lots and participants.
        :param procedure_ids: List of procedure external ids.
        """
        try:
            response_data = self._request(
                'get',
                f"procedures/details?procedure_ids={procedure_ids}",
            )
        except Exception as exc:
            _logger.error('get_lots request with procedure_ids %s '
                          'failed due to %s',
                          procedure_ids, exc, exc_info=True)
            raise exceptions.ETPRequestError

        return response_data