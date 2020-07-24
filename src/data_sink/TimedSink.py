import threading as th
from time import sleep

from data_sink.DataSink import DataSink


class TimedSink(DataSink):
    def __init__(self, base_data_sink, time=30, stop_maximum=3):
        assert isinstance(base_data_sink, DataSink)
        self.__class__ == base_data_sink.__class__
        self.base_data_sink = base_data_sink
        self.time = time
        self.stop_counter = 0
        self.stop_maximum = stop_maximum
        th.Thread(target=self._start_timed_sink).start()

    def append_data(self, data):
        self.base_data_sink.append_data(data)

    def remove_data(self, data):
        self.base_data_sink.remove_data(data)

    def copy_data(self):
        return self.base_data_sink.copy_data()

    def parse(self, response_object):
        self.base_data_sink.parse(response_object)

    def sink(self):
        self.base_data_sink.sink()

    def _start_timed_sink(self):
        while self.stop_counter < self.stop_maximum:
            sleep(self.time)
            data = self.base_data_sink.copy_data()
            if len(data) > 0:
                print('Writing %s items' % len(data), flush=True)
                self.stop_counter = 0
                self.sink()
            else:
                self.stop_counter += 1
                print('No data to sink. Stop counter %s/%s' %
                      (self.stop_counter, self.stop_maximum))
