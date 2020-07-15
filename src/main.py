from ExchangeItem import ExchangeItem
from RequestNegotiator import RequestNegotiator

# Request negotiator
negotiator = RequestNegotiator(total_cycles=5)

# Topics to track
topics = []
exalt_to_mirror = ExchangeItem(want='mirror', have='exalted')
high_stock_exalt_to_mirror = ExchangeItem(want='mirror', have='exalted',
                                          minimum_stock=10,
                                          allow_adjust_minimum_stock=False)
chaos_to_exalt = ExchangeItem(want='exalted', have='chaos')
chaos_to_ancient = ExchangeItem(want='ancient-orb', have='chaos',
                                minimum_stock=16)

# Attach topics
topics.extend([exalt_to_mirror, high_stock_exalt_to_mirror, chaos_to_exalt,
              chaos_to_ancient])
[negotiator.add_topic(topic) for topic in topics]

# Start
negotiator.start()
