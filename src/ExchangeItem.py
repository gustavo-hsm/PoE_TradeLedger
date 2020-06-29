from Observer import Subscriber


class ExchangeItem(Subscriber):

    def __init__(self, want, have, league='harvest', minimum_stock=0):

        # Additional params
        self.league = league
        self.minimum_stock = minimum_stock
        self.want = []

        if type(want) == str:
            self.want.append(want)
        else:
            self.want = list(want)

        self.have = []
        if type(have) == str:
            self.have.append(have)
        else:
            self.have = list(have)

        # HTTP POST Params
        self.json_params = self._generate_exchange_params()

    def get_league(self):
        return self.league

    def get_json_params(self):
        return self.json_params

    def raise_minimum_stock(self, factor=2):
        self.minimum_stock = self.minimum_stock * factor or factor
        self.json_params = self._generate_exchange_params()

    def _generate_exchange_params(self):
        params = {
            'exchange': {
                'status': {
                    'option': 'any'
                },
                'want': [x for x in self.want],
                'have': [x for x in self.have],
            }
        }

        if self.minimum_stock:
            params['exchange']['minimum'] = self.minimum_stock

        return params

    def update(self, *args):
        has_stock_args = None
        for arg in args:
            has_stock_args = 'raise_minimum_stock' in arg
            if has_stock_args:
                self.raise_minimum_stock()
