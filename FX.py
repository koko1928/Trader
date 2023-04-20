import requests
import getpass

# APIキーを入力させる
api_key = getpass.getpass(prompt='Enter your API key: ')

# APIのエンドポイント
endpoint = 'https://api-fxtrade.oanda.com/v3'
account_id = 'YOUR_ACCOUNT_ID'
instrument = 'USD_JPY'

# APIのヘッダー
headers = {
    'Authorization': 'Bearer ' + api_key,
    'Content-Type': 'application/json'
}

# 現在のレートを取得する関数
def get_current_price():
    url = f"{endpoint}/accounts/{account_id}/pricing?instruments={instrument}"
    response = requests.get(url, headers=headers)
    price_data = response.json()['prices'][0]
    return float(price_data['bids'][0]['price']), float(price_data['asks'][0]['price'])

# トレードを実行する関数
def execute_trade(trade_type, units, take_profit, stop_loss):
    url = f"{endpoint}/accounts/{account_id}/orders"
    data = {
        'order': {
            'type': 'MARKET',
            'instrument': instrument,
            'units': f"{trade_type}{units}",
            'timeInForce': 'FOK',
            'positionFill': 'DEFAULT',
            'takeProfitOnFill': {
                'price': f"{take_profit}"
            },
            'stopLossOnFill': {
                'price': f"{stop_loss}"
            }
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 201:
        print(f"Error executing trade: {response.text}")
    else:
        print(f"Trade executed successfully: {response.json()}")

# メイン処理
if __name__ == '__main__':
    # トレードを実行する条件を定義
    take_profit = 110.0  # 利確レート（現在のレートより高い値）
    stop_loss = 100.0  # 損切りレート（現在のレートより低い値）
    
    # 現在のレートを取得
    bid_price, ask_price = get_current_price()
    
    # 取引量を動的に調整する
    balance = 10000  # アカウントの残高
    risk_per_trade = 0.01  # 1トレードあたりのリスク
    max_loss_per_trade = balance * risk_per_trade  # 1トレードあたりの最大損失
    trade_units = int(max_loss_per_trade / abs(bid_price - stop_loss) / 1000) * 1000  # 1000通貨単位で丸める
    
    # 買い注文を実行
    if bid_price >= take_profit:
        execute_trade('BUY', trade_units, take_profit, stop_loss)
    
    # 売り注文を実行
    elif ask_price <= stop_loss:
        execute_trade('SELL', trade_units, take_profit, stop_loss)
