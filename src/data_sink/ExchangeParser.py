import json
from datetime import datetime

from data_sink.SinkToJSON import SinkToJSON


class ExchangeParser(SinkToJSON):
    def __init__(self, dir):
        SinkToJSON.__init__(self, dir)

    def append_data(self, data):
        super().append_data(data)

    def remove_data(self, data):
        super().remove_data(data)

    def copy_data(self):
        return super().copy_data()

    def parse(self, response_object):
        try:
            if '__getitem__' in dir(response_object):
                payload = json.loads(response_object[0].text)['result']
            else:
                payload = json.loads(response_object.text)['result']
        except KeyError:
            print('Unable to find "result" within text response. ' +
                  'Most likely an incompatible DataSink is being used ' +
                  'to perform this operation', flush=True)
            raise

        response_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        for item in payload:
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
                trade_register['buying_currency'] = item['listing'][
                    'price']['currency']
                trade_register['buying_price'] = item['listing'][
                    'price']['amount']
            self.append_data(trade_register)

    def sink(self):
        super().sink()
