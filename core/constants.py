import os
import sys
from pathlib import Path

from core.utils import read_from_json

if getattr(sys, "frozen", False):
    ROOT_DIR = Path(sys.executable).parent.absolute()
else:
    ROOT_DIR = Path(__file__).parent.absolute()

ABI_DIR = os.path.join(ROOT_DIR, "abis")

# path to private_keys.txt file
PRIVATE_KEYS_PATH = "data/private_keys.txt"

# path to proxies.txt file
PROXIES_PATH = "data/proxies.txt"

# path to a database.json file
DATABASE_PATH = "data/database.json"

GAS_MULTIPLIER = 1.2

RETRIES = 10

APPROVE_VALUE_RANGE = None

MAX_SLIPPAGE = 1

GAS_FEES_ESTIMATION_MULTIPLIER = 0.99

# stargate
STARGATE_ETH_NATIVE_POOL_ADDRESSES = {
    42161: "0xA45B5130f36CDcA45667738e2a258AB09f4A5f7F",
    10: "0xe8CDF27AcD73a434D661C84887215F7598e7d0d3",
    59144: "0x81F6138153d473E8c5EcebD3DC8Cd4903506B075",
    8453: "0xdc181Bd607330aeeBEF6ea62e03e5e1Fb4B6F7C7",
    534352: "0xC2b638Cb5042c1B3c5d5C969361fB50569840583",
}

STARGATE_NATIVE_POOL_ABI = read_from_json(os.path.join(ABI_DIR, "stargate_native_pool.json"))

STARGATE_FULL_BRIDGE_SIMULATION_TX_VALUE = 10000000000000

# common
EMPTY_DATA = "0x"
