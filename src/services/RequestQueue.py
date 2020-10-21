import logging

from nameko.rpc import rpc, RpcProxy

from services.Queue import Queue


class RequestQueue():
    name = 'request_queue'
    queue = Queue()

    @rpc
    def add_to_queue(self, item):
        try:
            self.queue.add(item)
        except Exception as e:
            self.dead_letter_queue.add({'Error': e})
            raise

    @rpc
    def retrieve_next_item(self):
        return self.queue.retrieve(size=1)

    @rpc
    def describe(self):
        return self.queue.describe()


class RequestQueueService():
    name = 'service'
    service = RpcProxy('request_queue')

    @rpc
    def add_to_queue(self, item):
        try:
            self.service.add_to_queue.call_async(item)
        except Exception as e:
            return 400
        else:
            return 200

    @rpc
    def describe(self):
        try:
            self.service.describe.call_async()
        except Exception as e:
            return 400
        else:
            return 200

    @rpc
    def retrieve(self):
        next_item = None
        try:
            next_item = self.service.retrieve_next_item()
        finally:
            return next_item
