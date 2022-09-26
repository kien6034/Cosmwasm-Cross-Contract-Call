from re import L

from numpy import rec
from .Bot import Bot


class Factory(Bot):
    ## for simplicity, decimal = 6
    def __init__(self, network_type, deployer_key, contract_addr=None) -> None:
        super().__init__(network_type, deployer_key)
        
        if contract_addr == None:
            self.factory_id = self.store_contract("factory")

            self.contract_addr = self.instantiate_contract(self.factory_id, {})
        
        else:
            self.contract_addr = contract_addr


    def create_token(self, owner, token_code_id): 
        self.execute_contract(
            owner,
            self.contract_addr,
            {
                "create_token": {
                    "code_id": token_code_id,
                }
            }
        )

    
    def get_latest_token(self):
        return self.query_contract(
            self.contract_addr,
            {
                "get_latest_token": {
                }
            }
        )
    
    def __repr__(self) -> str:
        return self.contract_addr