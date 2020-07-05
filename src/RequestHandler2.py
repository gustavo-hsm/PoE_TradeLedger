import requests
import json
from Observer import Publisher, Subscriber


class Abs_RequestHandler(Publisher):
    def __init__(self):
        Publisher.__init__(self)

    def require(self):
        raise NotImplementedError

    def publish(self, *args):
        print('Subscriber count: %s ' % len(self.subscribers))
        super().publish(args)


class PostHandler(Abs_RequestHandler):
    def __init__(self, ExchangeItem, api='exchange'):
        super().__init__()
        self.exchange_item = ExchangeItem

        self.base_url = "https://www.pathofexile.com/api/trade/"
        self.trade_url = {
            'search': self.base_url + 'search/' + self.exchange_item.
            get_league(),
            'exchange': self.base_url + 'exchange/' + self.exchange_item.
            get_league()
        }.get(api, 'exchange')

    def publish(self, *args):
        super().publish(args)

    def require(self):
        json_data = self.exchange_item.get_json_params()
        response = None

        try:
            response = requests.post(self.trade_url, json=json_data)
        except requests.RequestException as e:
            raise Exception(e)
        finally:
            self.publish({
                'handler': self,
                'response_object': response
            })


class FetchHandler(Abs_RequestHandler):
    def __init__(self, ExchangeItem, response_object):
        super().__init__()
        self.indexed_queries = []
        self.batch_size = 10
        self.maximum_result_size = 200
        self.base_url = "https://www.pathofexile.com/api/trade/fetch/"
        self.exchange_item = ExchangeItem
        self.response_object = response_object
        self._parse_response_text()

    def publish(self, *args):
        super().publish(args)

    def require(self):
        query_response = []
        for query in self.indexed_queries:
            try:
                response = requests.get(query)
            except requests.RequestException as e:
                raise Exception(e)
            finally:
                query_response.append(response)
        self.publish({
            'handler': self,
            'query_response': query_response
        })

    def _parse_response_text(self):
        payload = json.loads(self.response_object.text)
        query_id = payload['id']
        complexity = payload['complexity']
        result = payload['result']

        if len(result >= len(self.maximum_result_size)):
            self.exchange_item.raise_miminunm_stock()

        items = []
        while len(result) > self.batch_size:
            items.append([result.pop(0) for x in range(0, self.batch_size)])

        if len(result > 0):
            items.append(result)

        for item in items:
            query = self.base_url + ','.join(item) + '?query=' + query_id
            self.indexed_queries.append(query)
