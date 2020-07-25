import json
import threading as th
from time import sleep

from data_source.ExchangeItem import ExchangeItem
from data_channel.RequestHandler import PostHandler, FetchHandler
from data_channel.RequestRules import RuleManager
from data_sink.ExchangeToJSON import ExchangeToJSON
from objects.Observer import Subscriber
from static.EventType import EventType
from static.Params import NegotiatorParams
from data_channel import TaskManager


class ExchangeManager(TaskManager):
    def __init__(self, data_sink=ExchangeToJSON, total_cycles=10):
        TaskManager.__init__(self)
        self.data_sink = data_sink.__init__()

    def add_topic(self, topic):
        try:
            assert isinstance(topic, ExchangeItem)
            super().add_topic(topic)
        except AssertionError:
            # TODO: Logging at ERROR level
            print('Attempted to add unsupported topic')
            raise

    def remove_topic(self, topic):
        super().remove_topic(topic)

    def add_worker(self, worker):
        try:
            assert isinstance(worker, (PostHandler, FetchHandler))
            super().add_worker(worker)
        except AssertionError:
            # TODO: Logging at ERROR level
            print('Attempted to add unsupported worker')
            raise

    def remove_worker(self, worker):
        super().remove_worker(worker)

    def start(self):
        # Attach each topic to a new worker and subscribe to it
        for topic in self.topics:
            worker = PostHandler(topic, api='exchange')
            worker.subscribe((self, self.rule_manager))
            self.add_worker(worker)

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
