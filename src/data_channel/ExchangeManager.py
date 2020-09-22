import logging
import threading as th

from data_source.ExchangeItem import ExchangeItem
from data_channel.RequestHandler import PostHandler, FetchHandler
from data_channel.RequestRules import RuleManager
from data_channel.TaskManager import TaskManager
from data_parser.ExchangeParser import ExchangeParser
from static.EventType import EventType
from objects.Observer import Publisher


class ExchangeManager(TaskManager):
    def __init__(self):
        TaskManager.__init__(self)
        self.rule_manager = RuleManager.get_instance()

    def add_data_parser(self, data_parser):
        try:
            assert isinstance(data_parser, ExchangeParser)
            if isinstance(data_parser, Publisher):
                data_parser.subscribe(self)
            super().add_data_parser(data_parser)
        except AssertionError:
            logging.error('Attempted to add unsupported parser')
            raise

    def remove_data_parser(self, data_parser):
        if isinstance(data_parser, Publisher):
            data_parser.unsubscribe(self)
        try:
            super().remove_data_parser(data_parser)
        except ValueError:
            logging.warning('Parser %s is not on the list' % data_parser)
            pass

    def add_topic(self, topic):
        try:
            assert isinstance(topic, ExchangeItem)
            super().add_topic(topic)
        except AssertionError:
            logging.error('Attempted to add unsupported topic')
            raise

    def remove_topic(self, topic):
        super().remove_topic(topic)

    def add_worker(self, worker):
        try:
            assert isinstance(worker, (PostHandler, FetchHandler))
            super().add_worker(worker)
        except AssertionError:
            logging.error('Attempted to add unsupported worker')
            raise

    def remove_worker(self, worker):
        super().remove_worker(worker)

    def get_workers(self):
        return super().get_workers()

    def has_pending_workers(self):
        return super().has_pending_workers()

    def add_error(self, error):
        super().add_error(error)

    def has_pending_errors(self):
        return super().has_pending_errors()

    def command_targets(self, data, action='parse'):
        super().command_targets(data, action=action)

    def start(self):
        # Attach each topic to a new worker and subscribe to it
        for topic in self.topics:
            worker = PostHandler(topic, api='exchange')
            worker.subscribe((self, self.rule_manager))
            self.add_worker(worker)

    def end(self):
        # End was invoked
        # Kill remaining workers and sink remaining data
        logging.debug('Ending TaskManager %s ' % self)
        [self.remove_worker(worker) for worker in self.get_workers()]
        self.command_targets(None, action='dispatch')

    def update(self, *args):
        publisher_response = super().flatten_args(args)
        logging.debug(publisher_response)

        publisher = publisher_response['publisher']
        event_type = publisher_response['event_type']
        exchange_item = publisher_response['exchange_item']
        response_object = publisher_response['response_object']
        request_error = publisher_response['request_error']

        if event_type == EventType.HANDLER_NEXT:
            if response_object is not None and\
               isinstance(publisher, FetchHandler):
                th.Thread(target=self.command_targets,
                          args=[response_object, 'parse']).start()

        elif event_type == EventType.HANDLER_ERROR:
            logging.error('Something went wrong... %s\n%s' %
                          (publisher, response_object))
            self.add_error(request_error)
            self.remove_worker(publisher)

        elif event_type == EventType.HANDLER_FINISHED:
            logging.debug('Worker is finished - %s' % publisher)

            if response_object is not None:
                if isinstance(publisher, PostHandler):
                    # Use Response text to generate FetchHandlers
                    worker = FetchHandler(exchange_item, response_object)
                    worker.subscribe((self, self.rule_manager))
                    self.add_worker(worker)

                elif isinstance(publisher, FetchHandler):
                    # Dispatch the response object to Parse targets
                    th.Thread(target=self.command_targets,
                              args=[response_object, 'parse']).start()
            self.remove_worker(publisher)
