import threading as th

from objects.Observer import Subscriber


class TaskManager(Subscriber):
    def __init__(self):
        Subscriber.__init__(self)
        self.workers = set()
        self.topics = set()
        self.lock = th.Lock()

    def add_topic(self, topic):
        self.lock.acquire()
        try:
            self.topics.add(topic)
        finally:
            self.lock.release()

    def remove_topic(self, topic):
        self.lock.acquire()
        try:
            self.topics.remove(topic)
        finally:
            self.lock.release()

    def add_worker(self, worker):
        self.lock.acquire()
        try:
            self.workers.add(worker)
        finally:
            self.lock.release()

    def remove_worker(self, worker):
        self.lock.acquire()
        try:
            self.workers.remove(worker)
        finally:
            self.lock.release()

    def get_workers(self):
        self.lock.acquire()
        workers = None
        try:
            workers = self.workers.copy()
        finally:
            self.lock.release()
        return workers

    def has_pending_workers(self):
        return len(self.workers) > 0

    def start(self):
        raise NotImplementedError

    def end(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError
