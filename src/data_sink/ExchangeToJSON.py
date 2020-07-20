import json
import os
import errno
from time import sleep
from datetime import datetime

from data_sink.DataSink import DataSink


class ExchangeToJSON(DataSink):
    def __init__(self, dir):
        DataSink.__init__(self)
        self.dir = dir
        if not os.path.isdir(dir):
            print('Directory %s does not exist. Attempting to create..' % dir)
            try:
                os.mkdir(dir)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise Exception('Unable to create directory', e)
                pass

    def append_data(self, data):
        super().append_data(data)

    def remove_data(self, data):
        super().remove_data(data)

    def copy_data(self):
        return super().copy_data()

    def parse(self, response_object):
        if '__getitem__' in dir(response_object):
            payload = json.loads(response_object[0].text)['result']
        else:
            payload = json.loads(response_object.text)['result']
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
        try:
            sink_data = self.copy_data()
            filename = str(int(datetime.timestamp(datetime.now()))) + '.json'
            with open(self.dir + filename, 'w') as out:
                json.dump(sink_data, out)
            [self.remove_data(x) for x in sink_data]
        except Exception as e:
            raise (e)
