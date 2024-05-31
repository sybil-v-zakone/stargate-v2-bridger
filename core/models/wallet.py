from dataclasses import dataclass

from core import Client
from core.models.chain import Chain


@dataclass
class Wallet:
    private_key: str
    address: str
    proxy: str
    src_chain: str
    dst_chain: str
    bridge_sent: bool = False

    def to_client(self, chain: Chain) -> Client:
        return Client(private_key=self.private_key, proxy=self.proxy, chain=chain)
