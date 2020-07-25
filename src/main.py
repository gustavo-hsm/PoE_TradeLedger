from data_source.ExchangeItem import ExchangeItem
from data_channel.RequestNegotiator import RequestNegotiator
from data_channel.ExchangeManager import ExchangeManager
from data_channel.StashManager import StashManager
from data_sink.TimedExchangeParser import ExchangeParser
from data_sink.StashParser import StashParser

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
exchange_to_json = ExchangeParser(dir='output/harvest/')
stash_to_json = StashParser(dir='output/harvest/public-stash/',
                            id='771388910-784968649-749301602-' +
                            '847797292-808721043')

# Data channel
exchange_manager = ExchangeManager(data_sink=exchange_to_json)
stash_manager = StashManager(data_sink=stash_to_json,
                             init_id=stash_to_json.get_id())

# Attach sources to channel
topics.extend([exalt_to_mirror, high_stock_exalt_to_mirror, chaos_to_exalt,
              chaos_to_ancient])
[exchange_manager.add_topic(topic) for topic in topics]

# Negotiator to manage Data Channels
negotiator = RequestNegotiator(total_cycles=3)

# Attach managers to negotiator
negotiator.add_manager(exchange_manager)
negotiator.add_manager(stash_manager)

# Start
negotiator.start()
