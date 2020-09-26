import json
import logging
from datetime import datetime

from data_parser.DataParser import DataParser


class ExchangeParser(DataParser):
    def __init__(self, target=None):
        super().__init__(target=target)

    def dispatch(self):
        super().dispatch()

    def parse(self, data):
        try:
            if '__getitem__' in dir(data):
                payload = json.loads(data[0].text)['result']
            else:
                payload = json.loads(data.text)['result']
        except KeyError:
            logging.error('Unable to find "result" within text response. ' +
                          'Most likely an incompatible DataParse is being ' +
                          'used to perform this operation')
            raise

        response_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        for item in payload:
            try:
                trade_register = {
                    'offer_id': item['id'],
                    'trade_league': item['item']['league'],
                    'buying_currency': None,
                    'buying_price': None,
                    'offer_currency': item['item']['typeLine'],
                    'offer_amount': 1,
                    'offer_total_stock': item['item']['stackSize'],
                    'acc_user': item['listing']['account']['name'],
                    'acc_user_online': item['listing']
                    ['account']['online'] is not None,
                    'indexed_time': item['listing']['indexed'],
                    'processed_time': response_time,
                }

                if item['listing'] is not None:
                    if item['listing']['price'] is not None:
                        trade_register['buying_currency'] = item['listing'][
                            'price']['currency']
                        trade_register['buying_price'] = round(item['listing'][
                            'price']['amount'])
            except (TypeError, AttributeError):
                logging.error('Unable to parse this register:\n%s' % item)
                continue
            else:
                super().append_data(trade_register)
        self.dispatch()
