from brownie import config, network, accounts, interface
from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "development",
    "localnew",
    "None",
    "mainnet-fork-dev",
    "local",
]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


def get_dai_price_feed(price_feed_address):
    price_feed_contract = interface.AggregatorV3Interface(price_feed_address)
    dai_price = price_feed_contract.latestRoundData()[1]
    converted_dai = Web3.fromWei(dai_price, "ether")
    print(f"the dai/eth price is {converted_dai}")
    return float(converted_dai)
