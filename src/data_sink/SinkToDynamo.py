import logging
import threading as th
from sys import getsizeof
from time import sleep

import boto3
from botocore.exceptions import ClientError

from data_sink.DataSink import DataSink
from objects.Sync_decorator import sync


class SinkToDynamo(DataSink):
    lock = th.Lock()

    def __init__(self, table_name, endpoint_url, put_request_delay=0):
        DataSink.__init__(self)
        try:
            self.resource = boto3.resource('dynamodb',
                                           endpoint_url=endpoint_url)
            self.table = self.resource.Table(table_name)
            self.buffer_size = self.table.provisioned_throughput[
                'WriteCapacityUnits'] * 1024
            self.staging_buffer = []
            self.put_request_delay = put_request_delay
            self.allow_buffer_override = False
            self.sink_thread = th.Thread()
        except ClientError as e:
            logging.error(e)
            raise

    def set_buffer_override(self, buffer_override):
        try:
            assert type(buffer_override) is bool
            self.allow_buffer_override = buffer_override
        except AssertionError:
            logging.warning('Incompatible value: Expected %s, received %s' %
                            (bool, type(buffer_override)))
        finally:
            logging.info('Buffer override is: %s' % self.allow_buffer_override)

    def reset_buffer_size(self):
        self.buffer_size = self.table.provisioned_throughput[
                'WriteCapacityUnits'] * 1024

    def sink(self, data):
        try:
            self.staging_buffer.append(data)
            if not self.sink_thread.isAlive():
                self.sink_thread = th.Thread(target=self.dispatch_to_dynamodb)
                self.sink_thread.start()
        except RuntimeError as e:
            logging.error('Unable to start a new thread: %s' % e)
            raise
        finally:
            return super().SINK_SUCCESSFUL

    def split_data_into_batches(self, data):
        flat_data = list(self.flatten_object(data))
        total_size = sum(map(getsizeof, flat_data))
        dataset = []

        if total_size > self.buffer_size:
            batch = []
            current_batch_size = 0
            for item in flat_data:
                item_size = getsizeof(item)
                if item_size > self.buffer_size:
                    logging.warning(
                        'Item size (%s) exceeds table Write Capacity (%s)' %
                        (item_size, self.buffer_size))
                    if self.allow_buffer_override:
                        logging.warning(
                            'Buffer Override is set to True. ' +
                            'Item will be sent to DynamoDB.')
                        dataset.append(item)
                    else:
                        logging.warning(
                            'Buffer Override is set to False. ' +
                            'Item will be discarded.')
                elif (self.buffer_size - current_batch_size - item_size) > 0:
                    current_batch_size += item_size
                    batch.append(item)
                else:
                    dataset.append(batch)
                    current_batch_size = item_size
                    batch = []
                    batch.append(item)
            if len(batch) > 0:
                dataset.append(batch)
        else:
            # Given data fits entirely into the table Write Capacity
            return flat_data
        return dataset

    def flatten_object(self, data):
        for item in data:
            if '__getitem__' in dir(item) and not isinstance(item, (
                                                            str, bytes, dict)):
                yield from self.flatten_object(item)
            else:
                yield item

    @sync(lock)
    def dispatch_to_dynamodb(self):
        try:
            assert len(self.staging_buffer) > 0
            dataset = self.staging_buffer.copy()
            print('Dataset size: %s' % len(dataset))
            flat_data = self.split_data_into_batches(dataset)
            with self.table.batch_writer() as batch_writer:
                for batch in flat_data:
                    for item in batch:
                        batch_writer.put_item(Item=item)
                        sleep(self.put_request_delay)
        except ClientError as e:
            logging.error('%s\n%s' % (e, flat_data))
        except AssertionError:
            logging.warning('Unable to sink onto DynamoDB: No data to send')
        else:
            logging.info('Successfully dispatched %s items' % len(flat_data))
            [self.staging_buffer.remove(x) for x in dataset]
