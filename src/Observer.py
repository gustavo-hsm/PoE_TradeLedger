class Publisher():
    def __init__(self):
        self.subscribers = set()

    def publish(self, *args):
        for sub in self.subscribers:
            sub.update(args)

    def subscribe(self, subscriber):
        if '__getitem__' in dir(subscriber):
            [self.subscribers.add(sub) for sub in subscriber if
             isinstance(sub, Subscriber)]
        else:
            self.subscribers.add(subscriber)

    def unsubscribe(self, subscriber):
        if '__getitem__' in dir(subscriber):
            [self.subscribers.remove(sub) for sub in subscriber]
        else:
            self.subscribers.remove(subscriber)


class Subscriber():
    def __init__(self):
        update_state = None

    def update(self, *args):
        raise NotImplementedError
