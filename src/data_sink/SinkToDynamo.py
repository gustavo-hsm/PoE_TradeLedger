import threading as th
import logging
import sys
import json
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

from data_sink.DataSink import DataSink


class SinkToDynamo(DataSink):
    def __init__(self, table_name, endpoint_url):
        DataSink.__init__(self)
        try:
            self.resource = boto3.resource('dynamodb',
                                           endpoint_url=endpoint_url)
            self.table = self.resource.Table(table_name)
        except ClientError as e:
            logging.error(e.batch_write_response['Error']['Message'])

    def sink(self, data):
        sink_status = None
        try:
            with self.table.batch_writer() as batch:
                for item in data:
                    batch.put_item(Item=item)
        except ClientError as e:
            logging.error(e.batch_write_response['Error']['Message'])
            sink_status = super().SINK_FAILURE
        else:
            logging.info('Successfully dispatched %s items' % len(data))
            sink_status = super().SINK_SUCCESSFUL
        finally:
            return sink_status
