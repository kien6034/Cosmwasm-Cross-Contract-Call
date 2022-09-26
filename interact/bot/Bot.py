from terra_sdk.client.localterra import LocalTerra
from terra_sdk.util.contract import get_code_id, get_contract_address, read_file_as_b64
from terra_sdk.core.wasm import MsgStoreCode,MsgInstantiateContract, MsgExecuteContract, MsgMigrateContract
from terra_sdk.client.lcd import LCDClient
from terra_sdk.key.mnemonic import MnemonicKey 
from terra_sdk.core.coin import Coin
from terra_sdk.core.coins import Coins
from terra_sdk.key.raw import RawKey
from terra_sdk.client.lcd.api.tx import CreateTxOptions
import base64
from random import randbytes
import requests
from terra_sdk.core.wasm.data import AccessConfig, AccessType, AccAddress


import os, sys


from dotenv import load_dotenv
from urllib.request import urlopen
import json

class Bot:
    def __init__(self, network_type, deployer_key) -> None:
        self.deployer = None
        self.lt = None 
        self.isLocalTerra = False
        
        self.choose_network(network_type=network_type, menmonic_key = deployer_key)
        pass 
    
    def choose_network(self, network_type, menmonic_key) -> None:
        config = os.path.abspath("interact/bot/network.json")
        config_data = json.load(open(config))

        for nt in config_data:            
            if network_type == nt:
                if nt == "localterra":
                    gas_fee = "1uluna"
                    gas_adjustment = 2
                    self.lt = LocalTerra(gas_prices=gas_fee, gas_adjustment=2)

                    self.deployer  = self.lt.wallets["test1"]
                    self.isLocalTerra = True
                    return 
                else:
                    network = config_data[nt]
                    gas_fee, gas_adjustment= self.get_gas_fee(network["gas_url"])
                    self.lt = LCDClient(chain_id=network["chainID"], url=network["URL"], gas_prices=gas_fee, gas_adjustment=gas_adjustment)
                    
                    key = MnemonicKey(mnemonic=menmonic_key)
                    self.deployer = self.lt.wallet(key)
                    return 
        
        print("***** NETWORK TYPE ERROR: network type not support")
        sys.exit()
    

    def get_gas_fee(self, gas_url):
        f = requests.get(gas_url)
        data=  json.loads(f.text)
       
        return f"{data['uluna']}uluna", 1.4
    
    def get_deployer(self):
        return self.deployer
    
    def get_wallet(self, key):
        if self.isLocalTerra:
            print("--------- using LOCALTERRA: please use get_lt_wallet")
        return self.lt.wallet(key)
    
    def get_lt_wallet(self, phrase):
        if not self.isLocalTerra:
            print("---------- not using LOCALTERRA: please use get_wallet")
        return self.lt.wallets[phrase]

    
    def store_contract(self, contract_name):
        artifact_path = os.path.abspath("artifacts")
        contract_bytes = read_file_as_b64(f"{artifact_path}/{contract_name}.wasm")
    
        store_code = MsgStoreCode(
            self.deployer.key.acc_address,
            contract_bytes,
            instantiate_permission= AccessConfig(permission=AccessType.ACCESS_TYPE_EVERYBODY, address=None)
        )

        tx = self.deployer.create_and_sign_tx(
            options= CreateTxOptions(msgs=[store_code])
        )
        
        result = self.lt.tx.broadcast(tx)    
    
        code_id = get_code_id(result)
        print(f"New code id is created at: {code_id}")
        return code_id
    
    def migrate_contract(self, admin, contract, new_code_id, migrate_msg):
        msg = MsgMigrateContract(
            admin.key.acc_address,
            contract,
            new_code_id,
            migrate_msg
        )

        tx = admin.create_and_sign_tx(options=CreateTxOptions(msgs=[msg]))
        result = self.lt.tx.broadcast(tx)
        return result
        

    def instantiate_contract(self,code_id, init_msg):
        msg = MsgInstantiateContract(
            self.deployer.key.acc_address,
            self.deployer.key.acc_address,
            code_id,
            "kien6034",
            init_msg
        )

        tx = self.deployer.create_and_sign_tx(options=CreateTxOptions(msgs=[msg]))
        result = self.lt.tx.broadcast(tx)

        contract_address = get_contract_address(result)
        print(f"\n Contract instantiate with init msg: {init_msg} at: ---- {contract_address}\n ========================================\n")
        return contract_address


    def execute_contract(self, sender, contract_addr, exe_msg, coins=None):
        status = True
        if not coins:
            msg = MsgExecuteContract(
                sender.key.acc_address,
                contract_addr,
                exe_msg,
            )
        else:
            msg = MsgExecuteContract(
                sender.key.acc_address,
                contract_addr,
                exe_msg,
                coins=coins
            )

        tx = sender.create_and_sign_tx(options=CreateTxOptions(msgs=[msg]))
        result = self.lt.tx.broadcast(tx)

        if result.raw_log.__contains__("failed to execute message"):
            print('** ERROR: ', result.raw_log.split("message index: 0:")[1].split(": execute wasm contract failed")[0], '\n')
            return result, False
        else:
            print(f"EXECUTE: succeeded: {exe_msg} \n -----------------------------\n")
        return result, status

    def query_contract(self, contract_addr, msg):
        query_data= self.lt.wasm.contract_query(
            contract_addr,
            msg
        )
        print(f"QUERY: {query_data}")
        return query_data


 
    
                

                
            
             
        