from eth_account.messages import encode_defunct
from web3 import Web3
from django.conf import settings

PROVIDER_URL = f"https://mainnet.infura.io/v3/{settings.WEB3_KEY}"

w3 = Web3(Web3.HTTPProvider(PROVIDER_URL))


def verify_message(address, signed):
    message = encode_defunct(text='meme party')
    decoded_address = w3.eth.account.recover_message(message, signature=signed)
    return decoded_address.lower() == address.lower()
