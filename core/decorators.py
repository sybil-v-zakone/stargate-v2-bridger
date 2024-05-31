import asyncio
import random
from functools import wraps

from tqdm import tqdm
from web3 import AsyncWeb3

from config import GAS_THRESHOLDS
from core import logger
from core.models.chain import Polygon, MAINNET
from core.utils import sleep_pause, get_chain_gas_fee


def wait(delay_range: list):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            result = await func(self, *args, **kwargs)
            await sleep_pause(delay_range=delay_range, enable_message=False)
            return result

        return wrapper

    return decorator


def gas_delay(delay_range: list):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            while True:
                current_erc20_gas_fee = await get_chain_gas_fee(MAINNET)
                threshold = AsyncWeb3.to_wei(GAS_THRESHOLDS[MAINNET.name]['value'], "gwei")

                if current_erc20_gas_fee > threshold:
                    random_delay = random.randint(*delay_range)

                    logger.warning(
                        f"[ERC20] Current gas fee {round(AsyncWeb3.from_wei(current_erc20_gas_fee, 'gwei'), 2)} GWEI > Gas "
                        f"threshold {AsyncWeb3.from_wei(threshold, 'gwei')} GWEI. Waiting for {random_delay} seconds..."
                    )

                    with tqdm(
                            total=random_delay,
                            desc="Waiting",
                            unit="s",
                            dynamic_ncols=True,
                            colour="blue",
                    ) as pbar:
                        for _ in range(random_delay):
                            await asyncio.sleep(1)
                            pbar.update(1)
                else:
                    break

            if "src_chain" in kwargs:
                src_chain = kwargs["src_chain"]
            else:
                src_chain = Polygon

            if src_chain.name not in GAS_THRESHOLDS or not GAS_THRESHOLDS[src_chain.name]['enabled']:
                return await func(*args, **kwargs)

            while True:
                current_src_chain_gas_fee = await get_chain_gas_fee(src_chain)
                threshold = AsyncWeb3.to_wei(GAS_THRESHOLDS[src_chain.name]['value'], "gwei")

                if current_src_chain_gas_fee > threshold:
                    random_delay = random.randint(*delay_range)
                    gas_gwei = round(AsyncWeb3.from_wei(current_src_chain_gas_fee, 'gwei'), 2)

                    logger.warning(
                        f"[{src_chain.name}] Current gas fee {gas_gwei} GWEI > Gas "
                        f"threshold {AsyncWeb3.from_wei(threshold, 'gwei')} GWEI. Waiting for {random_delay} seconds..."
                    )

                    with tqdm(
                            total=random_delay,
                            desc="Waiting",
                            unit="s",
                            dynamic_ncols=True,
                            colour="blue",
                    ) as pbar:
                        for _ in range(random_delay):
                            await asyncio.sleep(1)
                            pbar.update(1)
                else:
                    break

            return await func(*args, **kwargs)

        return wrapper

    return decorator
