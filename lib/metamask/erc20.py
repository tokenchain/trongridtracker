from web3 import Web3
import json
import os

private_key = os.getenv('SIGNER_PRIVATE_KEY')
project_id = os.getenv('INFURA_PROJECT_ID')
infura_url = 'https://goerli.infura.io/v3/{}'.format(project_id)
web3 = Web3(Web3.HTTPProvider(infura_url))


def send_ETH(from_address, to_address, amount):
    tx = {
        'type': '0x2',
        'nonce': web3.eth.getTransactionCount(from_address),
        'from': from_address,
        'to': to_address,
        'value': web3.toWei(0.01, 'ether'),
        'maxFeePerGas': web3.toWei('250', 'gwei'),
        'maxPriorityFeePerGas': web3.toWei('3', 'gwei'),
        'chainId': 5
    }
    gas = web3.eth.estimateGas(tx)
    tx['gas'] = gas
    signed_tx = web3.eth.account.signTransaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

    if tx_receipt['status'] == 1:
        print('ETH transferred successfully! Hash: {}'.format(str(web3.toHex(tx_hash))))
    else:
        print('There was an error transferring the ETH')


def send_ERC20(from_address, to_address, amount, contract):
    tx = contract.functions.transfer(to_address, amount).buildTransaction({
        'from': from_address,
        'nonce': web3.eth.getTransactionCount(from_address),
        'maxFeePerGas': web3.toWei('250', 'gwei'),
        'maxPriorityFeePerGas': web3.toWei('3', 'gwei'),
        'value': 0,
        'chainId': 5
    })
    gas = web3.eth.estimateGas(tx)
    tx['gas'] = gas
    signed_tx = web3.eth.account.signTransaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

    if tx_receipt['status'] == 1:
        print('Tokens transferred successfully! Hash: {}'.format(str(web3.toHex(tx_hash))))
    else:
        print('There was an error transferring the tokens')


if __name__ == '__main__':
    from_address = '0x66D...'
    to_address = '0x895...'

    ### SEND ETH ###################

    send_ETH(from_address, to_address, 10000)  # amount is in wei

    ### SEND ERC-20 ################

    # UNI token address on Goerli:
    contract_address = '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984'

    with open("./abi.json", 'r') as f:
        contract_abi = json.load(f)

    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    send_ERC20(from_address, to_address, 100000, contract)  # amount is in wei
