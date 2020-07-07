import json
import threading as th
from time import sleep

from Observer import Publisher, Subscriber
from ExchangeItem import ExchangeItem
from RequestHandler2 import PostHandler, FetchHandler
from EventType import EventType


class RequestNegotiator(Publisher, Subscriber):
    def __init__(self):
        Publisher.__init__(self)
        Subscriber.__init__(self)
        self.workers = set()
        self.topics = set()
        self.x_rate_rules = set()
        self.queue = []

    def add_topic(self, ExchangeItem):
        self.topics.add(ExchangeItem)

    def remove_topic(self, ExchangeItem):
        self.topics.remove(ExchangeItem)

    def add_worker(self, RequestHandler):
        self.workers.add(RequestHandler)

    def remove_worker(self, RequestHandler):
        print('Removing worker %s' % RequestHandler)
        self.workers.remove(RequestHandler)

    def allow_request(self):
        # TODO
        return True
        # raise NotImplementedError

        if len(x_rate_rules) == 0:
            # No rules have been set yet. Allow request
            return True

        # Evaluate all rules
        rules = set([x.assert_http_rules() for x in x_rate_rules])

        # Deny request if any of these rules return False
        if False in rules:
            return False

        return True

    def assert_http_rules(self):
        # TODO
        pass

    def assert_stop_condition(self):
        sleep(10)
        return True

    def start(self):
        while self.assert_stop_condition():
            print('%s workers - %s queued' %
                  (len(self.workers), len(self.queue)))

            # Check if there are unfinished requests
            if len(self.workers) > 0:
                print('Pending requests. Waiting 30 seconds...')
                sleep(30)
            else:
                # Attach each topic to a poster and subscribe this object
                for topic in self.topics:
                    poster = PostHandler(topic, api='exchange')
                    poster.subscribe(self)
                    self.add_worker(poster)
            self._start_workers()

    def start_worker(self, worker):
        if worker.is_ready_to_start():
            if self.allow_request():
                th.Thread(target=worker.require).start()
            else:
                self.queue.add(worker)

    def _start_workers(self):
        for worker in self.workers:
            self.start_worker(worker)

    def update(self, *args):
        publisher_response = self._flatten_args(args)
        print(publisher_response)

        handler = publisher_response['handler']
        event_type = publisher_response['event_type']
        exchange_item = publisher_response['exchange_item']
        response_object = publisher_response['response_object']

        if event_type == EventType.HANDLER_NEXT:
            if self.allow_request():
                th.Thread(target=handler.require()).start()
            else:
                self.queue.add(handler)

        elif event_type == EventType.HANDLER_ERROR:
            print('Something went wrong... %s\n%s' %
                  (handler, response_object), flush=True)
            self.remove_worker(handler)

        elif event_type == EventType.HANDLER_FINISHED:
            print('Worker is finished - %s' % handler)
            # # Received response from a PostHandler
            # if type(publisher_response['handler']) is PostHandler:
            #     if response_object.status_code == 200:
            #         # Use Response text to generate FetchHandlers as needed
            #         getter = FetchHandler(exchange_item, response_object)
            #         getter.subscribe(self)
            #         self.getters.add(getter)

            # # Received response from a FetchHandler
            # elif type(publisher_response['handler']) is FetchHandler:
            #     pass
            self.remove_worker(handler)

    # TODO: "Unnest" args coming from publishers. It should come in
    # as a single tuple instead of a huge nested tuple
    def _flatten_args(self, args):
        if type(args) is tuple:
            return self._flatten_args(args[0])
        else:
            return args
