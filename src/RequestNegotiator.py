import json
import threading as th
from time import sleep

from Observer import Publisher, Subscriber
from ExchangeItem import ExchangeItem
from RequestHandler2 import PostHandler, FetchHandler


class RequestNegotiator(Publisher, Subscriber):
    def __init__(self):
        Publisher.__init__(self)
        Subscriber.__init__(self)
        self.topics = set()
        self.posters = set()
        self.x_rate_rules = set()

    def add_topic(self, ExchangeItem):
        self.topics.add(ExchangeItem)

    def remove_topic(self, ExchangeItem):
        self.topics.remove(ExchangeItem)

    def allow_request(self):
        raise NotImplementedError

        if len(x_rate_rules) == 0:
            # No rules have been set yet. Allow request
            return True

        # Evaluate all rules
        rules = set([x.assert_http_rules() for x in x_rate_rules])

        # Deny request if any of these rules return False
        if False in rules:
            return False

        return True

    def assert_stop_condition(self):
        return True

    def start(self):
        while self.assert_stop_condition():
            # Check if there are unfinished requests
            print('%s subscribers' % len(self.subscribers))
            if len(self.subscribers) > 0:
                print('Pending requests. Waiting 120 seconds...')
                sleep(120)
            else:
                # Attach each topic to a poster and subscribe this object
                for topic in self.topics:
                    poster = PostHandler(topic, api='exchange')
                    poster.subscribe(self)
                    self.posters.add(poster)

                # Assign a thread to fire each poster
                for poster in self.posters:
                    poster.require()
                    # th.Thread(target=poster.require).start()

                # Posters will publish their response once they're done

    def publish(self, *args):
        super().publish(args)

    def update(self, *args):
        print(args)
