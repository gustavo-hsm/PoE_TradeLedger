import json
import threading as th
from time import sleep

from Observer import Publisher, Subscriber
from ExchangeItem import ExchangeItem
from RequestHandler import PostHandler, FetchHandler
from EventType import EventType
from RequestRules import RuleManager


class RequestNegotiator(Subscriber):
    def __init__(self, total_cycles=10):
        Subscriber.__init__(self)
        self.workers = set()
        self.topics = set()
        self.rule_manager = RuleManager()
        self.cycle = 1
        self.total_cycles = total_cycles

    def add_topic(self, ExchangeItem):
        self.topics.add(ExchangeItem)

    def remove_topic(self, ExchangeItem):
        self.topics.remove(ExchangeItem)

    def add_worker(self, RequestHandler):
        self.workers.add(RequestHandler)

    def remove_worker(self, RequestHandler):
        self.workers.remove(RequestHandler)

    def assert_stop_condition(self):
        # TODO
        sleep(1)
        return self.cycle <= self.total_cycles or len(self.workers) > 0

    def start(self):
        while self.assert_stop_condition():
            print('%s worker(s)' % len(self.workers))

            # Generate posters if worker set is empty
            if len(self.workers) == 0:
                print('Cycle %s/%s' % (self.cycle, self.total_cycles))
                self.cycle = self.cycle + 1
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
        workers = self.workers.copy()

        for worker in workers:
            if worker.is_ready_to_start():
                if self.rule_manager.authorize():
                    self.start_worker(worker)
                else:
                    # Request was denied. Stop asking for authorization
                    break

    def update(self, *args):
        publisher_response = self._flatten_args(args)
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

    # TODO: "Unnest" args coming from publishers. It should come in
    # as a single tuple instead of a huge nested tuple
    def _flatten_args(self, args):
        if type(args) is tuple:
            return self._flatten_args(args[0])
        else:
            return args
