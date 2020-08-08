import logging
import threading as th
from time import sleep

from data_channel.RequestHandler\
     import RequestHandler, PostHandler, FetchHandler, StashHandler
from data_channel.TaskManager import TaskManager
from data_channel.RequestRules import RuleManager
from data_sink.DataSink import DataSink
from data_sink.StashParser import StashParser
from data_sink.ExchangeParser import ExchangeParser
from objects.Observer import Subscriber, Publisher
from static.EventType import EventType
from static.Params import NegotiatorParams


class RequestNegotiator():
    def __init__(self, total_cycles=3):
        self.rule_manager = RuleManager.get_instance()
        self.cycle = 0
        self.total_cycles = total_cycles
        self.managers = set()

    def add_manager(self, manager):
        assert isinstance(manager, TaskManager)
        self.managers.add(manager)

    def remove_manager(self, manager):
        self.managers.remove(manager)

    def get_all_workers(self):
        return [manager.get_workers() for manager in self.managers]

    def has_pending_tasks(self):
        return True in [manager.has_pending_workers() for
                        manager in self.managers]

    # TODO: Continue from here
    def has_pending_errors(self):
        return True in [manager.has_pending_errors() for
                        manager in self.managers]

    def command_end_manager(self):
        [manager.end() for manager in self.managers]

    def assert_stop_condition(self):
        sleep(NegotiatorParams.SLEEP_TIMER.value)

        # Allow code to keep running if there are:
        # * Pending cycles to run through
        # OR
        # * Unfinished workers doing their tasks
        return self.cycle < self.total_cycles or\
            self.has_pending_tasks()

    def start(self):
        try:
            assert len(self.managers) > 0
        except AssertionError:
            logging.error(msg='No TaskManagers attached')
            raise

        while self.assert_stop_condition():
            # Cycle workers once if there are no pending tasks
            if not self.has_pending_tasks():
                self.cycle += 1
                self.start_managers()
                logging.info(msg='Cycle %s/%s' %
                                 (self.cycle, self.total_cycles))
            self._launch_tasks()
        logging.debug('Work is finished. Issuing end() command to managers...')
        self.command_end_manager()

    def start_managers(self):
        {manager.start() for manager in self.managers}

    def launch_task(self, task):
        th.Thread(target=task.require).start()
        self.rule_manager.increment_request_counter()

    def _launch_tasks(self):
        for worker in self.get_all_workers():
            for task in worker:
                if task.is_ready_to_start():
                    if self.rule_manager.authorize():
                        self.launch_task(task)
                    else:
                        # Request was denied. Stop asking for authorization
                        break
