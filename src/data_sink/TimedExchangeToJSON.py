import threading as th
from time import sleep

from data_sink.ExchangeToJSON import ExchangeToJSON


class TimedExchangeToJSON(ExchangeToJSON):
    def __init__(self, dir, time=30, stop_maximum=3):
        ExchangeToJSON.__init__(self, dir)
        self.time = time
        self.stop_counter = 0
        self.stop_maximum = stop_maximum
        th.Thread(target=self._start_timed_sink).start()

    def parse(self, response_object):
        super().parse(response_object)

    def sink(self):
        super().sink()

    def _start_timed_sink(self):
        while self.stop_counter < self.stop_maximum:
            sleep(self.time)
            if len(self.data) > 0:
                print('Writing %s items' % len(self.data), flush=True)
                self.stop_counter = 0
                self.sink()
            else:
                self.stop_counter += 1
                print('No data to sink. Stop counter %s/%s' % 
                      (self.stop_counter, self.stop_maximum))
