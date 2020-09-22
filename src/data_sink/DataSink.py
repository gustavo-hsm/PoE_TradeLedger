from threading import Lock

from objects.Sync_decorator import sync


# class DataSink():
#     lock = Lock()

#     def __init__(self):
#         self.data = []

#     @sync(lock)
#     def append_data(self, data):
#         self.data.append(data)

#     @sync(lock)
#     def remove_data(self, data):
#         self.data.remove(data)

#     @sync(lock)
#     def copy_data(self):
#         return self.data.copy()

#     def parse(self):
#         raise NotImplementedError

#     def sink(self):
#         raise NotImplementedError


class DataSink():
    SINK_SUCCESSFUL = 0
    SINK_FAILURE = 1

    def __init__(self):
        super().__init__()

    def sink(self, data):
        raise NotImplementedError
