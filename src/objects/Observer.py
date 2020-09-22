import logging


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
        try:
            if '__getitem__' in dir(subscriber):
                [self.subscribers.remove(sub) for sub in subscriber]
            else:
                self.subscribers.remove(subscriber)
        except ValueError:
            logging.warning('Cannot unsubscribe %s because ' +
                            'it is not a subscriber' % subscriber)
            pass


class Subscriber():
    def __init__(self):
        update_state = None

    def update(self, *args):
        raise NotImplementedError

    # TODO: "Unnest" args coming from publishers. It should come in
    # as a single tuple instead of a huge nested tuple
    def flatten_args(self, args):
        if type(args) is tuple:
            return self.flatten_args(args[0])
        else:
            return args
