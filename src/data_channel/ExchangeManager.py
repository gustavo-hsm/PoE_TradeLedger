import threading as th

from data_source.ExchangeItem import ExchangeItem
from data_channel.RequestHandler import PostHandler, FetchHandler
from data_channel.RequestRules import RuleManager
from data_channel.TaskManager import TaskManager
from static.EventType import EventType
from objects.Observer import Publisher


class ExchangeManager(TaskManager):
    def __init__(self, data_sink):
        TaskManager.__init__(self)
        self.data_sink = data_sink
        self.rule_manager = RuleManager.get_instance()

        if isinstance(self.data_sink, Publisher):
            self.data_sink.subscribe(self)

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

    def get_workers(self):
        return super().get_workers()

    def has_pending_workers(self):
        return super().has_pending_workers()

    def start(self):
        # Attach each topic to a new worker and subscribe to it
        for topic in self.topics:
            worker = PostHandler(topic, api='exchange')
            worker.subscribe((self, self.rule_manager))
            self.add_worker(worker)

    def end(self):
        # End was invoked. Kill any remaining workers and sink
        # any remaining data
        # TODO: Logging at DEBUG level
        print('Ending TaskManager', self)
        print('Remaining workers:', len(self.workers))
        [self.remove_worker(worker) for worker in self.get_workers()]
        print('Sinking remaining data')
        self.data_sink.sink()

    def update(self, *args):
        publisher_response = super().flatten_args(args)
        # TODO: Logging at DEBUG level
        # print(publisher_response)

        publisher = publisher_response['publisher']
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
                    # Use Response text to generate FetchHandlers
                    if response_object.status_code == 200:
                        worker = FetchHandler(exchange_item, response_object)
                        worker.subscribe((self, self.rule_manager))
                        self.add_worker(worker)

                elif isinstance(publisher, FetchHandler):
                    # Dispatch the response object to DataSink
                    if response_object.status_code == 200:
                        th.Thread(target=self.data_sink.parse,
                                  args=[response_object]).start()
            self.remove_worker(publisher)
