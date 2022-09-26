from asyncio import constants
from bot.Bot import Bot
from bot.Token import Token
from terra_sdk.client.lcd import LCDClient
from dotenv import load_dotenv
import os, sys, json, base64


load_dotenv() 
network = "testnet"

try:
    deployer_key = os.environ.get("MNEMONIC_KEY")
    #contract_addr = os.environ.get("CONTRACT_ADDR")
except:
    print("Invalid enviroment variable")
    sys.exit()
deployer_key = os.environ.get("MNEMONIC_KEY")


bot = Bot(network, deployer_key)
deployer = bot.get_deployer()
print(deployer.key.acc_address)


token = Token(network, deployer_key, "ABC", [(deployer.key.acc_address, "1000000000000")], deployer.key.acc_address)