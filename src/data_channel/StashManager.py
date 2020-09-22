import logging
import json
import threading as th
from time import sleep

from data_channel.RequestHandler import StashHandler
from data_channel.RequestRules import RuleManager
from data_channel.TaskManager import TaskManager
from data_parser.StashParser import StashParser
from static.EventType import EventType
from objects.Observer import Publisher


class StashManager(TaskManager):
    def __init__(self, init_id='0'):
        TaskManager.__init__(self)
        self.id = init_id
        self.id_changed = True
        self.next_id = None
        self.rule_manager = RuleManager.get_instance()

    def add_data_parser(self, data_parser):
        try:
            assert isinstance(data_parser, StashParser)
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
        raise NotImplementedError

    def remove_topic(self, topic):
        raise NotImplementedError

    def add_worker(self, worker):
        try:
            assert isinstance(worker, StashHandler)
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

    def update_next_id(self, id):
        if self.id != id:
            self.id = id
            self.id_changed = True
        else:
            logging.info('next_change_id did not change: %s ' % id)
            self.id_changed = False

    def command_targets(self, data, action='parse'):
        super().command_targets(data, action=action)

    def start(self):
        worker = StashHandler(None, id=self.id)
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

        if isinstance(publisher, StashParser):
            self.update_next_id(publisher_response['next_change_id'])

        elif isinstance(publisher, StashHandler):
            event_type = publisher_response['event_type']
            exchange_item = publisher_response['exchange_item']
            response_object = publisher_response['response_object']
            request_error = publisher_response['request_error']

            if event_type == EventType.HANDLER_ERROR:
                logging.error('Something went wrong... %s\n%s' %
                              (publisher, response_object))
                self.add_error(request_error)

            elif event_type == EventType.HANDLER_FINISHED:
                logging.debug('Worker is finished - %s' % publisher)

                # Dispatch the response object to Parse targets
                th.Thread(target=self.command_targets,
                          args=[response_object, 'parse']).start()
            self.remove_worker(publisher)
