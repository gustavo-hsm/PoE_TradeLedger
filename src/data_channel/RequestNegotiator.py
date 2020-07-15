import json
import threading as th
from time import sleep

from data_source.RequestHandler import PostHandler, FetchHandler
from data_channel.RequestRules import RuleManager
from objects.Observer import Subscriber
from static.EventType import EventType


class RequestNegotiator(Subscriber):
    def __init__(self, total_cycles=10):
        Subscriber.__init__(self)
        self.workers = set()
        self.topics = set()
        self.rule_manager = RuleManager()
        self.cycle = 0
        self.total_cycles = total_cycles

    def add_topic(self, exchange_item):
        self.topics.add(exchange_item)

    def remove_topic(self, exchange_item):
        self.topics.remove(exchange_item)

    def add_worker(self, request_handler):
        self.workers.add(request_handler)

    def remove_worker(self, request_handler):
        self.workers.remove(request_handler)

    def assert_stop_condition(self):
        # TODO
        sleep(1)
        return self.cycle < self.total_cycles or len(self.workers) > 0

    def start(self):
        while self.assert_stop_condition():
            print('%s worker(s)' % len(self.workers))

            # Generate posters if worker set is empty
            if len(self.workers) == 0:
                self.cycle = self.cycle + 1
                print('Cycle %s/%s' % (self.cycle, self.total_cycles))
                # Attach each topic to a poster and subscribe this object
                for topic in self.topics:
                    poster = PostHandler(topic, api='exchange')
                    poster.subscribe((self, self.rule_manager))
                    self.add_worker(poster)
            self._start_workers()

    def start_worker(self, worker):
        th.Thread(target=worker.require).start()
        self.rule_manager.increment_request_counter()

    def _start_workers(self):
        for worker in self.workers:
            if worker.is_ready_to_start():
                if self.rule_manager.authorize():
                    self.start_worker(worker)
                else:
                    # Request was denied. Stop asking for authorization
                    break

    def update(self, *args):
        publisher_response = super().flatten_args(args)
        print(publisher_response)

        handler = publisher_response['handler']
        event_type = publisher_response['event_type']
        exchange_item = publisher_response['exchange_item']
        response_object = publisher_response['response_object']

        if event_type == EventType.HANDLER_NEXT:
            self.add_worker(handler)

        elif event_type == EventType.HANDLER_ERROR:
            print('Something went wrong... %s\n%s' %
                  (handler, response_object), flush=True)
            self.remove_worker(handler)

        elif event_type == EventType.HANDLER_FINISHED:
            print('Worker is finished - %s' % handler)
            # Received response from a PostHandler
            if response_object is not None:
                if isinstance(publisher_response['handler'], PostHandler):
                    if response_object.status_code == 200:
                        # Use Response text to generate FetchHandlers as needed
                        getter = FetchHandler(exchange_item, response_object)
                        getter.subscribe((self, self.rule_manager))
                        self.add_worker(getter)
                elif isinstance(publisher_response['handler'], FetchHandler):
                    # TODO: Received response from a FetchHandler
                    # Dispatch the response to ExchangeParser
                    if response_object.status_code == 200:
                        print(event_type, response_object)
            self.remove_worker(handler)
