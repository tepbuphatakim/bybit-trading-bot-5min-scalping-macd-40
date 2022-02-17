import json, config
from flask import Flask, jsonify, request
from pybit import HTTP

app = Flask(__name__)

session = HTTP(config.DEV_URL, api_key=config.API_KEY, api_secret=config.API_SECRET)

def order(side, quantity, symbol, stop_loss, take_profit, order_type="Market"):
    try:
        order = session.place_active_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            qty=quantity,
            time_in_force="GoodTillCancel",
            reduce_only=False,
            close_on_trigger=False,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        return order
    except Exception as e:
        print("Exception Error: " . format(e))
        return str(e)
    

def get_wallet_balance(coin = ""):
    try:
        wallet = session.get_wallet_balance(coin = coin)
        return wallet
    except Exception as e:
        print("Exception Error: " . format(e))
        return str(e)

def set_leverage(symbol, buy_leverage, sell_leverage):
    try:
        leverage = session.set_leverage(
            symbol=symbol,
            buy_leverage=buy_leverage,
            sell_leverage=sell_leverage
        )
        return leverage
    except Exception as e:
        print("Exception Error: " . format(e))
        return str(e)

def cross_isolated_margin_switch(symbol, is_isolated, buy_leverage, sell_leverage):
    try:
        switch = session.cross_isolated_margin_switch(
            symbol=symbol,
            is_isolated=is_isolated,
            buy_leverage=buy_leverage,
            sell_leverage=sell_leverage
        )
        return switch
    except Exception as e:
        print("Exception Error: " . format(e))
        return str(e)

@app.route('/', methods=['GET'])
def welcome():
    return 'Welcome bybit 5 minute scalping MACD 40'

@app.route('/bybit-order', methods=['POST'])
def bybit_order():
    data = json.loads(request.data)
    if data['passpharse'] != config.WEBHOOK_PASSPHRASE:
        return {
            "message": "Invalid passpharse"
        }

    side = data['order_action'].capitalize()
    stop_loss = 0
    take_profit = 0
    usdt_balance = get_wallet_balance('USDT')
    qty = 0

    if usdt_balance:
        qty = usdt_balance['result']['USDT']['available_balance'] / 2 / data['order_price']
    
    if data['order_action'] == 'buy':
        stop_loss = data['order_price'] - (data['order_price'] * 0.01)
        take_profit = data['order_price'] * 1.015
    else:
        stop_loss = data['order_price'] * 1.01
        take_profit = data['order_price'] - (data['order_price'] * 0.015)

    response = order(side, 0.001, data['symbol'], round(stop_loss, 2), round(take_profit, 2))
    return jsonify(response)

@app.route('/wallet-balance', methods=['GET'])
def wallet_balance():
    response = get_wallet_balance(request.args.get("coin"))
    return response

@app.route('/set-leverage', methods=['PUT'])
def set_leverage_route():
    data = json.loads(request.data)
    if data['passpharse'] != config.WEBHOOK_PASSPHRASE:
        return {
            "message": "Invalid passpharse"
        }

    response = set_leverage(data['symbol'], data['buy_leverage'], data['sell_leverage'])
    return {
        "response": response
    }

@app.route('/switch-margin', methods=['PUT'])
def switch_margin():
    data = json.loads(request.data)
    if data['passpharse'] != config.WEBHOOK_PASSPHRASE:
        return {
            "message": "Invalid passpharse"
        }

    response = cross_isolated_margin_switch(data['symbol'], False, data['buy_leverage'], data['sell_leverage'])
    return {
        "response": response
    }