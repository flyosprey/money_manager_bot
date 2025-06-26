import base64
import json
import re
import uuid
from datetime import datetime, timedelta
from urllib.parse import quote, urljoin

from requests.exceptions import RequestException

from money_manager.config import TIMEZONE_KYIV
from tbot.clients.base import BaseClient
from tbot.clients.walletapp_api.type import RecordType
from tbot.dto.transactions.payload import SimpleTransaction
from tbot.errors import InvalidCredentialsError
from tbot.utils import convert_timestamp_to_datetime

WEB_VERSION_CODE = "4.18.18"


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
            "Web-Version-Code": WEB_VERSION_CODE,
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
        self.current_api_version = self._find_current_api_version()

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

    def add_transaction(
        self,
        transaction: SimpleTransaction,
        record_id: str = None,
        rev_id: str = None,
    ) -> (str, dict):
        if record_id is None:
            record_id = str(uuid.uuid4())
        if rev_id is None:
            rev_id = str(uuid.uuid4()).replace("-", "")

        payload = self._prepare_create_transaction_payload(
            transaction=transaction, record_id=record_id, rev_id=rev_id
        )
        if not self.initialize_record(
            record_type=RecordType.TRANSACTION, record_id=record_id, rev_id=rev_id
        ):
            raise Exception("Failed to initialize record!")

        self.create_record(payload=payload)

        return record_id, payload

    def delete_transaction(
        self,
        transaction_payload: dict,
        rev_id: str = None,
    ) -> None:
        index = 2
        record_id = transaction_payload["docs"][0]["_id"].replace("Record_", "")
        if rev_id is None:
            rev_id = str(uuid.uuid4()).replace("-", "")

        payload = self._prepare_delete_transaction_payload(
            transaction_payload=transaction_payload, rev_id=rev_id, index=index
        )
        if not self.initialize_record(
            record_type=RecordType.TRANSACTION,
            record_id=record_id,
            rev_id=rev_id,
            index=index,
        ):
            raise Exception("Failed to initialize record!")

        self.create_record(payload=payload)

    def add_label(
        self,
        label: str,
        record_id: str = None,
        rev_id: str = None,
    ) -> str:
        if record_id is None:
            record_id = str(uuid.uuid4())
        if rev_id is None:
            rev_id = str(uuid.uuid4()).replace("-", "")

        payload = self._prepare_label_payload(
            label=label, record_id=record_id, rev_id=rev_id
        )
        if not self.initialize_record(
            record_type=RecordType.LABEL, record_id=record_id, rev_id=rev_id
        ):
            raise Exception("Failed to initialize record!")

        self.create_record(payload=payload)

        return record_id

    def get_history_changes(self) -> dict:
        response = self._request(
            method="GET",
            url=urljoin(
                self.api_url.format(version=self.current_api_version),
                f"/bb-{self.owner_id}/_changes",
            ),
        )

        return json.loads(response.text)

    def initialize_record(
        self, record_type: RecordType, record_id: str, rev_id: str, index: int = 1
    ) -> bool:
        payload = json.dumps(
            {f"{record_type.value}_{record_id}": [f"{index}-{rev_id}"]}
        )
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

    def _prepare_label_payload(self, label: str, record_id: str, rev_id: str) -> dict:
        created_at = self.get_datetime_now()
        return {
            "docs": [
                {
                    "reservedCreatedAt": created_at,
                    "reservedModelType": "HashTag",
                    "reservedOwnerId": self.owner_id,
                    "reservedAuthorId": self.owner_id,
                    "reservedSource": "web",
                    "name": label,
                    "color": "#26c6da",
                    "position": 1000,
                    "autoAssign": False,
                    "reservedUpdatedAt": created_at,
                    "_id": f"-HashTag_{record_id}",
                    "_rev": f"1-{rev_id}",
                }
            ],
            "new_edits": False,
        }

    @staticmethod
    def get_datetime_now():
        return (
            datetime.now(tz=TIMEZONE_KYIV).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        )

    def _prepare_delete_transaction_payload(
        self, transaction_payload: dict, rev_id: str, index: int = 2
    ) -> dict:
        doc = transaction_payload["docs"][0]
        deleted_at = self.get_datetime_now()

        old_rev_id = doc["_rev"]
        doc["_rev"] = f"{index}-{rev_id}"
        doc["_deleted"] = True
        doc["reservedDeletedAt"] = deleted_at
        doc["reservedDeletedSource"] = "web"
        doc["_revisions"] = {"start": 2, "ids": [rev_id, old_rev_id.split("-")[1]]}
        return transaction_payload

    def _prepare_create_transaction_payload(
        self, transaction: SimpleTransaction, record_id: str, rev_id: str
    ) -> dict:
        record_date = convert_timestamp_to_datetime(
            timestamp=transaction.time
        ) - timedelta(
            hours=datetime.now(tz=TIMEZONE_KYIV).utcoffset().total_seconds() / 3600
        )
        created_at = self.get_datetime_now()
        currency_id, account_id = self._find_account_currency_id(
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
                    "labels": (
                        [f"-HashTag_{transaction.label_id}"]
                        if transaction.label_id
                        else []
                    ),
                    "currencyId": currency_id,
                    "accountId": account_id,
                    "categoryId": transaction.category_id,
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
    def _find_account_currency_id(data: dict) -> tuple[str, str]:
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

    def _find_current_api_version(self) -> int | None:
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
