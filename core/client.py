import asyncio
from typing import Dict, Optional, Union

from aiohttp_proxy import ProxyConnector
from web3 import AsyncWeb3
from web3.middleware import async_geth_poa_middleware

from core import logger
from core.constants import GAS_MULTIPLIER, RETRIES
from core.models.chain import Chain, MAINNET
from core.utils import retry_on_fail


class Client:
    def __init__(self, private_key: str, proxy: str = None, chain: Chain = MAINNET) -> None:
        self.private_key = private_key
        self.chain = chain
        self.proxy = proxy
        self.w3 = self.init_web3(chain=chain)
        self.address = AsyncWeb3.to_checksum_address(
            value=self.w3.eth.account.from_key(private_key=private_key).address
        )

    def __str__(self) -> str:
        return self.address

    def __repr__(self) -> str:
        return self.address

    def init_web3(self, chain: Chain = None):
        request_kwargs = {"proxy": f"http://{self.proxy}"} if self.proxy else {}

        try:
            if not chain.rpc:
                raise NoRPCEndpointSpecifiedError

            return AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(endpoint_uri=chain.rpc, request_kwargs=request_kwargs))

        except NoRPCEndpointSpecifiedError as e:
            logger.error(e)
            exit()

    def change_chain(self, chain: Chain) -> None:
        self.chain = chain
        self.w3 = self.init_web3(chain=chain)

    async def send_transaction(
        self,
        to: str,
        data: str = None,
        from_: str = None,
        value: int = None,
    ):
        tx_params = await self.get_tx_params(to=to, data=data, from_=from_, value=value)

        tx_params["gas"] = await self.get_gas_estimate(tx_params=tx_params)

        sign = self.w3.eth.account.sign_transaction(tx_params, self.private_key)

        try:
            return await self.w3.eth.send_raw_transaction(sign.raw_transaction)

        except Exception as e:
            logger.error(f"Error while sending transaction: {e}")

    async def get_gas_estimate(self, tx_params: dict) -> int:
        while True:
            try:
                return await self.w3.eth.estimate_gas(tx_params)
            except Exception as e:
                if 'Block with id:' in str(e):
                    await asyncio.sleep(1)
                    continue
                raise e

    async def get_tx_params(self, to: str, data: str = None, from_: str = None, value: int = None) -> Dict:
        if not from_:
            from_ = self.address

        tx_params = {
            "chainId": await self.w3.eth.chain_id,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "from": self.w3.to_checksum_address(from_),
            "to": self.w3.to_checksum_address(to),
        }

        if data:
            tx_params["data"] = data

        if value:
            tx_params["value"] = value

        if self.chain.eip_1559:
            eip1559_params = await self._get_eip1559_params()
            tx_params["maxPriorityFeePerGas"] = eip1559_params["max_priority_fee_per_gas"]
            tx_params["maxFeePerGas"] = eip1559_params["max_fee_per_gas"]
        else:
            tx_params["gasPrice"] = await self.w3.eth.gas_price

        return tx_params

    async def verify_tx(self, tx_hash: str) -> bool:
        try:
            if tx_hash is None:
                return False

            response = await self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)

            if "status" in response and response["status"] == 1:
                logger.success(f"Transaction was successful: {self.chain.explorer}tx/{self.w3.to_hex(tx_hash)}")
                return True
            else:
                logger.error(f"Transaction failed: {self.chain.explorer}tx/{self.w3.to_hex(tx_hash)}")
                return False

        except Exception as e:
            logger.error(f"Unexpected error in verify_tx function: {e}")
            return False

    async def _get_eip1559_params(self) -> Dict[str, int]:
        w3 = self.init_web3(chain=self.chain)
        w3.middleware_onion.inject(async_geth_poa_middleware, layer=0)

        last_block = await w3.eth.get_block("latest")

        max_priority_fee_per_gas = await Client.get_max_priority_fee_per_gas(w3=w3, block=last_block)
        base_fee = int(last_block["baseFeePerGas"] * GAS_MULTIPLIER)
        max_fee_per_gas = base_fee + max_priority_fee_per_gas

        return {"max_priority_fee_per_gas": max_priority_fee_per_gas, "max_fee_per_gas": max_fee_per_gas}

    @staticmethod
    async def get_max_priority_fee_per_gas(w3: AsyncWeb3, block: dict) -> int:
        block_number = block["number"]

        latest_block_transaction_count = await w3.eth.get_block_transaction_count(block_number)
        max_priority_fee_per_gas_list = []
        for i in range(latest_block_transaction_count):
            try:
                transaction = await w3.eth.get_transaction_by_block(block_number, i)
                if "maxPriorityFeePerGas" in transaction:
                    max_priority_fee_per_gas_list.append(transaction["maxPriorityFeePerGas"])
            except Exception:
                continue

        if not max_priority_fee_per_gas_list:
            max_priority_fee_per_gas = await w3.eth.max_priority_fee
        else:
            max_priority_fee_per_gas_list.sort()
            max_priority_fee_per_gas = max_priority_fee_per_gas_list[len(max_priority_fee_per_gas_list) // 2]
        return max_priority_fee_per_gas

    @retry_on_fail(tries=RETRIES)
    async def get_native_balance(self, chain: Optional[Chain] = None, wei: bool = True) -> Optional[Union[int, float]]:
        w3 = self.w3 if chain is None else self.init_web3(chain=chain)

        try:
            balance = await w3.eth.get_balance(self.address)
            return balance if wei else float(AsyncWeb3.from_wei(balance, 'ether'))
        except Exception as e:
            logger.exception(f"Could not get balance of: {self.address}: {e}")
            return None

    def get_proxy_connector(self):
        if self.proxy is not None:
            proxy_url = f"http://{self.proxy}"
            return ProxyConnector.from_url(url=proxy_url)
        else:
            return None


class NoRPCEndpointSpecifiedError(Exception):
    def __init__(
        self,
        message: str = "No RPC endpoint specified. Specify one in config.py file",
        *args: object,
    ) -> None:
        self.message = message
        super().__init__(self.message, *args)
