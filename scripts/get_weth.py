from scripts.helpful_scripts import get_account
from brownie import interface, config, network, accounts
from web3 import Web3


def get_weth():
    account = get_account()
    print("i have an account")
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    print("Ihave an interface for weth")
    value = Web3.toWei(0.1, "ether")
    tx = weth.deposit({"from": account, "value": Web3.toWei(0.09, "ether")})
    print("I have deposited some weth")
    # tx.wait(1)
    print("Received 0.1 WETH")

    return tx

    # Mints WETH by depositing ETH
    # we alwas need ABI and ADDRESS


def main():
    get_weth()
