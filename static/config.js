let CHAIN_ID;
let CHAIN_NAME;
let RPC_URL;
let RELAY_URL;
let API_URL;

if(window.location.hostname == 'api.web3bd.network'){
  RELAY_URL = 'wss://api.web3bd.network/relay';

}else{
  RELAY_URL = 'ws://127.0.0.1:8053/relay';

}

CHAIN_ID = '0x1';
CHAIN_NAME = 'Ethereum Mainnet';
RPC_URL = 'https://rpc.particle.network/evm-chain';
API_URL = 'https://api.web3bd.network';

export {
  CHAIN_ID,
  CHAIN_NAME,
  RPC_URL,
  RELAY_URL,
  API_URL
}

// export default{
//     name: "default"
// }

