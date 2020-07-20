from data_source.ExchangeItem import ExchangeItem
from data_channel.RequestNegotiator import RequestNegotiator
from data_sink.TimedExchangeToJSON import TimedExchangeToJSON

topics = []

# Sample Data sources
exalt_to_mirror = ExchangeItem(want='mirror', have='exalted')
high_stock_exalt_to_mirror = ExchangeItem(want='mirror', have='exalted',
                                          minimum_stock=10,
                                          allow_adjust_minimum_stock=False)
chaos_to_exalt = ExchangeItem(want='exalted', have='chaos')
chaos_to_ancient = ExchangeItem(want='ancient-orb', have='chaos',
                                minimum_stock=16)

# Data sink
exchange_to_json = TimedExchangeToJSON(dir='output/harvest/')

# Data channel
negotiator = RequestNegotiator(total_cycles=3, data_sink=exchange_to_json)

# Attach sources to channel
topics.extend([exalt_to_mirror, high_stock_exalt_to_mirror, chaos_to_exalt,
              chaos_to_ancient])
[negotiator.add_topic(topic) for topic in topics]

# Start
negotiator.start()
