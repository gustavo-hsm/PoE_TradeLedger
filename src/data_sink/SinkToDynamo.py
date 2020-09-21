import threading as th
import logging
import sys
import json
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

from data_sink.DataSink import DataSink


class SinkToDynamo(DataSink):
    def __init__(self, table_name, endpoint_url, write_kb_threshold=1):
        DataSink.__init__(self)
        try:
            assert write_kb_threshold > 0 and type(write_kb_threshold) == int
            self.resource = boto3.resource('dynamodb',
                                           endpoint_url=endpoint_url)
            self.table = self.resource.Table(table_name)
            self.write_kb_threshold = 1024 * write_kb_threshold
        except ClientError as e:
            logging.error(e.batch_write_response['Error']['Message'])
        except AssertionError as e:
            logging.warning('Attempted to write an invalid number to '
                            + '"write_kb_threshold". Defaulting to 1 KB.')
            self.write_kb_threshold = 1024

    def append_data(self, data):
        super().append_data(data)
        th.Thread(target=self.automatic_sink).start()

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
            logging.error('Unable to find "result" within text response. ' +
                          'Most likely an incompatible DataSink is being ' +
                          'used to perform this operation')
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
        sink_data = self.copy_data()
        try:
            with self.table.batch_writer() as batch:
                for item in sink_data:
                    batch.put_item(Item=item)
        except ClientError as e:
            logging.error(e.batch_write_response['Error']['Message'])
        else:
            [self.remove_data(x) for x in sink_data]

    def evaluate_write_threshold(self):
        return sys.getsizeof(self.copy_data()) > self.write_kb_threshold

    def automatic_sink(self):
        if self.evaluate_write_threshold:
            logging.debug('write_kb_threshold exceeded. Issuing sink()')
            self.sink()
