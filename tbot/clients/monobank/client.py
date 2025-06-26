import json
from typing import Any
from urllib.parse import urljoin

from tbot.clients.base import BaseClient
from tbot.dto.monobank.payload import ClientInfoPayload, Transaction
from tbot.utils import get_unix_time


class MonobankClient(BaseClient):
    name = "monobank"
    api_url = "https://api.monobank.ua"

    def set_webhook(self, webhook_url: str) -> dict[str, Any]:
        response = self._request(
            method="POST",
            url=urljoin(self.api_url, "/personal/webhook"),
            data=json.dumps({"webHookUrl": webhook_url}),
        )

        return json.loads(response.text)

    def get_currencies_rate(self) -> dict[str, Any]:
        response = self._request(
            method="GET",
            url=urljoin(self.api_url, "/bank/currency"),
        )

        return json.loads(response.text)

    def get_client_info(self) -> ClientInfoPayload:
        response = self._request(
            method="GET",
            url=urljoin(self.api_url, "/personal/client-info"),
        )
        return ClientInfoPayload.model_validate(json.loads(response.text))

    def get_transactions(self, account_id: str | None, period: int) -> dict[str, Any]:
        from_date = get_unix_time(seconds=period)
        to_date = get_unix_time()
        response = self._request(
            method="GET",
            url=urljoin(
                self.api_url, f"/personal/statement/{account_id}/{from_date}/{to_date}"
            ),
        )

        return json.loads(response.text)

    def get_all_accounts_transactions(self, period: int) -> list[Transaction]:
        client_info = self.get_client_info()
        transactions = []
        for account in client_info.accounts:
            result = self.get_transactions(
                account_id=account.id,
                period=period,
            )
            for transaction in result:
                transactions.append(Transaction.model_validate(transaction))

        return transactions
