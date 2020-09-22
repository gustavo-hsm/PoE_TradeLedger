import logging
import threading as th
from time import sleep

from data_sink.DataSink import DataSink


class TimedSink(DataSink):
    def __init__(self, target, time=180, stop_maximum=3):
        assert isinstance(target, DataSink)
        super().__init__()
        self.data = []
        self.target = target
        self.time = time
        self.stop_counter = 0
        self.stop_maximum = stop_maximum
        th.Thread(target=self.start_timed_sink).start()

    def sink(self, data):
        self.data.append(data)
        return super().SINK_SUCCESSFUL

    def start_timed_sink(self):
        while self.stop_counter < self.stop_maximum:
            sleep(self.time)
            data = self.data.copy()
            data_count = len(data)
            if data_count > 0:
                logging.info('Writing %s items' % data_count)
                self.stop_counter = 0
                sink_status = self.target.sink(data)

                if sink_status is None:
                    logging.warning('No status response from sink target %s. \
                                    Will assume it was successful.' %
                                    self.target)
                elif sink_status > 0:
                    # TODO: Store failed attempts to be tried again later,
                    # preferably using Exponential Backoff
                    logging.warning('Failed to sink data on target %s' %
                                    self.target)
                    continue
                [self.data.remove(x) for x in data]
            else:
                self.stop_counter += 1
                logging.info('No data to sink. Stop counter %s/%s' %
                             (self.stop_counter, self.stop_maximum))
