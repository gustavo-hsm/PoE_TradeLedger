import threading as th


class DataSink():
    def __init__(self):
        self.data = []
        self.lock = th.Lock()

    def append_data(self, data):
        self.lock.acquire()
        try:
            self.data.append(data)
        finally:
            self.lock.release()

    def remove_data(self, data):
        self.lock.acquire()
        try:
            self.data.remove(data)
        finally:
            self.lock.release()

    def copy_data(self):
        data = []
        self.lock.acquire()
        try:
            data = self.data.copy()
        finally:
            self.lock.release()
        return data

    def parse(self):
        raise NotImplementedError

    def sink(self):
        raise NotImplementedError
