from nameko.rpc import rpc, RpcProxy

from services.Billboard import Billboard
from data_source.ExchangeItem import ExchangeItem


class ExchangeBillboard():
    name = 'exchange_billboard'
    billboard = Billboard()

    @rpc
    def attach_topic(self, want, have, league):
        try:
            topic = ExchangeItem(want, have, league)
            response = ExchangeBillboard.billboard.attach_topic(topic)
        except TypeError as e:
            return 400, 'Unable to create topic: %s' % e
        else:
            return 200, 'Successfully attached topic %s' % response

    @rpc
    def detach_topic(self, index):
        try:
            topic = ExchangeBillboard.billboard.detach_topic(index)
        except IndexError:
            return 400, 'Index %s is out of range (0:%s)' %\
                        (index, len(ExchangeBillboard.billboard.topics) - 1)
        else:
            return 200, 'Successfully removed topic %s' % topic

    @rpc
    def display_available_topics(self):
        topics = ExchangeBillboard.billboard.get_all_topics()
        message = '%s Topics found\n' % len(topics)
        for topic in topics:
            message = message + '[%s];Want:%s;Have:%s\n' %\
                (topics.index(topic), topic.want, topic.have)
        return 200, message

    @rpc
    def display_topic_info(self, index):
        try:
            topic = ExchangeBillboard.billboard.get_topic_by_index(index)
            message = topic.get_json_params()
        except IndexError:
            return 400, 'Index %s is out of range (0:%s)' %\
                        (index, len(ExchangeBillboard.billboard.topics) - 1)
        else:
            return 200, message

    @rpc
    def display_workers(self):
        pass
