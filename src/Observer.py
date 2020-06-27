class Publisher():
    def __init__(self):
        self.subscribers = set()
        self.subscribers_response = None

    def publish(self):
        for sub in self.subscribers:
            sub.update(self.subscribers_response)

    def subscribe(self, subscriber):
        self.subscribers.add(subscriber)

    def unsubscribe(self, subscriber):
        self.subscribers.remove(subscriber)


class Subscriber():
    def __init__(self):
        update_state = None

    def update(self, subscribers_response):
        raise NotImplementedError
