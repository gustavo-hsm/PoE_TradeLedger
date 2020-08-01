import logging
import threading as th
from time import sleep

from data_sink.ExchangeParser import ExchangeParser


class TimedExchangeParser(ExchangeParser):
    def __init__(self, dir, time=30, stop_maximum=3):
        ExchangeParser.__init__(self, dir)
        self.time = time
        self.stop_counter = 0
        self.stop_maximum = stop_maximum
        th.Thread(target=self._start_timed_sink).start()

    def parse(self, response_object):
        super().parse(response_object)

    def sink(self):
        super().sink()

    def copy_data(self):
        return super().copy_data()

    def _start_timed_sink(self):
        while self.stop_counter < self.stop_maximum:
            sleep(self.time)
            data_count = len(self.copy_data())
            if data_count > 0:
                logging.info('Writing %s items' % data_count)
                self.stop_counter = 0
                self.sink()
            else:
                self.stop_counter += 1
                logging.info('No data to sink. Stop counter %s/%s' %
                             (self.stop_counter, self.stop_maximum))
