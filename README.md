# Binance-Dual_Currency_Arbitrage
(Beta) two-leg price engine in a triangular arbitrage. Need to be price-agnostic to 2 base currencies

# Usage
1. Add key and secret in `key/key.json`

2. run  `python arb_engine cur1 cur2`

example : 
`python arb_engine BNB USDT` or `python arb_engine USDT BNB`
create websockets subscription to all price stream that have both BNB/X and X/USDT symbols, regardless of currencies being the base or quote currencies. 



# Output
(+BNB)s1b2: sell ANKRBNB buy ANKRBTC make 0.012(BNB) 0.022 2543.0

### Explanation :
1. +BNB : The trades results in a net gain of BNB (thus net loss in BTC)
2. s1b2 : selling symbol 1 and buying symbol 2. sell ANKRBNB and buy ANKRBTC in this example.
3. make 0.012(BNB): Expected profit (without discounting commission)
4. 0.022: Profit margin(%), 2.2% in this example.
5. 2543: Quantity, ANKR in this example
