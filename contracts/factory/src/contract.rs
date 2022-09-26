#[cfg(not(feature = "library"))]
use cosmwasm_std::entry_point;
use cosmwasm_std::{Binary, Deps, DepsMut, Env, MessageInfo, Response, StdResult, WasmMsg, SubMsg, CosmosMsg, to_binary, ReplyOn, Reply, StdError, Uint128};
use cw2::set_contract_version;
use cw_utils::parse_reply_instantiate_data;

use crate::error::ContractError;
use crate::msg::{ExecuteMsg, InstantiateMsg, QueryMsg};
use cw20::{Cw20InstantiateMsg, MinterResponse, Cw20Coin};
use crate::state::{LATEST_TOKEN};


const CONTRACT_NAME: &str = "crates.io:factory";
const CONTRACT_VERSION: &str = env!("CARGO_PKG_VERSION");
const INSTANTIATE_REPLY_ID: u64= 1;


#[cfg_attr(not(feature = "library"), entry_point)]
pub fn instantiate(
    deps: DepsMut,
    _env: Env,
    _info: MessageInfo,
    _msg: InstantiateMsg,
) -> Result<Response, ContractError> {
    set_contract_version(deps.storage, CONTRACT_NAME, CONTRACT_VERSION)?;

    Ok(Response::new().add_attribute("action", "instantiate"))
}

#[cfg_attr(not(feature = "library"), entry_point)]
pub fn execute(
    deps: DepsMut,
    _env: Env,
    info: MessageInfo,
    msg: ExecuteMsg,
) -> Result<Response, ContractError> {
    match msg {
        ExecuteMsg::CreateToken {code_id} => exe_create_token(deps, info, code_id),
    }
}


fn exe_create_token(_deps:DepsMut, info: MessageInfo, code_id: u64) -> Result<Response, ContractError>{
    // Creating a response with the submessage
    let response = Response::new();
    Ok(response.add_submessage(SubMsg {
        id: 1,
        gas_limit: None,
        msg: CosmosMsg::Wasm(WasmMsg::Instantiate {
            code_id: code_id,
            funds: vec![],
            admin: Some(info.sender.to_string()),
            label: "token".to_string(),
            msg: to_binary(&Cw20InstantiateMsg {
                name: "new token".to_string(),
                symbol: "nToken".to_string(),
                decimals: 6,
                initial_balances: vec![Cw20Coin{address: info.sender.to_string(), amount: Uint128::new(100)}],
                mint: Some(MinterResponse {
                    minter: info.sender.to_string(),
                    cap: None,
                }),
                marketing: None
            })?,
        }),
        reply_on: ReplyOn::Success,
    })
    .add_attribute("aciton", "create_pair"))
}

#[cfg_attr(not(feature = "library"), entry_point)]
pub fn reply(deps: DepsMut, _env: Env, msg: Reply) -> StdResult<Response> {
    match msg.id {
        INSTANTIATE_REPLY_ID => handle_instantiate_reply(deps, msg),
        id => Err(StdError::generic_err(format!("Unknown reply id: {}", id))),
    }
}

fn handle_instantiate_reply(deps: DepsMut, msg: Reply) -> StdResult<Response> {
    // Handle the msg data and save the contract address
    // See: https://github.com/CosmWasm/cw-plus/blob/main/packages/utils/src/parse_reply.rs
    let res = parse_reply_instantiate_data(msg).unwrap();
    
    LATEST_TOKEN.save(deps.storage, &res.contract_address)?;

    // Save res.contract_address
    Ok(Response::new().add_attribute("contract_addr", res.contract_address))
}


#[cfg_attr(not(feature = "library"), entry_point)]
pub fn query(deps: Deps, _env: Env, msg: QueryMsg) -> StdResult<Binary> {
    match msg {
        QueryMsg::GetLatestToken { } => to_binary(&query_latest_token(deps))
    }
}


fn query_latest_token(deps: Deps) -> String {
    LATEST_TOKEN.load(deps.storage).unwrap()
}