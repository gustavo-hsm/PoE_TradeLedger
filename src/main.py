from ExchangeItem import ExchangeItem
from RequestNegotiator import RequestNegotiator

# Request negotiator
negotiator = RequestNegotiator()

# Topics to track
exalt_to_mirror = ExchangeItem(want='mirror', have='exalted')
high_stock_exalt_to_mirror = ExchangeItem(want='mirror', have='exalted',
                                          minimum_stock=10,
                                          allow_adjust_minimum_stock=False)

# Attach topics
negotiator.add_topic(exalt_to_mirror)
negotiator.add_topic(high_stock_exalt_to_mirror)

# Start
negotiator.start()
