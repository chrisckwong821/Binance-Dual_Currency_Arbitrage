# Binance-Dual_Currency_Arbitrage
(Beta) Bi-directional price engine for triangular arbitrage. Need to hold 2 base currencies

# Usage
1. Add key and secret in `key/key.json`

2. run  `python arb_engine.py cur1 cur2`

example : 
`python arb_engine.py BNB BTC` or `python arb_engine.py BTC BNB`
create websockets subscription to all price stream that have both BNB/X and X/BTC symbols, regardless of currencies being the base or quote currencies. 



# Output
(+BNB)s1b2: sell ANKRBNB buy ANKRBTC make 0.012(BNB) 1.2% 2543

### Explanation :
**+BNB:** The flow results in a net gain of BNB in the first two legs( / net loss in BTC), thus the final leg would sell BNBBTC. 

**s1b2:** selling symbol 1 and buying symbol 2. sell ANKRBNB and buy ANKRBTC in this example.

**make 0.012(BNB):** Expected profit (without discounting commission)

**1.2%:** Profit margin(%)

**2543:** Quantity in target currency, ANKR in this example



# Dependency
`pip install requests websocket websocket-client`



