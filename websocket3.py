# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 19:12:55 2018

@author: Zhu
"""

import asyncio
import websockets
import json
 
def main():
    asyncio.get_event_loop().run_until_complete(start_gdax_websocket())

async def start_gdax_websocket():
    async with websockets.connect('wss://ws-feed.gdax.com') as websocket:
        await websocket.send(build_request())
        async for m in websocket:
            jdata=json.loads(m)
            if(jdata['type'] in 'ticker' and 'last_size' in jdata and 'side' in jdata):
                print("ProductId: " + jdata['product_id']+" :Best bid is: "+jdata['best_bid']+" : and best ask is: "+jdata['best_ask']+" : Size being offered is: "+jdata['last_size']+" :Side is: "+jdata['side'])

def build_request():
    return "{ \"type\": \"subscribe\",    \"channels\": [{ \"name\": \"ticker\", \"product_ids\": [\"BTC-USD\"] }]}"

if __name__ == "__main__":
    main()
