class TradeItem():
    def __init__(self, league):
        super().__init__()
        self.league = league
        self.json_params = self.generate_json_params()

    def get_league(self):
        return self.league

    def get_json_params(self):
        return self.json_params

    def adjust_json_params(self, *params):
        raise NotImplementedError

    def generate_json_params(self):
        raise NotImplementedError
