import requests
import json

from objects.Observer import Publisher
from static.EventType import EventType
from static.Params import HandlerParams
# from data_source.TradeItem import TradeItem


class RequestHandler(Publisher):
    def __init__(self, exchange_item):
        # TODO: Assert exchange_item
        # assert isinstance(exchange_item, TradeItem)
        Publisher.__init__(self)
        self.exchange_item = exchange_item
        self.response = None
        self.event_type = None
        self.request_error = None

    def is_ready_to_start(self):
        return self.get_event_type() in (
            EventType.HANDLER_READY, EventType.HANDLER_NEXT)

    def get_exchange_item(self):
        return self.exchange_item

    def get_response(self):
        return self.response

    def get_event_type(self):
        return self.event_type

    def get_request_error(self):
        return self.request_error

    def set_response(self, exchange_item):
        self.exchange_item = exchange_item

    def set_response(self, response):
        self.response = response

    def set_event_type(self, event_type):
        self.event_type = event_type

    def set_request_error(self, request_error):
        self.request_error = request_error

    def publish(self):
        args = {
            'publisher': self,
            'event_type': self.get_event_type(),
            'exchange_item': self.get_exchange_item(),
            'response_object': self.get_response(),
            'request_error': self.get_request_error(),
        }
        super().publish(args)

    def require(self):
        raise NotImplementedError


class PostHandler(RequestHandler):
    def __init__(self, exchange_item, api='exchange'):
        super().__init__(exchange_item)
        self.trade_url = {
            'search': HandlerParams.SEARCH_URL.value + self.exchange_item.
            get_league(),
            'exchange': HandlerParams.EXCHANGE_URL.value + self.exchange_item.
            get_league()
        }.get(api, 'exchange')
        self.set_event_type(EventType.HANDLER_READY)

    def require(self):
        self.set_event_type(EventType.HANDLER_STARTED)
        json_data = self.exchange_item.get_json_params()

        try:
            self.set_response(requests.post(self.trade_url, json=json_data))
            self.set_event_type(EventType.HANDLER_FINISHED)
        except (requests.RequestException, requests.HTTPError) as e:
            self.set_event_type(EventType.HANDLER_ERROR)
            self.set_request_error(e)
        finally:
            self.publish()


class FetchHandler(RequestHandler):
    def __init__(self, exchange_item, response_object):
        super().__init__(exchange_item)
        self.indexed_queries = []
        self.exchange_item = exchange_item
        self.response_object = response_object

        self.batch_size = HandlerParams.MAXIMUM_BATCH_SIZE.value
        self.maximum_result_size = HandlerParams.MAXIMUM_FETCH_SIZE.value
        self.fetch_url = HandlerParams.FETCH_URL.value

        self._parse_response_text()
        self.set_event_type(EventType.HANDLER_READY)

    def require(self):
        self.set_event_type(EventType.HANDLER_STARTED)
        try:
            self.set_response(requests.get(self.indexed_queries.pop(0)))

            # Check if this was the last indexed query to require
            if len(self.indexed_queries) == 0:
                self.set_event_type(EventType.HANDLER_FINISHED)
            else:
                self.set_event_type(EventType.HANDLER_NEXT)
        except (requests.RequestException, requests.HTTPError) as e:
            self.set_event_type(EventType.HANDLER_ERROR)
            self.set_request_error(e)
        except IndexError:
            self.set_event_type(EventType.HANDLER_FINISHED)
            pass
        finally:
            self.publish()

    def _parse_response_text(self):
        payload = json.loads(self.response_object.text)
        query_id = payload['id']
        complexity = payload['complexity']
        result = payload['result']
        items = []

        if len(result) >= self.maximum_result_size:
            self.exchange_item.raise_minimum_stock()

        while len(result) > self.batch_size:
            items.append([result.pop(0) for x in range(0, self.batch_size)])

        if len(result) > 0:
            items.append(result)

        for item in items:
            query = self.fetch_url + ','.join(item) + '?query=' + query_id
            self.indexed_queries.append(query)


class StashHandler(RequestHandler):
    def __init__(self, exchange_item=None, id='0'):
        super().__init__(exchange_item)
        self.id = id
        self.base_url = HandlerParams.STASH_URL.value + '?id=' + str(id)
        self.set_event_type(EventType.HANDLER_READY)

    def require(self):
        self.set_event_type(EventType.HANDLER_STARTED)

        try:
            self.set_response(requests.get(self.base_url))
            self.set_event_type(EventType.HANDLER_FINISHED)
        except (requests.RequestException, requests.HTTPError) as e:
            self.set_event_type(EventType.HANDLER_ERROR)
            self.set_request_error(e)
        finally:
            self.publish()
