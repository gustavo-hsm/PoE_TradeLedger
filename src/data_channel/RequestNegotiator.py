import json
import threading as th
from time import sleep

from data_channel.RequestHandler import PostHandler, FetchHandler
from data_channel.RequestRules import RuleManager
from objects.Observer import Subscriber
from static.EventType import EventType
from static.Params import NegotiatorParams


class RequestNegotiator(Subscriber):
    def __init__(self, data_sink, total_cycles=10):
        Subscriber.__init__(self)
        self.data_sink = data_sink
        self.workers = set()
        self.topics = set()
        self.rule_manager = RuleManager()
        self.cycle = 0
        self.total_cycles = total_cycles
        self.lock = th.Lock()

    def add_topic(self, exchange_item):
        self.lock.acquire()
        try:
            self.topics.add(exchange_item)
        finally:
            self.lock.release()

    def remove_topic(self, exchange_item):
        self.lock.acquire()
        try:
            self.topics.remove(exchange_item)
        finally:
            self.lock.release()

    def add_worker(self, request_handler):
        self.lock.acquire()
        try:
            self.workers.add(request_handler)
        finally:
            self.lock.release()

    def remove_worker(self, request_handler):
        self.lock.acquire()
        try:
            self.workers.remove(request_handler)
        finally:
            self.lock.release()

    def assert_stop_condition(self):
        sleep(NegotiatorParams.SLEEP_TIMER.value)

        # Allow code to keep running if there are:
        # * Pending cycles to run through
        # OR
        # * Unfinished workers doing their tasks
        return self.cycle < self.total_cycles or len(self.workers) > 0

    def start(self):
        while self.assert_stop_condition():
            # TODO: Logging at DEBUG level
            print('%s worker(s)' % len(self.workers))

            # Generate workers if worker set is empty
            if len(self.workers) == 0:
                self.cycle += 1
                # TODO: Logging at INFO level
                print('Cycle %s/%s' % (self.cycle, self.total_cycles))

                # Attach each topic to a new worker and subscribe to it
                for topic in self.topics:
                    worker = PostHandler(topic, api='exchange')
                    worker.subscribe((self, self.rule_manager))
                    self.add_worker(worker)
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
        publisher_response = super().flatten_args(args)
        # TODO: Logging at DEBUG level
        # print(publisher_response)

        handler = publisher_response['handler']
        event_type = publisher_response['event_type']
        exchange_item = publisher_response['exchange_item']
        response_object = publisher_response['response_object']

        if event_type == EventType.HANDLER_NEXT:
            if response_object is not None and\
               isinstance(handler, FetchHandler):
                th.Thread(target=self.data_sink.parse,
                          args=[response_object]).start()

        elif event_type == EventType.HANDLER_ERROR:
            # TODO: Logging at ERROR level
            print('Something went wrong... %s\n%s' %
                  (handler, response_object), flush=True)
            self.remove_worker(handler)

        elif event_type == EventType.HANDLER_FINISHED:
            # TODO: Logging at DEBUG level
            print('Worker is finished - %s' % handler)

            if response_object is not None:
                if isinstance(handler, PostHandler):
                    # Received response from a PostHandler
                    # Use Response text to generate FetchHandlers as needed
                    if response_object.status_code == 200:
                        worker = FetchHandler(exchange_item, response_object)
                        worker.subscribe((self, self.rule_manager))
                        self.add_worker(worker)

                elif isinstance(handler, FetchHandler):
                    # Received response from a FetchHandler
                    # Dispatch the response object to DataSink
                    if response_object.status_code == 200:
                        th.Thread(target=self.data_sink.parse,
                                  args=[response_object]).start()
            self.remove_worker(handler)
