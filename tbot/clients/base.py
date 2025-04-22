from time import sleep
from typing import Any

import structlog
from requests import RequestException, Response, Session

from tbot.errors import RetryExceededError
from tbot.utils import get_random_user_agent

logger = structlog.get_logger()


DEFAULT_TIMEOUT = 20
SLEEP_TIME = 62
MAX_RETRIES = 8


class BaseClient:
    name: str

    def __init__(
        self,
        credentials: dict[str, Any] = None,
        sleep_time: int = SLEEP_TIME,
        max_retries: int = MAX_RETRIES,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self.retry_count = 0
        self.timeout = timeout
        self.sleep_time = sleep_time
        self.max_retries = max_retries
        self.credentials = credentials or {}

        self.session = Session()
        self.base_headers = self._get_base_headers()

    def _request(self, url: str, method: str, **kwargs: Any) -> Response:
        headers = kwargs.pop("headers", {})
        headers.update({**self.credentials, **self.base_headers})
        try:
            response = self.session.request(
                method,
                url,
                **kwargs,
                headers=headers,
                timeout=self.timeout,
            )
            logger.info(
                "%s response status=%s, content=%s.",
                self.name,
                response.status_code,
                response.text,
                request={"method": method, "uri": url, **kwargs},
            )

            if response.status_code == 429:
                return self.retry(
                    url=url,
                    method=method,
                    headers=headers,
                    **kwargs,
                )
        except RequestException as e:
            raise RequestException(f"Unsuccessful request to {self.name}: {e}") from e
        if response.status_code >= 400:
            raise RequestException(
                f"Unsuccessful request to {self.name}: [status={response.status_code}] {response.text}"
            )

        return response

    def retry(self, url: str, method: str, **kwargs: Any) -> Response:
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            sleep(self.sleep_time)
            result = self._request(url=url, method=method, **kwargs)
            self.retry_count = 0
            return result

        raise RetryExceededError("Too many requests!")

    @staticmethod
    def _get_base_headers() -> dict[str, str]:
        user_agent, chrome_version = get_random_user_agent()
        return {
            "User-Agent": user_agent,
            "sec-ch-ua": f'"Not.A/Brand";v="8", "Chromium";v="{chrome_version}", "Google Chrome";v="{chrome_version}"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
        }
