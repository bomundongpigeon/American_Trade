import requests
import json
import datetime
from pytz import timezone
import time
import yaml
import pandas as pd

with open('config.yaml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)
APP_KEY = _cfg['APP_KEY']
APP_SECRET = _cfg['APP_SECRET']
ACCESS_TOKEN = ""
CANO = _cfg['CANO']
ACNT_PRDT_CD = _cfg['ACNT_PRDT_CD']
DISCORD_WEBHOOK_URL = _cfg['DISCORD_WEBHOOK_URL']
URL_BASE = _cfg['URL_BASE']

class turtle_trade:
    def __init__(self):
        self.QQQ_trade_signal = 'hold'
        self.SOXX_trade_signal = 'hold'
        price_ref_check = None
        self.QQQ_ATR = None
        self.SOXX_ATR = None
        stock = ['QQQ','SOXX']
        while True:

            t_now = datetime.datetime.now(timezone('America/New_York'))  # 뉴욕 기준 현재 시간
            t_9 = t_now.replace(hour=9, minute=30, second=0, microsecond=0)
            t_start = t_now.replace(hour=9, minute=35, second=0, microsecond=0)
            t_sell = t_now.replace(hour=15, minute=45, second=0, microsecond=0)
            t_exit = t_now.replace(hour=15, minute=50, second=0, microsecond=0)
            today = t_now.weekday()

            if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
                send_message("주말이므로 프로그램을 종료합니다.")
                break

            elif t_9 < t_now < t_exit:
                send_message("자동매매를 시작합니다.")
                self.stock_dict, self.stock_dollor, self.stock_profit = get_stock_balance()
                self.cash = get_balance()
                self.dollor_rate = get_exchange_rate()
                self.dollor = self.cash / self.dollor_rate
                self.total_dollor = self.dollor + self.stock_dollor
                time.sleep(0.1)
                if self.QQQ_trade_signal == 'what': ### 수정 필요 ###
                    send_message("오늘은 그만")
                    break
                else:
                    for i in stock:
                        print(i)
                        if self.price_ref_check(i) == None:
                            self.QQQ_ATR, self.QQQ_20day_high_price, self.QQQ_20day_low_price, self.SOXX_ATR, self.SOXX_20day_high_price, self.SOXX_20day_low_price = self.market_stock_select()
                            time.sleep(0.1)
                        else:
                            if i == 'QQQ' and self.QQQ_trade_signal != 'sell':
                                self.QQQ_cur_price = get_current_price('NAS','QQQ')
                                QQQ_current_status = QQQ_check(self.stock_dict)
                                time.sleep(0.1)

                                if QQQ_current_status == 'long' and (self.QQQ_trade_signal == 'hold' or 'buy'):
                                    self.TQQQ_cur_price_table = get_old_price('NAS', 'TQQQ')
                                    self.TQQQ_cur_price = get_current_price('NAS', 'TQQQ')
                                    self.TQQQ_ATR = ATR_calculate(self.TQQQ_cur_price_table)
                                    send_message("TQQQ ATR : ", self.TQQQ_ATR)
                                    time.sleep(0.1)
                                    if self.QQQ_cur_price < self.QQQ_20day_high_price - 2 * self.QQQ_ATR:
                                        self.TQQQ_cur_qty = self.stock_dict['TQQQ']
                                        self.TQQQ_cur_price_table = get_old_price('NAS', 'TQQQ')
                                        self.TQQQ_cur_price = get_current_price('NAS', 'TQQQ')
                                        self.TQQQ_ATR = ATR_calculate(self.TQQQ_cur_price_table)

                                        self.TQQQ_sell_price = self.TQQQ_cur_price - 2 * self.TQQQ_ATR
                                        sell('NASD', 'TQQQ', self.TQQQ_cur_qty, self.TQQQ_sell_price)
                                        self.QQQ_trade_signal = 'sell'

                                    elif self.TQQQ_cur_price > get_stock_price('TQQQ') + 2.8 * self.TQQQ_ATR and self.trade_signal != 'sell':
                                        self.TQQQ_cur_price = get_current_price('NAS', 'TQQQ')
                                        self.TQQQ_sell_price = self.TQQQ_cur_price
                                        self.cur_qty = self.stock_dict['TQQQ']
                                        sell('NASD', 'TQQQ', self.cur_qty, self.sell_price)
                                        self.QQQ_trade_signal = 'sell'

                                elif QQQ_current_status == 'short' and (self.QQQ_trade_signal == 'hold' or 'buy'):
                                    self.SQQQ_cur_price_table = get_old_price('NAS', 'SQQQ')
                                    self.SQQQ_cur_price = get_current_price('NAS', 'SQQQ')
                                    self.SQQQ_ATR = ATR_calculate(self.SQQQ_cur_price_table)
                                    send_message("SQQQ ATR : ", self.SQQQ_ATR)
                                    if self.QQQ_cur_price > self.QQQ_20day_low_price + 2 * self.QQQ_ATR:
                                        self.SQQQ_cur_qty = self.stock_dict['SQQQ']
                                        self.SQQQ_cur_price_table = get_old_price('NAS', 'SQQQ')
                                        self.SQQQ_cur_price = get_current_price('NAS', 'SQQQ')
                                        self.SQQQ_ATR = ATR_calculate(self.SQQQ_cur_price_table)
                                        self.SQQQ_sell_price = self.SQQQ_cur_price - 2 * self.SQQQ_ATR
                                        sell('NASD', 'SQQQ', self.SQQQ_cur_qty, self.SQQQ_sell_price)
                                        self.QQQ_trade_signal = 'sell'

                                    elif self.SQQQ_cur_price > (get_stock_price('SQQQ') + 2.8 * self.SQQQ_ATR) and self.trade_signal != 'sell':
                                        self.SQQQ_cur_price = get_current_price('NAS', 'SQQQ')
                                        self.SQQQ_sell_price = self.SQQQ_cur_price
                                        self.SQQQ_cur_qty = self.stock_dict['SQQQ']
                                        sell('NASD', 'SQQQ', self.SQQQ_cur_qty, self.SQQQ_sell_price)
                                        self.QQQ_trade_signal = 'sell'

                                elif QQQ_current_status == 'hold' and self.QQQ_trade_signal == 'hold':

                                    if self.turtle_signal_1() == 'long' or self.turtle_signal_2() == 'long':
                                        send_message('QQQ_turtle signal : long')
                                        self.TQQQ_cur_price_table = get_old_price('NAS', 'TQQQ')
                                        self.TQQQ_cur_price = get_current_price('NAS', 'TQQQ')
                                        self.TQQQ_ATR = ATR_calculate(self.TQQQ_cur_price_table)
                                        self.TQQQ_unit = unit_calculate(self.total_dollor, self.TQQQ_ATR)
                                        buy('NASD', 'TQQQ', self.TQQQ_unit, self.TQQQ_cur_price + 2 * self.TQQQ_ATR)
                                        self.trade_signal = 'buy'
                                    elif self.turtle_signal_1() == 'short' or self.turtle_signal_2() == 'short':
                                        send_message('QQQ_turtle signal : short')
                                        self.SQQQ_cur_price_table = get_old_price('NAS', 'SQQQ')
                                        self.SQQQ_cur_price = get_current_price('NAS', 'SQQQ')
                                        self.SQQQ_ATR = ATR_calculate(self.SQQQ_cur_price_table)
                                        self.SQQQ_unit = unit_calculate(self.total_dollor, self.SQQQ_ATR)
                                        buy('NASD', 'SQQQ', self.SQQQ_unit, self.SQQQ_cur_price + 2 * self.SQQQ_ATR)
                                        self.trade_signal = 'buy'
                                    else:
                                        send_message('turtle signal : hold')

                            elif i == 'SOXX' and self.SOXX_trade_signal != 'sell':
                                self.SOXX_cur_price = get_current_price('NAS','SOXX')
                                SOXX_current_status = SOXX_check(self.stock_dict)

                                if SOXX_current_status == 'long' and (self.SOXX_trade_signal == 'hold' or 'buy'):
                                    self.SOXL_cur_qty = self.stock_dict['SOXL']
                                    self.SOXL_cur_price_table = get_old_price('AMS', 'SOXL')
                                    self.SOXL_cur_price = get_current_price('AMS', 'SOXL')
                                    self.SOXL_ATR = ATR_calculate(self.SOXL_cur_price_table)
                                    send_message("SOXL ATR : ", self.SOXL_ATR)
                                    if self.SOXX_cur_price < self.SOXX_20day_high_price - 2 * self.SOXX_ATR:
                                        self.SOXL_sell_price = self.SOXL_cur_price - 2 * self.SOXL_ATR
                                        sell('AMEX','SOXL',self.SOXL_cur_qty,self.SOXL_sell_price)
                                        self.SOXX_trade_signal = 'sell'
                                    elif self.SOXL_cur_price > (get_stock_price('SOXL') + 2.8 * self.SOXL_ATR) and self.SOXX_trade_signal != 'sell':
                                        self.SOXL_sell_price = self.SOXL_cur_price
                                        sell('AMEX', 'SOXL', self.SOXL_cur_qty, self.SOXL_sell_price)
                                        self.SOXX_trade_signal = 'sell'

                                elif SOXX_current_status == 'short' and (self.SOXX_trade_signal == 'hold' or 'buy'):
                                    self.SOXS_cur_price = get_current_price('AMS', 'SOXS')
                                    self.SOXS_cur_price_table = get_old_price('AMS', 'SOXS')
                                    self.SOXS_ATR = ATR_calculate(self.SOXS_cur_price_table)
                                    send_message("SOXS ATR : ",self.SOXS_ATR)
                                    if self.SOXX_cur_price > self.SOXX_20day_low_price + 2 * self.SOXX_ATR:
                                        self.SOXS_cur_qty = self.stock_dict['SOXS']
                                        self.SOXS_cur_price = get_current_price('AMS', 'SOXS')
                                        self.SOXS_ATR = ATR_calculate(self.SOXS_cur_price_table)
                                        self.SOXS_sell_price = self.SOXS_cur_price - 2 * self.SOXS_ATR
                                        sell('NASD', 'SOXS', self.SOXS_cur_qty, self.SOXS_sell_price)
                                        self.SOXX_trade_signal = 'sell'

                                    elif self.SOXS_cur_price > get_stock_price('SOXS') + 2.8 * self.SOXS_ATR and self.SOXX_trade_signal != 'sell':
                                        self.SOXS_cur_price = get_current_price('AMS', 'SOXS')
                                        self.SOXS_sell_price = self.SOXS_cur_price
                                        self.SOXS_cur_qty = self.stock_dict['SOXS']
                                        sell('AMEX', 'SOXS', self.SOXS_cur_qty, self.SOXS_sell_price)
                                        self.SOXX_trade_signal = 'sell'

                                elif SOXX_current_status == 'hold' and self.SOXX_trade_signal == 'hold':

                                    if self.turtle_signal_1('SOXX') == 'long' or self.turtle_signal_2('SOXX') == 'long':
                                        send_message('SOXX_turtle signal : long')
                                        self.SOXL_cur_price_table = get_old_price('AMS', 'SOXL')
                                        self.SOXL_cur_price = get_current_price('AMS', 'SOXL')
                                        self.SOXL_ATR = ATR_calculate(self.SOXL_cur_price_table)
                                        self.SOXL_unit = unit_calculate(self.total_dollor, self.SOXL_ATR)
                                        buy('AMEX', 'SOXL', self.SOXL_unit, self.SOXL_cur_price + 2 * self.SOXL_ATR)
                                        self.SOXX_trade_signal = 'buy'

                                    elif self.turtle_signal_1('SOXX') == 'short' or self.turtle_signal_2('SOXX') == 'short':
                                        send_message('SOXX_turtle signal : short')
                                        self.SOXS_cur_price_table = get_old_price('AMS', 'SOXS')
                                        self.SOXS_cur_price = get_current_price('AMS', 'SOXS')
                                        self.SOXS_ATR = ATR_calculate(self.SOXS_cur_price_table)
                                        self.SOXS_unit = unit_calculate(self.total_dollor, self.SOXS_ATR)
                                        buy('AMEX', 'SOXS', self.SOXS_unit, self.SOXS_cur_price + 2 * self.SOXS_ATR)
                                        self.SOXX_trade_signal = 'buy'


    def stock_price_ref(self,market,stock):
        ref_price_table = get_old_price(market,stock)
        ref_ATR = ATR_calculate(ref_price_table)
        ref_twenty_day_high_price = ref_price_table.iloc[-21:-1, :]['high'].max()
        ref_twenty_day_low_price = ref_price_table.iloc[-21:-1, :]['low'].min()

        return ref_ATR, ref_twenty_day_high_price, ref_twenty_day_low_price

    def market_stock_select(self):
        self.QQQ_ATR, self.QQQ_20day_high_price, self.QQQ_20day_low_price = self.stock_price_ref('NAS','QQQ')
        self.SOXX_ATR, self.SOXX_20day_high_price, self.SOXX_20day_low_price = self.stock_price_ref('NAS','SOXX')

        return self.QQQ_ATR, self.QQQ_20day_high_price, self.QQQ_20day_low_price, self.SOXX_ATR, self.SOXX_20day_high_price, self.SOXX_20day_low_price

    def price_ref_check(self,stock):
        if stock == 'QQQ':
            if self.QQQ_ATR is None:
                return None
            else:
                return 'QQQ_OK'
        if stock == 'SOXX':
            if self.SOXX_ATR is None:
                return None
            else:
                return 'SOXX_OK'

    def turtle_signal_1(self,code='QQQ'):
        cur_price = get_current_price('NAS', code)
        price_table = get_old_price('NAS', code)
        twenty_day_high_price = price_table.iloc[-21:-1,:]['high'].max()
        twenty_day_low_price = price_table.iloc[-21:-1,:]['low'].min()

        print(code, cur_price, twenty_day_high_price, twenty_day_low_price)

        if cur_price >= twenty_day_high_price:
            return "long"
        elif cur_price <= twenty_day_low_price:
            return "short"
        else:
            return "hold"

    def turtle_signal_2(self,code='QQQ'):
        cur_price = get_current_price('NAS', code)
        price_table = get_old_price('NAS', code)
        fifty_five_day_high_price = price_table.iloc[-56:-1,:]['high'].max()
        fifty_five_day_low_price = price_table.iloc[-56:-1,:]['low'].min()

        if cur_price >= fifty_five_day_high_price:
            return "long"
        elif cur_price <= fifty_five_day_low_price:
            return "short"
        else:
            return "hold"

    def status_check(self,long_code,short_code):
        if stock_check(long_code):
            current_status = 'long'
        elif stock_check(short_code):
            current_status = 'short'
        else:
            current_status = 'hold'
        return current_status

    def long_clearing(self,market, code='QQQ'):

        twenty_day_high_price = self.ref_price_table.iloc[:,-21:-2]['high'].max()
        current_price = get_current_price(market, code)

        if current_price < twenty_day_high_price - 2 * self.ref_ATR:
            return 'sell'
        else:
            return 'hold'




def send_message(msg):
    """디스코드 메세지 전송"""
    now = datetime.datetime.now()
    message = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {str(msg)}"}
    requests.post(DISCORD_WEBHOOK_URL, data=message)
    print(message)

def hashkey(datas):
    """암호화"""
    PATH = "uapi/hashkey"
    URL = f"{URL_BASE}/{PATH}"
    headers = {
    'content-Type' : 'application/json',
    'appKey' : APP_KEY,
    'appSecret' : APP_SECRET,
    }
    res = requests.post(URL, headers=headers, data=json.dumps(datas))
    hashkey = res.json()["HASH"]
    return hashkey

def get_access_token():
    """토큰 발급"""
    headers = {"content-type":"application/json"}
    body = {"grant_type":"client_credentials",
    "appkey":APP_KEY,
    "appsecret":APP_SECRET}
    PATH = "oauth2/tokenP"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    ACCESS_TOKEN = res.json()["access_token"]
    return ACCESS_TOKEN

def get_old_price(market,code):
    """기간별 가격 조회"""
    PATH = "uapi/overseas-price/v1/quotations/dailyprice"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json",
            "authorization": f"Bearer {ACCESS_TOKEN}",
            "appKey":APP_KEY,
            "appSecret":APP_SECRET,
            "tr_id":"HHDFS76240000"}
    params = {
        "AUTH": "",
        "EXCD":market,
        "SYMB":code,
        "GUBN":0,
        "MODP":1,
        "BYMD": ""
    }

    res = requests.get(URL, headers=headers, params=params)
    price_table = pd.DataFrame(res.json()['output2'])
    price_table = price_table.astype({'clos':'float','high':'float','low':'float'})
    price_table = price_table.sort_values(by=['xymd'],ascending=True)
    return price_table

def get_current_price(market="NAS", code="QQQ"):
    """현재가 조회"""
    PATH = "uapi/overseas-price/v1/quotations/price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json",
            "authorization": f"Bearer {ACCESS_TOKEN}",
            "appKey":APP_KEY,
            "appSecret":APP_SECRET,
            "tr_id":"HHDFS00000300"}
    params = {
        "AUTH": "",
        "EXCD":market,
        "SYMB":code
    }
    res = requests.get(URL, headers=headers, params=params)
    return float(res.json()['output']['last'])

def ATR_calculate(price_table):
    price_table['TR_A'] = price_table['high'] - price_table['clos'].shift()
    price_table['TR_B'] = price_table['clos'].shift() - price_table['low']
    price_table['TR_C'] = price_table['high'] - price_table['low']
    price_table['TR'] = price_table[['TR_A','TR_B','TR_C']].max(axis=1)

    price_table['ATR'] = price_table['TR'].rolling(window=20).mean()
    price_table['EMA'] = (price_table['ATR'].shift()*19 + price_table['TR']*2)/21

    # print(price_table[['clos','high','low','TR_A','TR_B','TR_C','TR','ATR','EMA']])
    EMA = float(price_table.iloc[-2:-1,:]['EMA'])

    return EMA

def get_balance():
    """현금 잔고조회"""
    PATH = "uapi/domestic-stock/v1/trading/inquire-psbl-order"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json",
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"TTTC8908R",
        "custtype":"P",
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": "005930",
        "ORD_UNPR": "65500",
        "ORD_DVSN": "01",
        "CMA_EVLU_AMT_ICLD_YN": "Y",
        "OVRS_ICLD_YN": "Y"
    }
    res = requests.get(URL, headers=headers, params=params)
    cash = float(res.json()['output']['ord_psbl_cash']) + float(res.json()['output']['ord_psbl_frcr_amt_wcrc'])
    return int(cash)

def get_exchange_rate():
    """환율 조회"""
    PATH = "uapi/overseas-stock/v1/trading/inquire-present-balance"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json",
            "authorization": f"Bearer {ACCESS_TOKEN}",
            "appKey":APP_KEY,
            "appSecret":APP_SECRET,
            "tr_id":"CTRP6504R"}
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "OVRS_EXCG_CD": "NASD",
        "WCRC_FRCR_DVSN_CD": "01",
        "NATN_CD": "840",
        "TR_MKET_CD": "01",
        "INQR_DVSN_CD": "00"
    }
    res = requests.get(URL, headers=headers, params=params)
    exchange_rate = 1270.0
    if len(res.json()['output2']) > 0:
        exchange_rate = float(res.json()['output2'][0]['frst_bltn_exrt'])
    return exchange_rate

def unit_calculate(dollor,ATR):
    one_percent_dollor = dollor * 0.01
    print('1% cash : ', one_percent_dollor)
    unit = round(one_percent_dollor / ATR)

    return unit

def get_stock_balance():
    """주식 잔고조회"""
    PATH = "uapi/overseas-stock/v1/trading/inquire-balance"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json",
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"JTTT3012R",
        "custtype":"P"
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "OVRS_EXCG_CD": "NASD",
        "TR_CRCY_CD": "USD",
        "CTX_AREA_FK200": "",
        "CTX_AREA_NK200": ""
    }
    res = requests.get(URL, headers=headers, params=params)
    stock_list = res.json()['output1']
    evaluation = res.json()['output2']
    stock_dict = {}
    send_message(f"====주식 보유잔고====")
    for stock in stock_list:
        if int(stock['ovrs_cblc_qty']) > 0:
            stock_dict[stock['ovrs_pdno']] = stock['ovrs_cblc_qty']
            send_message(f"{stock['ovrs_item_name']}({stock['ovrs_pdno']}): {stock['ovrs_cblc_qty']}주")
            time.sleep(0.1)
    send_message(f"주식 평가 금액: ${evaluation['tot_evlu_pfls_amt']}")
    stock_dollor = float(evaluation['tot_evlu_pfls_amt'])
    time.sleep(0.1)
    send_message(f"평가 손익 합계: ${evaluation['ovrs_tot_pfls']}")
    stock_profit = float(evaluation['tot_pftrt'])
    time.sleep(0.1)
    send_message(f"=================")
    return stock_dict, stock_dollor, stock_profit

def get_stock_price(stock_name):
    """주식 잔고조회"""
    PATH = "uapi/overseas-stock/v1/trading/inquire-balance"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json",
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"JTTT3012R",
        "custtype":"P"
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "OVRS_EXCG_CD": "NASD",
        "TR_CRCY_CD": "USD",
        "CTX_AREA_FK200": "",
        "CTX_AREA_NK200": ""
    }
    res = requests.get(URL, headers=headers, params=params)
    stock_list = res.json()['output1']
    evaluation = res.json()['output2']
    stock_dict = {}
    send_message(f"====주식 보유잔고====")
    for stock in stock_list:
        if int(stock['ovrs_cblc_qty']) > 0:
            stock_dict[stock['ovrs_pdno']] = stock['ovrs_cblc_qty']
            send_message(f"{stock['ovrs_item_name']}({stock['ovrs_pdno']}): {stock['ovrs_cblc_qty']}주")
            time.sleep(0.1)
            if stock['ovrs_pdno'] == stock_name:
                send_message("stock_name : ", stock_name)
                stock_buy_price = stock['pchs_avg_pric']
                send_message("storck_buy_price : ", stock_buy_price)
                return float(stock_buy_price)


def buy(market="NASD", code="TQQQ", qty="1", price="0"):
    """미국 주식 지정가 매수"""
    PATH = "uapi/overseas-stock/v1/trading/order"
    URL = f"{URL_BASE}/{PATH}"
    data = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "OVRS_EXCG_CD": market,
        "PDNO": code,
        "ORD_DVSN": "00",
        "ORD_QTY": str(int(qty)),
        "OVRS_ORD_UNPR": f"{round(price,2)}",
        "ORD_SVR_DVSN_CD": "0"
    }
    headers = {"Content-Type":"application/json",
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"JTTT1002U",
        "custtype":"P",
        "hashkey" : hashkey(data)
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    if res.json()['rt_cd'] == '0':
        send_message(f"[매수 성공]{str(res.json())}")
        return True
    else:
        send_message(f"[매수 실패]{str(res.json())}")
        return False

def sell(market="NASD", code="AAPL", qty="1", price="0"):
    """미국 주식 지정가 매도"""
    PATH = "uapi/overseas-stock/v1/trading/order"
    URL = f"{URL_BASE}/{PATH}"
    data = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "OVRS_EXCG_CD": market,
        "PDNO": code,
        "ORD_DVSN": "00",
        "ORD_QTY": str(int(qty)),
        "OVRS_ORD_UNPR": f"{round(price,2)}",
        "ORD_SVR_DVSN_CD": "0"
    }
    headers = {"Content-Type":"application/json",
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"JTTT1006U",
        "custtype":"P",
        "hashkey" : hashkey(data)
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    if res.json()['rt_cd'] == '0':
        send_message(f"[매도 성공]{str(res.json())}")
        return True
    else:
        send_message(f"[매도 실패]{str(res.json())}")
        return False

def stock_check(stock_dict,code):
    if stock_dict=={}:
        print("No stock")
    else:
        for sym in stock_dict.keys():
            if code == sym:
                return True

def QQQ_check(stock_dict):
    if stock_check(stock_dict,'TQQQ'):
        current_status = 'long'
    elif stock_check(stock_dict,'SQQQ'):
        current_status = 'short'
    else:
        current_status = 'hold'
    return current_status

def SOXX_check(stock_dict):
    if stock_check(stock_dict,'SOXL'):
        current_status = 'long'
    elif stock_check(stock_dict,'SOXS'):
        current_status = 'short'
    else:
        current_status = 'hold'
    return current_status


try:
    ACCESS_TOKEN = get_access_token()
    trade_start = turtle_trade()
except:
    time.sleep(5)
    ACCESS_TOKEN = get_access_token()
    trade_start = turtle_trade()