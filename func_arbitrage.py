import requests
import json


#Binance Ticker
def get_coin_ticker(url):
    req=requests.get(url)
    coin_json=json.loads(req.text)
    return coin_json

#Structure Arbitrage Pairs
def structure_triangular_pairs(coin_list):
    #Declare Variables
    triangular_pairs_list=[]
    remove_duplicates_list=[]
    pairs_list=[]
  
  #Get Pair A  
    for pair_a in coin_list["symbols"]:
        a_base=pair_a["baseAsset"]
        a_quote=pair_a["quoteAsset"]
        #print(a_base, a_quote)
        
        #Assign A to Box
        a_pair_box=[a_base,a_quote]
        
        #Get Pair B
        for pair_b in coin_list["symbols"]:
            b_base=pair_b["baseAsset"]
            b_quote=pair_b["quoteAsset"]

            #Check Pair B
            if pair_b!=pair_a:
                if b_base in a_pair_box or b_quote in a_pair_box:
                    
                    #Get Pair C
                    for pair_c in coin_list["symbols"]:
                        c_base=pair_c["baseAsset"]
                        c_quote=pair_c["quoteAsset"]
                    
                    # Count the number of matching C items
                    if pair_c!=pair_a and pair_c!=pair_b:
                        pair_a_symbol=pair_a["symbol"]
                        pair_b_symbol=pair_b["symbol"]
                        pair_c_symbol=pair_c["symbol"]
                        combine_all=[pair_a_symbol,pair_b_symbol,pair_c_symbol]
                        pair_box=[a_base,a_quote,b_base,b_quote,c_base,c_quote]
                        
                        counts_c_base=0
                        for i in pair_box:
                            if i==c_quote:
                                counts_c_base+=1
                        counts_c_quote=0
                        for i in pair_box:
                            if i==c_quote:
                                counts_c_quote+=1
                        #Determine triangular Match
                        if counts_c_base==2 and counts_c_quote==2 and c_base!=c_quote:
                            combined=pair_a_symbol+","+pair_b_symbol+","+pair_c_symbol
                            unique_item=''.join(sorted(combine_all))

                            if unique_item not in remove_duplicates_list:
                                match_dict={
                                    "a_base":a_base,
                                    "b_base":b_base,
                                    "c_base":c_base,
                                    "a_quote":a_quote,
                                    "b_quote":b_quote,
                                    "c_quote":c_quote,
                                    "pair_a":pair_a["symbol"],
                                    "pair_b":pair_b["symbol"],
                                    "pair_c":pair_c["symbol"],
                                    "combined":combined
                                }
                                triangular_pairs_list.append(match_dict)
                                remove_duplicates_list.append(unique_item)
    return triangular_pairs_list

def get_price_for_t_pair(t_pair,prices_json):
    #Extract Pair Info
    pair_a=t_pair["pair_a"]
    pair_b=t_pair["pair_b"]
    pair_c=t_pair["pair_c"]
    pair_a_ask=0
    pair_b_ask=0
    pair_c_ask=0
    pair_a_bid=0
    pair_b_bid=0
    pair_c_bid=0
    
    for price_t in prices_json:
        if(price_t["symbol"]==pair_a):
            pair_a_ask= float(price_t["askPrice"])
        if(price_t["symbol"]==pair_a):
            pair_a_bid=float(price_t["bidPrice"])
        if(price_t["symbol"]==pair_b):
            pair_b_ask=float(price_t["askPrice"])
        if(price_t["symbol"]==pair_b):
            pair_b_bid=float(price_t["bidPrice"])
        if(price_t["symbol"]==pair_c):
            pair_c_ask=float(price_t["askPrice"])
        if(price_t["symbol"]==pair_c):
            pair_c_bid=float(price_t["bidPrice"])
            
    #Output Dictionary
    return{
        "pair_a_ask":pair_a_ask,
        "pair_a_bid":pair_a_bid,
        "pair_b_ask":pair_b_ask,
        "pair_b_bid":pair_b_bid,
        "pair_c_ask":pair_c_ask,
        "pair_c_bid":pair_c_bid,
    }
                            
def calc_triangular_arb_surface_rate(t_pair,prices_dict):
    
    #Set Variables
    starting_amount=1
    min_surface_rate=0
    surface_dict={}
    contract_2=""
    contract_3=""
    direction_trade_1=""
    direction_trade_2=""
    direction_trade_3=""
    acquired_coin_t2=0
    acquired_coin_t3=0
    calculated=0         
    
    #Extract Pair Variables
    a_base=t_pair["a_base"]
    a_quote=t_pair["a_quote"]
    b_base=t_pair["b_base"]
    b_quote=t_pair["b_quote"]
    c_base=t_pair["c_base"]
    c_quote=t_pair["c_quote"]
    pair_a=t_pair["pair_a"]
    pair_b=t_pair["pair_b"]
    pair_c=t_pair["pair_c"]
        
    #Extract Price Information
    a_ask=prices_dict["pair_a_ask"]
    a_bid=prices_dict["pair_a_bid"]
    b_ask=prices_dict["pair_b_ask"]
    b_bid=prices_dict["pair_b_bid"]        
    c_ask=prices_dict["pair_c_ask"]
    c_bid=prices_dict["pair_c_bid"]
    
    # Set directions and loop through
    direction_list={"forward","reverse"}
    for direction in direction_list:
        
        # Set additional variables for swap information
        swap_1=0
        swap_2=0
        swap_3=0
        swap_1_rate=0
        swap_2_rate=0
        swap_3_rate=0
        
    """
        If we are swapping the coin on the left (base) to the right (quote) then * 1/ask
        If we are swapping the coin on the right (quote) to the left (base) then * bid
    """
    
    if direction=="forward":
        swap_1=a_base
        swap_2=a_quote
        swap_1_rate=1/a_ask
        direction_trade_1="base_to_quote"
    if direction=="reverse":
        swap_1=a_quote
        swap_2=a_base
        swap_1_rate=a_bid
        direction_trade_1="quote_to_base"
    
    #Place first trade
    contract_1=pair_a
    acquired_coin_t1=starting_amount*swap_1_rate
    """  FORWARD """
    # SCENARIO 1 Check if a_quote (acquired_coin) matches b_quote
    if direction == "forward":
        if a_quote == b_quote and calculated == 0:
            swap_2_rate = b_bid
            acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
            direction_trade_2 = "quote_to_base"
            contract_2 = pair_b

            # If b_base (acquired coin) matches c_base
            if b_base == c_base:
                swap_3 = c_base
                swap_3_rate = 1 / c_ask
                direction_trade_3 = "base_to_quote"
                contract_3 = pair_c

            # If b_base (acquired coin) matches c_quote
            if b_base == c_quote:
                swap_3 = c_quote
                swap_3_rate = c_bid
                direction_trade_3 = "quote_to_base"
                contract_3 = pair_c

            acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
            calculated = 1

    # SCENARIO 2 Check if a_quote (acquired_coin) matches b_base
    if direction == "forward":
        if a_quote == b_base and calculated == 0:
            swap_2_rate = 1 / b_ask
            acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
            direction_trade_2 = "base_to_quote"
            contract_2 = pair_b

            # If b_quote (acquired coin) matches c_base
            if b_quote == c_base:
                swap_3 = c_base
                swap_3_rate = 1 / c_ask
                direction_trade_3 = "base_to_quote"
                contract_3 = pair_c

            # If b_quote (acquired coin) matches c_quote
            if b_quote == c_quote:
                swap_3 = c_quote
                swap_3_rate = c_bid
                direction_trade_3 = "quote_to_base"
                contract_3 = pair_c

            acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
            calculated = 1

    # SCENARIO 3 Check if a_quote (acquired_coin) matches c_quote
    if direction == "forward":
        if a_quote == c_quote and calculated == 0:
            swap_2_rate = c_bid
            acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
            direction_trade_2 = "quote_to_base"
            contract_2 = pair_c

            # If c_base (acquired coin) matches b_base
            if c_base == b_base:
                swap_3 = b_base
                swap_3_rate = 1 / b_ask
                direction_trade_3 = "base_to_quote"
                contract_3 = pair_b

            # If c_base (acquired coin) matches b_quote
            if c_base == b_quote:
                swap_3 = b_quote
                swap_3_rate = b_bid
                direction_trade_3 = "quote_to_base"
                contract_3 = pair_b

            acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
            calculated = 1

    # SCENARIO 4 Check if a_quote (acquired_coin) matches c_base
    if direction == "forward":
        if a_quote == c_base and calculated == 0:
            swap_2_rate = 1 / c_ask
            acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
            direction_trade_2 = "base_to_quote"
            contract_2 = pair_c

            # If c_quote (acquired coin) matches b_base
            if c_quote == b_base:
                swap_3 = b_base
                swap_3_rate = 1 / b_ask
                direction_trade_3 = "base_to_quote"
                contract_3 = pair_b

            # If c_quote (acquired coin) matches b_quote
            if c_quote == b_quote:
                swap_3 = b_quote
                swap_3_rate = b_bid
                direction_trade_3 = "quote_to_base"
                contract_3 = pair_b

            acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
            calculated = 1

    """  REVERSE """
    # SCENARIO 1 Check if a_base (acquired_coin) matches b_quote
    if direction == "reverse":
        if a_base == b_quote and calculated == 0:
            swap_2_rate = b_bid
            acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
            direction_trade_2 = "quote_to_base"
            contract_2 = pair_b

            # If b_base (acquired coin) matches c_base
            if b_base == c_base:
                swap_3 = c_base
                swap_3_rate = 1 / c_ask
                direction_trade_3 = "base_to_quote"
                contract_3 = pair_c

            # If b_base (acquired coin) matches c_quote
            if b_base == c_quote:
                swap_3 = c_quote
                swap_3_rate = c_bid
                direction_trade_3 = "quote_to_base"
                contract_3 = pair_c

            acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
            calculated = 1

    # SCENARIO 2 Check if a_base (acquired_coin) matches b_base
    if direction == "reverse":
        if a_base == b_base and calculated == 0:
            swap_2_rate = 1 / b_ask
            acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
            direction_trade_2 = "base_to_quote"
            contract_2 = pair_b

            # If b_quote (acquired coin) matches c_base
            if b_quote == c_base:
                swap_3 = c_base
                swap_3_rate = 1 / c_ask
                direction_trade_3 = "base_to_quote"
                contract_3 = pair_c

            # If b_quote (acquired coin) matches c_quote
            if b_quote == c_quote:
                swap_3 = c_quote
                swap_3_rate = c_bid
                direction_trade_3 = "quote_to_base"
                contract_3 = pair_c

            acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
            calculated = 1

    # SCENARIO 3 Check if a_base (acquired_coin) matches c_quote
    if direction == "reverse":
        if a_base == c_quote and calculated == 0:
            swap_2_rate = c_bid
            acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
            direction_trade_2 = "quote_to_base"
            contract_2 = pair_c

            # If c_base (acquired coin) matches b_base
            if c_base == b_base:
                swap_3 = b_base
                swap_3_rate = 1 / b_ask
                direction_trade_3 = "base_to_quote"
                contract_3 = pair_b

            # If c_base (acquired coin) matches b_quote
            if c_base == b_quote:
                swap_3 = b_quote
                swap_3_rate = b_bid
                direction_trade_3 = "quote_to_base"
                contract_3 = pair_b

            acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
            calculated = 1

    # SCENARIO 4 Check if a_base (acquired_coin) matches c_base
    if direction == "reverse":
        if a_base == c_base and calculated == 0:
            swap_2_rate = 1 / c_ask
            acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
            direction_trade_2 = "base_to_quote"
            contract_2 = pair_c

            # If c_quote (acquired coin) matches b_base
            if c_quote == b_base:
                swap_3 = b_base
                swap_3_rate = 1 / b_ask
                direction_trade_3 = "base_to_quote"
                contract_3 = pair_b

            # If c_quote (acquired coin) matches b_quote
            if c_quote == b_quote:
                swap_3 = b_quote
                swap_3_rate = b_bid
                direction_trade_3 = "quote_to_base"
                contract_3 = pair_b

            acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
            calculated = 1

        """ PROFIT LOSS OUTPUT """

        # Profit and Loss Calculations
        profit_loss = acquired_coin_t3 - starting_amount
        profit_loss_perc = (profit_loss / starting_amount) * 100 if profit_loss != 0 else 0

        # Trade Descriptions
        trade_description_1 = f"Start with {swap_1} of {starting_amount}. Swap at {swap_1_rate} for {swap_2} acquiring {acquired_coin_t1}."
        trade_description_2 = f"Swap {acquired_coin_t1} of {swap_2} at {swap_2_rate} for {swap_3} acquiring {acquired_coin_t2}."
        trade_description_3 = f"Swap {acquired_coin_t2} of {swap_3} at {swap_3_rate} for {swap_1} acquiring {acquired_coin_t3}."

        # Output Results
        if profit_loss_perc > min_surface_rate:
            surface_dict = {
                "swap_1":swap_1,
                "swap_2":swap_2,
                "swap_3":swap_3,
                "contract_1":contract_1,
                "contract_2":contract_2,
                "contract_3":contract_3,
                "direction_trade_1":direction_trade_1,
                "direction_trade_2":direction_trade_2,
                "direction_trade_3":direction_trade_3,
                "starting_amount":starting_amount,
                "acquired_coin_t1":acquired_coin_t1,
                "acquired_coin_t2":acquired_coin_t2,
                "acquired_coin_t3":acquired_coin_t3,
                "swap_1_rate":swap_1_rate,
                "swap_2_rate":swap_2_rate,
                "swap_3_rate":swap_3_rate,
                "profit_loss":profit_loss,
                "profit_loss_perc":profit_loss_perc,
                "direction":direction,
                "trade_description_1":trade_description_1,
                "trade_description_2":trade_description_2,
                "trade_description_3":trade_description_3
            }
        
        # if profit_loss_perc <min_surface_rate:
        #             surface_dict = {
        #                 "swap_1": swap_1,
        #                 "swap_2": swap_2,
        #                 "swap_3": swap_3,
        #                 "contract_1": contract_1,
        #                 "contract_2": contract_2,
        #                 "contract_3": contract_3,
        #                 "direction_trade_1": direction_trade_1,
        #                 "direction_trade_2": direction_trade_2,
        #                 "direction_trade_3": direction_trade_3,
        #                 "starting_amount": starting_amount,
        #                 "acquired_coin_t1": acquired_coin_t1,
        #                 "acquired_coin_t2": acquired_coin_t2,
        #                 "acquired_coin_t3": acquired_coin_t3,
        #                 "swap_1_rate": swap_1_rate,
        #                 "swap_2_rate": swap_2_rate,
        #                 "swap_3_rate": swap_3_rate,
        #                 "profit_loss": profit_loss,
        #                 "profit_loss_perc": profit_loss_perc,
        #                 "direction": direction,
        #                 "trade_description_1": trade_description_1,
        #                 "trade_description_2": trade_description_2,
        #                 "trade_description_3": trade_description_3
        #             }
        return surface_dict

    return surface_dict 
        
            
#Binance
# symbol="BTCUSDT"
# interval="1d"
# candles=requests.get(f"https://data.binance.com/api/v3/klines?symbol={symbol}&interval={interval}")
# candles_json=[]
# if candles.status_code==200:
#   candles_json=json.loads(candles.text)
#   print(candles_json)
  
  
#   #Structure close prices
# my_candles=[]
# for c in candles_json:
#   my_candles.append(c[4])
# print(my_candles)