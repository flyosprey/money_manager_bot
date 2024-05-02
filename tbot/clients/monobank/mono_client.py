from typing import Any
from urllib.parse import urljoin

from requests import RequestException, Session

DEFAULT_TIMEOUT = 10


class MonobankClient:
    def __init__(
        self,
        base_url: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout
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
            # logger.info(
            #     "DeepLoyalty response status=%s, content=%s",
            #     response.status_code,
            #     response.text,
            #     request={"method": method, "uri": uri, **kwargs},
            # )
        except RequestException as e:
            raise MonoExceptionError(f"Unsuccessful request to Monobank: {e}") from e
        if response.status_code >= 400:
            raise MonoExceptionError(
                f"Unsuccessful request to Monobank: [status={response.status_code}] {response.text}"
            )
        try:
            return response.json()
        except RequestException as e:
            raise MonoExceptionError(f"Unsuccessful request to Monobank: {e}") from e

    def get_currency_rate(self, token: str) -> dict[str, Any]:
        return self._request(
            method="GET",
            uri="bank/currency",
            access_token=token,
        )

    def get_client_info(self, token: str) -> dict[str, Any]:
        return self._request(
            method="GET",
            uri="personal/client-info",
            access_token=token,
        )


class MonoExceptionError(Exception):
    pass
