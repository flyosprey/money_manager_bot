import base64
import json
import re
import uuid
from datetime import datetime, timedelta
from urllib.parse import quote, urljoin

from requests.exceptions import RequestException

from money_manager.config import TIMEZONE_KYIV
from tbot.clients.base import BaseClient
from tbot.dto.transactions.payload import SimpleTransaction
from tbot.dto.walletapp.mcc_codes import MCCCodeCategory
from tbot.errors import InvalidCredentialsError
from tbot.utils import convert_timestamp_to_datetime


class WalletAppClient(BaseClient):
    name = "WalletApp"
    api_url = "https://api.budgetbakers.com"

    def login(self, username: str, password: str) -> tuple[str, str]:
        self.activate_session_id()
        session_id = self.get_session_id(username=username, password=password)
        return self.get_owner_id(session_id=session_id)

    def activate_session_id(self) -> None:
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9,uk;q=0.8",
            "access-control-request-headers": "flavor,platform,web-version-code",
            "access-control-request-method": "POST",
            "origin": "https://web.budgetbakers.com",
            "priority": "u=1, i",
        }
        self._request(
            method="OPTIONS",
            headers=headers,
            url=urljoin(self.api_url, "/auth/authenticate/userpass"),
        )

    def get_session_id(self, username: str, password: str) -> str:
        payload = quote(f"username={username}&password={password}", safe="=&")
        headers = {
            "accept": "application/json, text/plain, text/html, */*",
            "accept-language": "en-US,en;q=0.9,uk;q=0.8",
            "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
            "flavor": "0",
            "origin": "https://web.budgetbakers.com",
            "platform": "web",
            "priority": "u=1, i",
            "web-version-code": "4.18.9",
        }
        try:
            response = self._request(
                method="POST",
                headers=headers,
                data=payload,
                url=urljoin(self.api_url, "/auth/authenticate/userpass"),
            )
        except RequestException as error:
            raise InvalidCredentialsError("Username or password are invalid") from error

        return response.cookies["id"]

    def get_owner_id(self, session_id: str) -> tuple[str, str]:
        headers = {
            "accept": "application/json, text/plain, text/html, */*",
            "accept-language": "en-US,en;q=0.9,uk;q=0.8",
            "cookie": f"id={session_id}",
            "flavor": "0",
            "origin": "https://web.budgetbakers.com",
            "platform": "web",
            "priority": "u=1, i",
            "referer": "https://web.budgetbakers.com/",
            "web-version-code": "4.18.9",
        }
        response = self._request(
            method="GET",
            headers=headers,
            url=urljoin(self.api_url, "/ribeez/user/abc"),
        )

        owner_id = re.search(r"bb-([-\d\w]+)", response.text)
        if not owner_id:
            raise Exception("No owner id!")

        owner_id_token = re.search(rf"{owner_id[1]}\"\$(.+?)\*", response.text)
        if not owner_id_token:
            raise Exception("No owner id token!")

        return owner_id[1], owner_id_token[1]


class CloudWalletAppClient(BaseClient):
    name = "CloudWalletApp"
    api_url = "https://couch-prod-eu-{version}.budgetbakers.com"
    api_versions = (1, 2)

    def __init__(self, owner_id: str, owner_id_token: str, *args, **kwargs):
        credentials = {
            "authorization": f'Basic {base64.b64encode(f"{owner_id}:{owner_id_token}".encode()).decode()}'
        }
        super().__init__(*args, **kwargs, credentials=credentials)

        self.owner_id = owner_id
        self.current_api_version = self.__find_current_api_version()

        self.base_headers.update(
            {
                "Accept-Language": "en-US,en;q=0.9,uk;q=0.8",
                "Connection": "keep-alive",
                "Origin": "https://web.budgetbakers.com",
                "Referer": "https://web.budgetbakers.com/",
                "accept": "application/json",
                "content-type": "application/json",
            }
        )

    def __prepare_payload(
        self, transaction: SimpleTransaction, record_id: str, rev_id: str
    ) -> dict:
        record_date = convert_timestamp_to_datetime(
            timestamp=transaction.time
        ) - timedelta(
            hours=datetime.now(tz=TIMEZONE_KYIV).utcoffset().total_seconds() / 3600
        )
        created_at = (
            datetime.now(tz=TIMEZONE_KYIV).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        )
        currency_id, account_id = self.__find_account_currency_id(
            data=self.get_history_changes()
        )
        return {
            "docs": [
                {
                    "reservedCreatedAt": created_at,
                    "reservedModelType": "Record",
                    "reservedOwnerId": self.owner_id,
                    "reservedAuthorId": self.owner_id,
                    "reservedSource": "web",
                    "recordDate": record_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
                    + "Z",
                    "type": int(transaction.amount < 0),
                    "recordState": 1,
                    "paymentType": 1,
                    "amount": abs(transaction.amount),
                    "labels": [],
                    "currencyId": currency_id,
                    "accountId": account_id,
                    "categoryId": MCCCodeCategory[transaction.type][transaction.mcc],
                    "payee": transaction.contractor,
                    "note": transaction.note,
                    "refAmount": abs(transaction.amount),
                    "reservedUpdatedAt": created_at,
                    "_id": f"Record_{record_id}",
                    "_rev": f"1-{rev_id}",
                }
            ],
            "new_edits": False,
        }

    @staticmethod
    def __find_account_currency_id(data: dict) -> tuple[str, str]:
        currency_id = None
        account_id = None

        for result in data["results"]:
            if result["id"].startswith("-Currency_"):
                currency_id = result["id"]
            if account_id is None and result["id"].startswith("-Account_"):
                account_id = result["id"]
            if currency_id and account_id:
                break

        return currency_id, account_id

    def __find_current_api_version(self) -> int | None:
        for index, version in enumerate(self.api_versions):
            try:
                self._request(
                    method="GET",
                    url=urljoin(
                        self.api_url.format(version=version),
                        f"/bb-{self.owner_id}/_changes",
                    ),
                )
                return version
            except RequestException as e:
                if index + 1 == len(self.api_versions):
                    raise e

        return

    def add_record(
        self,
        transaction: SimpleTransaction,
        record_id: str = None,
        rev_id: str = None,
    ) -> None:
        if record_id is None:
            record_id = str(uuid.uuid4())
        if rev_id is None:
            rev_id = str(uuid.uuid4()).replace("-", "")

        payload = self.__prepare_payload(
            transaction=transaction, record_id=record_id, rev_id=rev_id
        )
        if not self.initialize_record(record_id=record_id, rev_id=rev_id):
            raise Exception("Failed to initialize record!")

        self.create_record(payload=payload)

    def get_history_changes(self) -> dict:
        response = self._request(
            method="GET",
            url=urljoin(
                self.api_url.format(version=self.current_api_version),
                f"/bb-{self.owner_id}/_changes",
            ),
        )

        return json.loads(response.text)

    def initialize_record(self, record_id: str, rev_id: str) -> bool:
        payload = json.dumps({f"Record_{record_id}": [f"1-{rev_id}"]})
        response = self._request(
            method="POST",
            data=payload,
            url=urljoin(
                self.api_url.format(version=self.current_api_version),
                f"/bb-{self.owner_id}/_revs_diff",
            ),
        )

        return "missing" in response.text

    def create_record(self, payload: dict) -> None:
        self._request(
            method="POST",
            data=json.dumps(payload),
            url=urljoin(
                self.api_url.format(version=self.current_api_version),
                f"/bb-{self.owner_id}/_bulk_docs",
            ),
        )
