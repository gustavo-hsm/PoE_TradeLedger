import logging
from threading import Lock

from objects.Sync_decorator import sync
from objects.Observer import Subscriber


class TaskManager(Subscriber):
    lock = Lock()

    def __init__(self):
        Subscriber.__init__(self)
        self.workers = set()
        self.topics = set()
        self.errors = []
        self.target_parsers = set()

    @sync(lock)
    def add_topic(self, topic):
        self.topics.add(topic)

    @sync(lock)
    def remove_topic(self, topic):
        self.topics.remove(topic)

    @sync(lock)
    def add_worker(self, worker):
        self.workers.add(worker)

    @sync(lock)
    def remove_worker(self, worker):
        self.workers.remove(worker)

    @sync(lock)
    def get_workers(self):
        return self.workers.copy()

    @sync(lock)
    def add_error(self, error):
        self.errors.append(error)

    @sync(lock)
    def get_error(self):
        try:
            error = self.errors.pop()
        except IndexError:
            return None
        else:
            return error

    @sync(lock)
    def add_data_parser(self, data_parser):
        self.target_parsers.add(data_parser)

    @sync(lock)
    def remove_data_parser(self, data_parser):
        self.target_parsers.remove(data_parser)

    def command_targets(self, data, action='parse'):
        try:
            assert len(self.target_parsers) > 0
            for target in self.target_parsers:
                if action == 'parse':
                    assert data is not None
                    target.parse(data)
                elif action == 'dispatch':
                    target.dispatch()
        except AssertionError:
            logging.error('Unable to complete request because ' +
                          'there are no targets OR no data was supplied')

    def has_pending_workers(self):
        return len(self.workers) > 0

    def has_pending_errors(self):
        return len(self.errors) > 0

    def start(self):
        raise NotImplementedError

    def end(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError
