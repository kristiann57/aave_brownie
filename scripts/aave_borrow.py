from code import interact
from distutils.command.config import config
from threading import activeCount
from scripts.helpful_scripts import (
    get_account,
    FORKED_LOCAL_ENVIRONMENTS,
    get_dai_price_feed,
)
from scripts.get_weth import get_weth
from brownie import network, config, interface
from web3 import Web3

amount = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    print(f"just got an account {account.address}")
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    print("I am about to get some weth")
    if network.show_active() in FORKED_LOCAL_ENVIRONMENTS:
        get_weth()
    print("jus got seom weth some weth")
    lending_pool = get_lending_pool()
    print("ust got the lending pool contract to interact with it")
    # we need to approve each time we want to send erc20 tokens
    tx_approved = approve_erc20(lending_pool.address, amount, erc20_address, account)
    tx_approved.wait(1)
    # lets deposit the WETH ERC20 to the aave protocol
    tx = lending_pool.deposit(
        erc20_address, amount, account.address, 0, {"from": account}
    )
    print("I have just deposited the weth to the protocol")
    tx.wait(1)
    # I am requesting AAVE to tell me how much I can borrow based on my helth factor and
    availableBorrowsETH, totalDebtETH = get_account_data(lending_pool, account)
    latest_dai_price = get_dai_price_feed(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    amount_to_borrow_in_dai = (1 / latest_dai_price) * (availableBorrowsETH * 0.50)
    print(f"I am going to borrow {amount_to_borrow_in_dai} dai!")
    # I need the DAi token address to call the borrow method
    dai_token_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_token_address,
        Web3.toWei(amount_to_borrow_in_dai, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    get_account_data(lending_pool, account)
    repay_all(amount_to_borrow_in_dai, lending_pool, account)
    get_account_data(lending_pool, account)


def repay_all(amount, lending_pool, account):
    # borrowed_address_token = config["networks"][network.show_active()]["dai_token"]
    approve_erc20(
        lending_pool.address,
        Web3.toWei(amount, "ether"),
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    print("I have just aproved the repay transaction")
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        Web3.toWei(amount, "ether"),
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)


def approve_erc20(spender, amount, erc20_address, account):
    print("approving erc20 transaction")
    account = get_account()
    ERC20 = interface.IERC20(erc20_address)
    print(
        f"jsut got the ERC20 contract via the interface: erc20 address is {erc20_address}"
    )
    tx = ERC20.approve(spender, amount, {"from": account})
    print("executed the approve method of the ER20 contract")
    tx.wait(1)
    print("erc transation has been approved")
    return tx


def get_lending_pool():
    lending_pool_address_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    print(
        f"manage to get the right addressprovider from config {lending_pool_address_provider.address}"
    )
    # lending_pool_address = lending_pool_address_provider.getLendingPool()
    lending_pool_address = "0xE0fBa4Fc209b4948668006B2bE61711b7f465bAe"
    print(
        "about to get the lending pool contract by using the address and abi(interface)"
    )
    lending_pool = interface.ILendingPool(lending_pool_address)
    print(f"just got the lending pool contract {lending_pool.address}")
    return lending_pool


def get_account_data(lending_pool, account):
    (
        totalCollateralETH,
        totalDebtETH,
        availableBorrowsETH,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = lending_pool.getUserAccountData(account.address)
    print("accont data called and saved in a variable")
    totalCollateralETH = Web3.fromWei(totalCollateralETH, "ether")
    totalDebtETH = Web3.fromWei(totalDebtETH, "ether")
    availableBorrowsETH = Web3.fromWei(availableBorrowsETH, "ether")
    print(f"your totalCollateralETH is: {totalCollateralETH }")
    print(f"your totalDebtETH is: {totalDebtETH }")
    print(f"your availableBorrowsETH is: {availableBorrowsETH }")
    print(f"your currentLiquidationThreshold is: {currentLiquidationThreshold }")
    print(f"your ltv is: {ltv }")
    print(f"your healthFactor is: {healthFactor }")
    # print(f"your healthFactor is: {healthFactor }")
    return (float(availableBorrowsETH), float(totalDebtETH))
