import logging
from time import time
from threading import Lock

from objects.Sync_decorator import sync


class Queue():
    lock = Lock()

    def __init__(self):
        self.queue = []
        self.processed = []

    @sync(lock)
    def add(self, item):
        self.queue.append(item)

    @sync(lock)
    def retrieve(self, size=1):
        items = self.queue[:size]
        self.processed.extend(items)
        del self.queue[:size]
        return items

    # TODO
    def health_check(self):
        pass

    @sync(lock)
    def get_queue_size(self):
        return len(self.queue)

    @sync(lock)
    def get_processed_size(self):
        return len(self.processed)

    def describe(self):
        queue_size = self.get_queue_size()
        processed_size = self.get_processed_size()
        message = 'Objects pooled: %s\nObjects processed: %s'\
            % (queue_size, processed_size)
        message += '\n-----------------------'
        message += '\nList of pooled objects'
        message += '\n-----------------------\n'
        message += '\n'.join(map(str, self.queue))
        print(message)
