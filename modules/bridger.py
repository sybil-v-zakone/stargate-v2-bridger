import random

from config import (
    USE_FULL_BRIDGE,
    USE_MOBILE_PROXY,
    BALANCE_PERCENTAGE_TO_BRIDGE,
    STARGATE_BRIDGE_MODE,
    WALLET_DELAY_RANGE,
    AFTER_FAIL_DELAY_RANGE,
    INCLUDE_FEES_IN_AMOUNT,
)
from core import logger
from core.dapps import Stargate
from core.models.chain import Chain
from core.utils import change_ip, sleep_pause
from modules import Database


async def bridge_batch():
    database = Database.read_from_json()

    while True:
        wallet = database.get_random_active_item()

        if not wallet:
            break

        if USE_MOBILE_PROXY:
            await change_ip()

        logger.info(f"Wallet: {wallet.address}")
        logger.debug(f"Transactions left: {database.transactions_left}")

        client = wallet.to_client(chain=Chain.from_name(wallet.src_chain))

        if USE_FULL_BRIDGE:
            amount_to_bridge = None
            include_fees = False
        else:
            balance = await client.get_native_balance(wei=False)
            amount_to_bridge = balance * (random.randint(*BALANCE_PERCENTAGE_TO_BRIDGE) / 100)
            include_fees = INCLUDE_FEES_IN_AMOUNT

        if await Stargate(client=client).bridge(
            dst_chain=Chain.from_name(wallet.dst_chain),
            amount=amount_to_bridge,
            mode=STARGATE_BRIDGE_MODE,
            include_fees=include_fees,
        ):
            wallet.bridge_sent = True
            database.save_database()
            sleep_range = WALLET_DELAY_RANGE
        else:
            sleep_range = AFTER_FAIL_DELAY_RANGE

        await sleep_pause(delay_range=sleep_range, enable_message=False)
    logger.success(f"All bridges sent")
