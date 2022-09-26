from asyncio import constants
from bot.Bot import Bot
from bot.Token import Token
from bot.Factory import Factory
from terra_sdk.client.lcd import LCDClient
from dotenv import load_dotenv
import os, sys, json, base64


load_dotenv() 
network = "localterra"

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

wallet1 = bot.get_lt_wallet("test1")
wallet2 = bot.get_lt_wallet("test2")
wallet3 = bot.get_lt_wallet("test3")


token = Token(network, deployer_key, "ABC", [(deployer.key.acc_address, "1000000000000")], deployer.key.acc_address)

factory = Factory(network, deployer_key)


factory.create_token(deployer, int(token.token_code_id))

latest_token = factory.get_latest_token()


token1 = Token(network, deployer_key, "ABC", [(deployer.key.acc_address, "1000000000000")], deployer.key.acc_address, latest_token)

token1.get_balance(deployer.key.acc_address)
