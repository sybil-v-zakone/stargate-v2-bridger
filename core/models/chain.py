from dataclasses import dataclass
from enum import Enum
from typing import Optional

from config import (
    MAINNET_RPC_URL,
    LINEA_RPC_URL,
    SCROLL_RPC_URL,
    ARBITRUM_RPC_URL,
    BASE_RPC_URL,
    OPTIMISM_RPC_URL,
)


@dataclass
class Chain:
    name: str
    chain_id: int | None = None
    coin_symbol: str | None = None
    explorer: str | None = None
    eip_1559: bool | None = None
    rpc: str | None = None
    lz_eid: int | None = None

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_name(cls, name: str) -> Optional["Chain"]:
        try:
            return ChainEnum[name].value
        except KeyError:
            return None


MAINNET = Chain(
    name="ERC20",
    rpc=MAINNET_RPC_URL,
    chain_id=1,
    lz_eid=30101,
    coin_symbol="ETH",
    explorer="https://etherscan.io/",
    eip_1559=True
)

ARBITRUM = Chain(
    name="Arbitrum",
    rpc=ARBITRUM_RPC_URL,
    chain_id=42161,
    coin_symbol="ETH",
    explorer="https://arbiscan.io/",
    eip_1559=True,
    lz_eid=30110
)

LINEA = Chain(
    name="Linea",
    rpc=LINEA_RPC_URL,
    chain_id=59144,
    coin_symbol="ETH",
    explorer="https://lineascan.build/",
    eip_1559=True,
    lz_eid=30183
)

BASE = Chain(
    name="Base",
    rpc=BASE_RPC_URL,
    chain_id=8453,
    coin_symbol="ETH",
    explorer="https://basescan.org/",
    eip_1559=True,
    lz_eid=30184
)

SCROLL = Chain(
    name="Scroll",
    rpc=SCROLL_RPC_URL,
    chain_id=534352,
    coin_symbol="ETH",
    explorer="https://scrollscan.com/",
    eip_1559=False,
    lz_eid=30214
)


OPTIMISM = Chain(
    name="Optimism",
    rpc=OPTIMISM_RPC_URL,
    chain_id=10,
    coin_symbol="ETH",
    explorer="https://optimistic.etherscan.io/",
    eip_1559=True,
    lz_eid=30111
)


class ChainEnum(Enum):
    MAINNET = MAINNET
    Arbitrum = ARBITRUM
    Optimism = OPTIMISM
    Base = BASE
    Scroll = SCROLL
    Linea = LINEA
