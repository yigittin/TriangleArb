import requests
import json
import func_arbitrage

urlPairs="https://api.binance.com/api/v3/exchangeInfo"
urlPrices="https://api.binance.com/api/v3/ticker/bookTicker"

def step_0():
#Binance Get All Ticker List
  url="https://api.binance.com/api/v3/exchangeInfo"
  coin_json=func_arbitrage.get_coin_ticker(url)
  return coin_json

def step_1(coin_list):
  #Structured list of coins
  structured_list=func_arbitrage.structure_triangular_pairs(coin_list)
  
  #Save Structured List
  with open("structured_triangular_pairs.json","w") as fp:
    json.dump(structured_list,fp)

#Calculate Surface Arbitrage Oppurtunities
def step_2():
  with open("structured_triangular_pairs.json") as json_file:
    structured_pairs=json.load(json_file)
  
  #Get Latest Surface Prices
  prices_json=func_arbitrage.get_coin_ticker(urlPrices)
  #Loop Through Prices
  for t_pair in structured_pairs:
    prices_dict=func_arbitrage.get_price_for_t_pair(t_pair,prices_json)
    if(prices_dict["pair_a_ask"]>0 and prices_dict["pair_a_bid"]>0 and prices_dict["pair_b_ask"]>0 and prices_dict["pair_b_bid"]>0 and prices_dict["pair_c_ask"]>0 and prices_dict["pair_c_bid"]>0):
      surface_arb=func_arbitrage.calc_triangular_arb_surface_rate(t_pair,prices_dict)
      print(surface_arb)
if __name__=="__main__":
  #coin_list=step_0()
  #step_1(coin_list)
  step_2()