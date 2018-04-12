# -*- coding: utf-8 -*-
"""
Created on Sun April  8 18:30:05 2018

@author: Chunhui Zhu
"""
import pandas as pd
import  requests
import json 
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")
import time
import numpy as np
import datetime as DT
from pymongo import MongoClient


"""
import asyncio
import websockets
import json
async def test():
    
    async with websockets.connect('wss://ws-feed.gdax.com') as websocket:
        request="{ \"type\": \"subscribe\", \"channels\": [{\"name\": \"ticker\", \"product_ids\": [\"ETH-USD\"]}]}"
        myJSON = JSON.stringify(request)
        await websocket.send(myJSON)
        
        
       
asyncio.get_event_loop().run_until_complete(test())        
 
def build_request():
    return "{ \"type\": \"subscribe\", \"channels\": [{\"name\": \"heartbeat\", \"product_ids\": [\"ETH-USD\"]}]}"

    
asyncio.get_event_loop().run_until_complete(test())


"""

def menu(option):
    print("")
    print("======================================")
    print("                 Menu                 ")
    print("======================================")
    print("             1.  Trade                ")
    print("             2.  Show Blotter         ")
    print("             3.  Show P/L             ")
    print("             4.  Quit                 ")
    print("======================================")
  
    while True:
        try:
             option = int(input("Please enter a number (1-4): "))
             break
        except ValueError:
             print("Wrong input! Try again.")
                 
    while(option<1 or option >4) :
        print("Wrong number! Try again.")
        print("\n")
        option = int(input("Please enter a number (1-4): ")) 
    return(option)
    


#checkticker(symbol)is for checking if symbol is correctly inputed by trader
#Aftet user entry the symbol, lookup its company name form coinmarketcap.com
#return company name which will use in history100day(com)
def checkticker(symbol):
    url="https://api.coinmarketcap.com/v1/ticker/"
    jdata=requests.get(url).json()
    for i in jdata:
        if i["symbol"]==symbol:
            company=i["name"]
            return(company)    


#updatedprice(symbol) will excutive after the trade confirmed
#return an array[ask, bid] to Trade() for order calculation 
def updatedprice(symbol):
        ticker="USDT-"+symbol
        url="https://bittrex.com/api/v1.1/public/getorderbook?market="+ticker+"&type=both"
        jdata=requests.get(url).json()
        data=jdata["result"]["buy"][0]
        askprice=data['Rate']
        
        data=jdata["result"]["sell"][0]
        bidprice=data['Rate']
        
        newprice=[askprice,bidprice]
        return(newprice)

    

#showtrade() will be excutive before the trader confirms the trade
#last 24hr trading data is from bittrex.com
#show basic analytics: average price, max price, min price, variance of price
def showtrade(symbol):
    ticker="USDT-"+symbol
    url="https://bittrex.com/api/v1.1/public/getorderbook?market="+ticker+"&type=both"
    jdata=requests.get(url).json()
    
    buydata=jdata["result"]["buy"]
    dfbuy=pd.DataFrame.from_dict(buydata)
    meanbuy=dfbuy["Rate"].mean()
    maxbuy=max(dfbuy["Rate"])
    minbuy=min(dfbuy["Rate"])
    stdbuy=np.std(dfbuy["Rate"])
    
    selldata=jdata["result"]["sell"]
    dfsell=pd.DataFrame.from_dict(selldata)
    meansell=dfsell["Rate"].mean()
    maxsell=max(dfsell["Rate"])
    minsell=min(dfsell["Rate"])
    stdsell=np.std(dfsell["Rate"])
    
    print("")
    print("----------------------------------------------------------------")
    print(" Bittrex.com: USDT-"+symbol+"       Last 24hr Price: buy/sell   ")
    print("----------------------------------------------------------------")
    print("     Price             Buy                     Sell             ")
    print("----------------------------------------------------------------")
    print("   Average:      "+"{0:.10f}".format(meanbuy)+"         "+"{0:.10f}".format(meansell))
    print("   Max    :      "+"{0:.10f}".format(maxbuy)+"         "+"{0:.10f}".format(maxsell))
    print("   Min    :      "+"{0:.10f}".format(minbuy)+"         "+"{0:.10f}".format(minsell))
    print("   Std    :      "+"{0:.10f}".format(stdbuy)+"           "+"{0:.10f}".format(stdsell))
    print("----------------------------------------------------------------")
    print("")




#history100day(com) will be called from his100chart(company)
#get last 100 days recorded price from coinmarketcap.com
#return panda dataframe his100 with history data
def history100day(com):
    
    #use datatime function to calculate the date before 100 days
    #and store as backdate base on the designed formate
    today=DT.date.today()
    backdate= today-DT.timedelta(days=100)
    formate='%Y%m%d'
    back100date=backdate.strftime(formate)
    today=today.strftime(formate)

    #assign today and back100date to url date range
    #https://coinmarketcap.com/currencies/bitcoin/historical-data/?start=20180305&end=20180404
    url="https://coinmarketcap.com/currencies/"+com+"/historical-data/?start="+back100date+"&end="+today
    soup = BeautifulSoup(requests.get(url, "lxml").content)
    headings=[th.get_text() for th in soup.find("tr").find_all("th")]
    
    hisdata=[]
    for row in soup.find_all("tr")[1:]:
        rowdata = list(td.get_text().replace(",","") for td in row.find_all("td"))
        hisdata.append(rowdata)   

    #stor histroy data in a panda df his100
    #Change the type of datetime and order data by date
    his100=pd.DataFrame(hisdata,columns=headings)
    his100["Date"]=pd.to_datetime(his100["Date"]).dt.date
    his100=his100.sort_values(by='Date')
    cols=his100.columns.drop('Date')
    his100[cols]=his100[cols].apply(pd.to_numeric,errors='ignore')
    return(his100)


#his100chart(company) will excutive after checking trader input is correct 
#get data by calling history100day(com)
#perform data visulatizations for last 100 days trading data
def his100chart(company):
    company=company.lower()
    df100=history100day(company)
    
    import matplotlib.pyplot as plt
    from matplotlib.finance import candlestick2_ohlc

    #show 20 day moving averages
    print("Last 100-day trade history chart")
    
    df100["HMean"]=df100["High"].rolling(20).mean()
    df100["LMean"]=df100["Low"].rolling(20).mean()
    df100.reset_index(inplace=True)
    
    
    fig, ax=plt.subplots()
    plt.xticks(rotation=45)
    plt.xlabel("Last 100 days")
    plt.ylabel("USD Price")
    plt.title(company+"/USD : High and Low 20 day moving averages" )
    
    candlestick2_ohlc(ax, df100["Open"], df100["High"], df100["Low"], df100["Close"], width=1, colorup='g')
    df100.HMean.plot(ax=ax)
    df100.LMean.plot(ax=ax)
    
    plt.show()


#Trade(amount) function excutive following steps of trade:
#checkticker(symbol) will check if input can be found in the trade in coinmarketcap.com
#his100chart(company) show 100-day datachart 
#showtrade(symbol) show basic analytics for decision making 
#if trade decides to trade and enter number of the trade
#updatedprice(symbol) return instant bid/askprice after confirm number of the trade

def Trade(histlist,pllist,amount):
    company=None
    while not company:
        symbol=str(input("Enter a ticker (exmaple: BTC) : "))
        symbol=symbol.upper()
        company=checkticker(symbol)
        if not company:
            print("Ticker not found. ")
            

    his100chart(company)
    showtrade(symbol)
    
    decision=int(input("Do you want to trade (Enter 1:Yes, 0:No.)?  :  ")) 
    if decision==1:
        #The user is then asked to confirm the trade at the market price by enter the quantity.
            while True:
                try:
                     quantity=float(input("Enter number of share(s) (positive for buy/ negative for sell): ")) 
                     break
                except ValueError:
                     print("Wrong input! Try again.")
                     
            if quantity !=0.0 :  
                newprice=updatedprice(symbol)
                if quantity>0.0:
                    cost=newprice[0]*quantity
                    
                    #check if cash account has enought money to buy
                    while(amount<cost):
                        print("Your Account: " + str(amount)+ "   |     Cost : " +str(cost))
                        print("You don't have enought money in your account. ")
                        quantity=float(input("Enter number of share(s) (positive for buy/ negative for sell / 0 back to manu): ")) 
                        #get instant price
                        newprice=updatedprice(symbol)
                        cost=newprice[0]*quantity
                    
                  
                    amount-=cost 
                    order={"Company":company,"Symbol":symbol,"Side":"buy","Volumn":quantity,"Price":newprice[0],"Total Cost":cost,"Time":time.strftime("%c")}
                    print("Total cost :  ",cost)
                    print("Cash Account : ",amount)
                    histlist.append(order)
                    pllist,order=updatePL(pllist,order)
                          
                #if quantity is negative, recorde add as sell stock with bid price
                elif quantity<0.00 :
                    cost= newprice[1] * quantity
                    amount-=cost 
                    order={"Company":company,"Symbol":symbol,"Side":"sell","Volumn":quantity,"Price":newprice[1],"Total Cost":cost,"Time":time.strftime("%c")}
                    print("Total cost :  "+ str(cost))  
                    print("Cash Account : ",amount)
                    histlist.append(order)
                    pllist,order=updatePL(pllist,order)
                    
                    
    return(histlist,pllist,amount)



#when new trade executive, call updataPL(), calculate the profit and loss and update cash amount in account
#each ticker only has maximun 1 recorde in the table  
#Rpl updated only when coins are sold
#Upl is not change
def  updatePL(pllist,order):
    old={}
    #order={"Company","Symbol","Side","Volumn","Price","Total Cost","Time"}
    #plcolname={"Symbol", "Inventory","Wap","Rpl","Upl","Time"}
    for j,i in enumerate(pllist):
        if i["Symbol"]==order["Symbol"]:
            old=pllist[j]
            del pllist[j]    
            
    if len(old)==0:
        new={"Symbol":order["Symbol"],"Inventory":order["Volumn"],"Wap":order["Price"],"Rpl":0.00,"Upl":0.00,"Time":order["Time"] } 
        pllist.append(new) 
    else:
        if order["Volumn"]<0.00 and old["Inventory"]>0.00:
            Rpl=(order["Price"]-old["Wap"])*min(abs(order["Volumn"]),abs(old["Inventory"]))
        
        #if it is short position, buying use ask price 
        elif float(order["Volumn"])>0.00 and float(old["Inventory"])<0.00 :
            Rpl=(old["Wap"]-order["Price"])*min(abs(order["Volumn"]),abs(old["Inventory"]))    
        
        else:
            Rpl=0.0
     
        #For wap (is absolute positive representing a signle price of share of buy and sell:
        inven=float(old["Inventory"])+float(order["Volumn"])
        if( inven!=0.00):
            Wap=(float(old["Wap"])*float(old["Inventory"])+float(order["Price"])*float(order["Volumn"]))/inven    
        else:
            Wap=0.00
            
        new={"Symbol":order["Symbol"], "Inventory":inven,"WAP":Wap,"Rpl":Rpl,"Upl":0.00,"Time":order["Time"]}
        pllist.append(new)
  
    return(pllist,order)



#showPL() undated only when user selction Show P/L .      
#showPL() is to update the unreal profit/loss using updated ask/bid price to est.
#Upl is only data will be changed regarding to exist ticker.
#updateprice() has (tick,askprice,bidprice,time.strftime("%c"))
#pllist has items as in ['Ticker', Inventory, Rpl,Upl,'Time',Wap]
#inventory is negative, to cover short sell, upl use ask price; else use bid price.

def showPL(pllist):

    for i, j in enumerate(pllist): 
        newprice=updatedprice(j["Symbol"])  
        #For long position, upl use bid price

        if j["Inventory"]>0.00 :
            j["Upl"]=(newprice[1]-j["WAP"])*j["Inventory"]
            
        #For short position, upl use ask price; else upl use ask price  
        elif j["Inventory"]<0.00 :
            j["Upl"]=(j["WAP"]-newprice[0])*j["Inventory"]
           
        else: 
            j["Upl"]=0.0
            j["WAP"]=0.0
               
    return(pllist)  
    



#connect with mongodb at the begining, 
#if there are datarows in pl and account in mongodb, 
#recorde pl and account_balance to local variables,  
#drop the pl and account_balance in mongodb. 
#new pl and account_balance will reinstore in mongodb at the end
if __name__=="__main__":
    #creat empty list to storage current training data 
    histlist=[] 
    pllist=[]
    
    cl = MongoClient('localhost', 27017)
    """
    PLMongo.drop()
    AcctMongo.drop()
    HistoryMongo.drop()
    """
    

    
    HistoryMongo= cl["local"]["history"]
    PLMongo= cl["local"]["pl"]
    if PLMongo.count() !=0:
        pllist=list(PLMongo.find()) 
        PLMongo.drop()
    
    AcctMongo= cl["local"]["account"]  #only for recorde the currenct balance 
    if AcctMongo.count() == 0:
        amount=1000000.00
    else:
        account=list(AcctMongo.find()) 
        amount=account[0]["Account_Balance"]
        AcctMongo.drop()
         
    print("Your account balance: ",amount)
    
    option=1 
    
    while option != 4 :  
            option=menu(option)
            
            if (option==1): 
                histlist,pllist,amount=Trade(histlist,pllist,amount)
                print("_________________________________________________")
                #if a new trade excutive, insert the recorde to Mongodb
                if (not histlist)==False:
                    HistoryMongo.insert(histlist)
                    histlist=[]
             
            #Displays the trade blotter, a list of historic trades made by the user. The trade blotter will display
            #the following trade data, with the most recent trade at the top
            elif (option==2):                
                if amount== 1000000.00:
                    print("")
                    print("No trading record.")
                    print("")
                else:    
                    print("")
                    print("======================================")
                    print("            Trading History           ")
                    print("======================================")          
                  
                    histdf = pd.DataFrame(list(HistoryMongo.find()))
                    del histdf["_id"]
                    histdf=histdf[["Company","Symbol","Side","Volumn","Price","Total Cost","Time"]]
                    print(histdf[::-1])   
                print("_________________________________________________")


            #Displays the profit / loss statement. The P/L will display, 
            #the following trade data, with the most recent trade at the top 
            #Ticker, Position, Current Market Price, VWAP, UPL (Unrealized P/L), RPL (Realized P/L)
            
            elif (option==3):
                if not pllist:
                    print("")
                    print("Your do not have trades in your account.")
                    print("")

                else:
                    pllist=showPL(pllist)
                    print("")
                    print("======================================")
                    print("              Profit/Loss             ")
                    print("======================================")
                    PLdf= pd.DataFrame(pllist)                
                    #arrange the column order based on plcolname
                    PLdf=PLdf[["Symbol", "Inventory","WAP","Rpl","Upl","Time"]]
                    print(PLdf[::-1])  
                    
                print("_________________________________________________")   
                    
            #Quit when option==4
            else: 
                AcctMongo.insert({"Account_Balance":amount})
                PLMongo.insert(pllist)
                cl.close()
                print("Good Luck!")
                print("_________________________________________________")
                break;
