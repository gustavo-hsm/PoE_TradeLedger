import logging

from data_source.ExchangeItem import ExchangeItem
from data_channel.RequestNegotiator import RequestNegotiator
from data_channel.ExchangeManager import ExchangeManager
from data_sink.TimedExchangeParser import TimedExchangeParser

topics = []
logging.basicConfig(filename='logs/main.log', filemode='a', level=logging.INFO)

# Sample Data sources
chaos_to_exalt = ExchangeItem(want='exalted', have='chaos', league='heist')
exalt_to_chaos = ExchangeItem(want='chaos', have='exalted', league='heist')

chaos_to_ancient = ExchangeItem(want='ancient-orb', have='chaos',
                                league='heist')
ancient_to_chaos = ExchangeItem(want='chaos', have='ancient-orb',
                                league='heist')

# Data sink
exchange_to_json = TimedExchangeParser(dir='output/heist/',
                                       prefix='CurrencyWatch',
                                       time=180)

# Data channel
exchange_manager = ExchangeManager(data_sink=exchange_to_json)

# Attach sources to channel
exchange_manager.add_topic(chaos_to_exalt)
exchange_manager.add_topic(exalt_to_chaos)
exchange_manager.add_topic(chaos_to_ancient)
exchange_manager.add_topic(ancient_to_chaos)

# Negotiator to manage Data Channels
negotiator = RequestNegotiator(total_cycles=10)

# Attach managers to negotiator
negotiator.add_manager(exchange_manager)

# Start
negotiator.start()
