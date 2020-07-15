from time import time
from Observer import Subscriber


class RuleManager(Subscriber):
    def __init__(self):
        self.rules = set()
        # Initializing this manager with a custom rule
        self.add_rule(RequestRule(duration=30, maximum_requests=6))

    def add_rule(self, rule):
        self.rules.add(rule)

    def expire_rules(self):
        rules = self.rules.copy()
        for rule in rules:
            if rule.expire_rule():
                self.rules.remove(rule)

    def authorize(self):
        # Remove expired rules before evaluating authorization
        self.expire_rules()

        # Evaluate all rules
        can_request = [rule.allow_request() for rule in self.rules]
        print('Rules: %s - Results: %s' % (len(self.rules), can_request))
        # Deny request if any of these rules return False
        return False not in can_request

    def increment_request_counter(self):
        [rule.add_current_requests() for rule in self.rules]

    def update(self, *args):
        publisher_response = self._flatten_args(args)
        if publisher_response['response_object'] is not None:
            headers = dict(publisher_response['response_object'].
                           headers._store)
            try:
                base_rules = headers['x-rate-limit-ip'][-1].split(',')
                current_state = headers['x-rate-limit-ip-state'][-1].split(',')
                for rule, state in zip(base_rules, current_state):
                    # 12:6:60 -  Maximum of 12 requests within 6 seconds.
                    # 60 seconds of timeout if threshold is exceeded.
                    rule_info = rule.split(':')

                    # 1:6:0 - Where we are at. 1 request has been made within
                    # 6 seconds. Therefore, it takes 0 seconds of timeout
                    state_info = state.split(':')

                    # Ensure both objects refers to the same rule
                    assert rule_info[1] == state_info[1]

                    current_state = int(state_info[0])
                    maximum_requests = int(rule_info[0])
                    duration = int(rule_info[1])
                    self.add_rule(RequestRule(duration, maximum_requests,
                                  current_state=current_state))

            except (IndexError, KeyError, AssertionError) as e:
                print('Error atempting to parse HTTP headers.'
                      + 'Creating a Custom Rule instead')
                self.add_rule(RequestRule(duration=60, maximum_requests=3))
                raise Exception(e)

    # TODO: "Unnest" args coming from publishers. It should come in
    # as a single tuple instead of a huge nested tuple
    def _flatten_args(self, args):
        if type(args) is tuple:
            return self._flatten_args(args[0])
        else:
            return args


class RequestRule():
    def __init__(self, duration, maximum_requests, current_state=0):
        self.rule_duration = time() + duration
        self.current_state = current_state
        self.maximum_requests = maximum_requests

    def allow_request(self):
        # Requests can only be authorized while
        return self.current_state < self.maximum_requests

    def add_current_requests(self):
        self.current_state = self.current_state + 1

    def expire_rule(self):
        # Rules can only be expired once their set timer runs out
        return time() > self.rule_duration
