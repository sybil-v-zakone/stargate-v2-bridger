import itertools
import json
import random
import sys
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from config import (
    USE_MOBILE_PROXY,
    SRC_CHAIN,
    DST_CHAIN,
)
from core import logger, Client
from core.constants import PRIVATE_KEYS_PATH, PROXIES_PATH, DATABASE_PATH
from core.models.wallet import Wallet
from core.utils import read_from_txt


@dataclass
class Database:
    data: List[Wallet]

    def _to_dict(self) -> List[Dict[str, Any]]:
        return [vars(data_item) for data_item in self.data]

    @staticmethod
    def create_database() -> "Database":
        if SRC_CHAIN == "" or DST_CHAIN == "":
            logger.error(f"SRC_CHAIN and DST_CHAIN must be specified")
            sys.exit(1)
        if SRC_CHAIN == DST_CHAIN:
            logger.error(f"SRC_CHAIN and DST_CHAIN must have different values")
            sys.exit(1)

        data = []

        private_keys = read_from_txt(file_path=PRIVATE_KEYS_PATH)
        proxies = read_from_txt(file_path=PROXIES_PATH)

        if USE_MOBILE_PROXY:
            proxies = proxies * len(private_keys)

        for private_key, proxy in itertools.zip_longest(private_keys, proxies, fillvalue=None):
            try:
                temp_client = Client(private_key=private_key, proxy=proxy)

                item = Wallet(
                    private_key=private_key,
                    address=temp_client.address,
                    proxy=proxy,
                    src_chain=SRC_CHAIN,
                    dst_chain=DST_CHAIN,
                )

                data.append(item)
            except Exception as e:
                logger.exception(f"[Database] {e}")

        logger.success(f"[Database] Created successfully", send_to_tg=False)
        return Database(data=data)

    def save_database(self, file_name: str = DATABASE_PATH):
        db_dict = self._to_dict()

        with open(file_name, "w") as json_file:
            json.dump(db_dict, json_file, indent=4)

    @classmethod
    def read_from_json(cls, file_name: str = DATABASE_PATH) -> "Database":
        try:
            with open(file_name, "r") as json_file:
                db_dict = json.load(json_file)
        except Exception as e:
            logger.error(f"[Database] {e}")

        data = []

        for item in db_dict:
            account_data = {
                "private_key": item.pop("private_key"),
                "proxy": item.pop("proxy"),
            }

            item.pop("address")

            account = Client(**account_data)
            data_item = Wallet(
                private_key=account.private_key, address=account.address, proxy=account_data["proxy"], **item
            )
            data.append(data_item)

        return cls(data=data)

    def get_random_active_item(self) -> Optional[Wallet]:
        active_wallets = [item for item in self.data if not item.bridge_sent]
        if len(active_wallets) == 0:
            return None
        return random.choice(active_wallets)

    @property
    def transactions_left(self) -> int:
        return len([item for item in self.data if not item.bridge_sent])
