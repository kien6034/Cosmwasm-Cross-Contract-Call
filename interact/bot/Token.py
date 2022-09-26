from re import L

from numpy import rec
from .Bot import Bot


class Token(Bot):
    ## for simplicity, decimal = 6
    def __init__(self, network_type, deployer_key, symbol, initial_balances, minter, contract_addr=None) -> None:
        super().__init__(network_type, deployer_key)
        
        if contract_addr == None:
            self.token_code_id = self.store_contract("cw20_base")
            self.symbol = symbol

            initial_balances_data = []
            for user in initial_balances:
                initial_balances_data.append(
                    {
                        "address": user[0],
                        "amount": user[1]
                    }
                )

            self.contract_addr = self.instantiate_contract(self.token_code_id, {
                "name": symbol,
                "symbol": symbol,
                "decimals": 6,
                "initial_balances": initial_balances_data,
                "mint": {
                    "minter": minter
                }
            })
        
        else:
            self.contract_addr = contract_addr

    
    def increase_allowance(self, owner, spender, amount): 
        self.execute_contract(
            owner,
            self.contract_addr,
            {
                "increase_allowance": {
                    "spender": spender,
                    "amount": amount
                }
            }
        )

    
    def transfer(self, sender, recipient, amount):
        self.execute_contract(
            sender,
            self.contract_addr,
            {
                "transfer": {
                    "recipient": recipient,
                    "amount": amount
                }
            }
        )

    def batch_transfer(self, sender, recipients, amounts):
        self.execute_contract(
            sender,
            self.contract_addr,
            {
                "batch_transfer":{
                    "recipients": recipients,
                    "amounts": amounts
                }
            }
        )

    
    def get_balance(self, user):
        return self.query_contract(
            self.contract_addr,
            {
                "balance": {
                    "address": user
                }
            }
        )

    def __repr__(self) -> str:
        return self.contract_addr