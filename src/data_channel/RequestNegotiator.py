import threading as th
from time import sleep

from data_channel.RequestHandler\
     import RequestHandler, PostHandler, FetchHandler, StashHandler
from data_channel.RequestRules import RuleManager
from data_sink.DataSink import DataSink
from data_sink.StashParser import StashParser
from data_sink.ExchangeParser import ExchangeParser
from objects.Observer import Subscriber, Publisher
from static.EventType import EventType
from static.Params import NegotiatorParams


class RequestNegotiator(Subscriber):
    def __init__(self, data_sink, total_cycles=1):
        Subscriber.__init__(self)
        self.data_sink = data_sink
        self.workers = set()
        self.topics = set()
        self.rule_manager = RuleManager()
        self.cycle = 0
        self.total_cycles = total_cycles
        self.lock = th.Lock()
        self.id_changed = None
        self.next_id = None

        if isinstance(self.data_sink, Publisher):
            self.data_sink.subscribe(self)

        if isinstance(self.data_sink, StashParser):
            self.id_changed = True
            self.next_id = self.data_sink.get_id()

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

    def get_topics(self):
        topics = set()
        self.lock.acquire()
        try:
            topics = self.topics.copy()
        finally:
            self.lock.release()
        return topics

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
        return self.cycle < self.total_cycles or\
            len(self.workers) > 0 or\
            self.total_cycles == -1

    def start(self):
        while self.assert_stop_condition():
            # TODO: Logging at DEBUG level
            print('%s worker(s)' % len(self.workers))

            # Generate workers if worker set is empty
            if len(self.workers) == 0:
                self.cycle += 1
                # TODO: Logging at INFO level
                print('Cycle %s/%s' % (self.cycle, self.total_cycles))

                if isinstance(self.data_sink, StashParser) and self.id_changed:
                    self.id_changed = False
                    worker = StashHandler(id=self.next_id)
                    worker.subscribe((self, self.rule_manager))
                    self.add_worker(worker)

                elif isinstance(self.data_sink, ExchangeParser):
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
        publisher = publisher_response['publisher']

        if isinstance(publisher, DataSink):
            # Received response from a DataSink
            if isinstance(publisher, StashParser):
                # Update next change ID
                next_change_id = publisher_response['next_change_id']
                if self.next_id != next_change_id:
                    self.next_id = next_change_id
                    self.id_changed = True

        elif isinstance(publisher, RequestHandler):
            # Received response from a RequestHandler
            event_type = publisher_response['event_type']
            exchange_item = publisher_response['exchange_item']
            response_object = publisher_response['response_object']

            if event_type == EventType.HANDLER_NEXT:
                if response_object is not None and\
                   isinstance(publisher, FetchHandler):
                    th.Thread(target=self.data_sink.parse,
                              args=[response_object]).start()

            elif event_type == EventType.HANDLER_ERROR:
                # TODO: Logging at ERROR level
                print('Something went wrong... %s\n%s' %
                      (publisher, response_object), flush=True)
                self.remove_worker(publisher)

            elif event_type == EventType.HANDLER_FINISHED:
                # TODO: Logging at DEBUG level
                print('Worker is finished - %s' % publisher)

                if response_object is not None:
                    if isinstance(publisher, PostHandler):
                        # Received response from a PostHandler
                        # Use Response text to generate FetchHandlers as needed
                        if response_object.status_code == 200:
                            worker = FetchHandler(exchange_item,
                                                  response_object)
                            worker.subscribe((self, self.rule_manager))
                            self.add_worker(worker)

                    elif isinstance(publisher, (FetchHandler, StashHandler)):
                        # Received response from a FetchHandler or StashHandler
                        # Dispatch the response object to DataSink
                        if response_object.status_code == 200:
                            th.Thread(target=self.data_sink.parse,
                                      args=[response_object]).start()
                self.remove_worker(publisher)
