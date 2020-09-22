import logging
from threading import Lock

from data_sink.DataSink import DataSink
from objects.Sync_decorator import sync


class DataParser():
    lock = Lock()

    def __init__(self, target=None):
        self.target_list = set()
        self.data = []
        if target:
            self.add_target(target)

    @sync(lock)
    def append_data(self, data):
        self.data.append(data)

    @sync(lock)
    def remove_data(self, data):
        self.data.remove(data)

    @sync(lock)
    def copy_data(self):
        return self.data.copy()

    def add_target(self, target):
        try:
            assert isinstance(target, DataSink)
            self.target_list.add(target)
        except AssertionError:
            logging.warning('Attempted to add an invalid target: %s -> %s' %
                            (target, self))

    def remove_target(self, target):
        try:
            self.target_list.remove(target)
        except ValueError:
            logging.warning('Target "%s" is not on the list' % target)

    def dispatch(self):
        try:
            data = self.copy_data()
            assert len(data) > 0 and len(self.target_list) > 0
            logging.debug('Preparing to dispatch %s items to %s targets' %
                          (len(data), len(self.target_list)))

            for target in self.target_list:
                sink_status = target.sink(data)
                if sink_status is None:
                    logging.warning('No status response from sink target %s. \
                                    Will assume it was successful.' % target)
                elif sink_status > 0:
                    # TODO: Store failed attempts to be tried again later,
                    # preferably using Exponential Backoff
                    logging.warning('Failed to sink data on target %s' %
                                    target)
            [self.remove_data(x) for x in data]
        except AssertionError:
            logging.warning('Unable to dispatch, either because there is ' +
                            'no data to dispatch OR there are no targets')

    def parse(self, data):
        raise NotImplementedError
