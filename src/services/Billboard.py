class Billboard():
    def __init__(self):
        self.topics = []
        self.active_workers = []

    def attach_topic(self, topic):
        self.topics.append(topic)
        return topic

    def detach_topic(self, index: int):
        try:
            return self.topics.pop(index)
        except ValueError as e:
            return ('Expected an Integer index, Received %s\n%s' % (index, e))

    def get_topic_by_index(self, index: int):
        try:
            return self.topics[index]
        except ValueError as e:
            return ('Expected an Integer index, Received %s\n%s' % (index, e))

    def get_all_topics(self):
        return self.topics

    def get_all_active_workers(self):
        return self.active_workers

    def retrieve_topic(self, worker):
        topic = None
        if len(self.topics) > 0:
            topic = self.topics.pop(0)
            self.active_workers.append([worker, topic])
        return topic
