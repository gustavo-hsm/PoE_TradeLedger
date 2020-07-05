class Publisher():
    def __init__(self):
        self.subscribers = set()

    def publish(self, *args):
        for sub in self.subscribers:
            sub.update(args)

    def subscribe(self, subscriber):
        self.subscribers.add(subscriber)

    def unsubscribe(self, subscriber):
        self.subscribers.remove(subscriber)


class Subscriber():
    def __init__(self):
        update_state = None

    def update(self, *args):
        raise NotImplementedError
