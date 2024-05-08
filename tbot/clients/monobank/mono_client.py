import json
from time import sleep
from typing import Any
from urllib.parse import urljoin

import structlog
from requests import RequestException, Session

from tbot.dto.monobank.payload import ClientInfoPayload, Transaction
from tbot.utils import get_unix_time

logger = structlog.get_logger()


DEFAULT_TIMEOUT = 20
SLEEP_TIME = 62
MAX_RETRIES = 3


class MonobankClient:
    def __init__(
        self,
        base_url: str,
        sleep_time: int = SLEEP_TIME,
        max_retries: int = MAX_RETRIES,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self.retry_count = 0
        self.base_url = base_url
        self.timeout = timeout
        self.sleep_time = sleep_time
        self.max_retries = max_retries
        self.session = Session()

    def _request(self, uri: str, method: str, access_token: str, **kwargs: Any):
        headers = kwargs.pop("headers", {})
        headers["X-Token"] = access_token
        try:
            response = self.session.request(
                method,
                urljoin(self.base_url, uri),
                **kwargs,
                headers=headers,
                timeout=self.timeout,
            )
            if response.status_code == 429:
                return self.retry(
                    uri=uri,
                    method=method,
                    headers=headers,
                    access_token=access_token,
                    **kwargs,
                )
            logger.info(
                "Monobank response status=%s, content=%s.", response.status_code, response.text,
                request={"method": method, "uri": uri, **kwargs},
            )
        except RequestException as e:
            raise MonoExceptionError(f"Unsuccessful request to Monobank: {e}") from e
        if response.status_code >= 400:
            raise MonoExceptionError(
                f"Unsuccessful request to Monobank: [status={response.status_code}] {response.text}"
            )
        try:
            return json.loads(response.text)
        except RequestException as e:
            raise MonoExceptionError(f"Unsuccessful request to Monobank: {e}") from e

    def retry(self, uri: str, method: str, access_token: str, **kwargs: Any) -> dict:
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            sleep(self.sleep_time)
            result = self._request(
                uri=uri, method=method, access_token=access_token, **kwargs
            )
            self.retry_count = 0
            return result

        raise MonoExceptionError("Too many requests!")

    def get_currency_rate(self, token: str) -> dict[str, Any]:
        return self._request(
            method="GET",
            uri="/bank/currency",
            access_token=token,
        )

    def get_client_info(self, token: str) -> ClientInfoPayload:
        result = self._request(
            method="GET",
            uri="/personal/client-info",
            access_token=token,
        )
        return ClientInfoPayload.model_validate(result)

    def get_transactions(
        self, token: str, account_id: str | None, period: int
    ) -> dict[str, Any]:
        from_date = get_unix_time(seconds=period)
        to_date = get_unix_time()
        return self._request(
            method="GET",
            uri=f"/personal/statement/{account_id}/{from_date}/{to_date}",
            access_token=token,
        )

    def get_all_accounts_transactions(
        self, token: str, period: int
    ) -> list[Transaction]:
        client_info = self.get_client_info(token=token)
        transactions = []
        for account in client_info.accounts:
            result = self.get_transactions(
                token=token,
                account_id=account.id,
                period=period,
            )
            for transaction in result:
                transactions.append(Transaction.model_validate(transaction))

        return transactions


class MonoExceptionError(Exception):
    pass
