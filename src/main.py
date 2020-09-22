import logging

from data_source.ExchangeItem import ExchangeItem
from data_channel.RequestNegotiator import RequestNegotiator
from data_channel.ExchangeManager import ExchangeManager
from data_channel.StashManager import StashManager
from data_parser.ExchangeParser import ExchangeParser
from data_parser.StashParser import StashParser
from data_sink.TimedSink import TimedSink
from data_sink.SinkToConsole import SinkToConsole
from data_sink.SinkToLocal import SinkToLocal

topics = []
logging.basicConfig(filename='logs/main.log', filemode='a', level=logging.INFO)

# Sample Data sources
chaos_to_exalt = ExchangeItem(want='exalted', have='chaos', league='heist')
exalt_to_chaos = ExchangeItem(want='chaos', have='exalted', league='heist')

chaos_to_ancient = ExchangeItem(want='ancient-orb', have='chaos',
                                league='heist')
ancient_to_chaos = ExchangeItem(want='chaos', have='ancient-orb',
                                league='heist')

# Data Parser
exchange_parser = ExchangeParser()
stash_parser = StashParser()

# Data Sink
console_display = SinkToConsole()
local_file = SinkToLocal('output/heist/', prefix='SampleExchangeData')
timed_sink_to_local_file = TimedSink(local_file, time=6, stop_maximum=10)

# Data channel
exchange_manager = ExchangeManager()
stash_manager = StashManager()

# Attach sources to channel
exchange_manager.add_topic(chaos_to_exalt)
exchange_manager.add_topic(exalt_to_chaos)
exchange_manager.add_topic(chaos_to_ancient)
exchange_manager.add_topic(ancient_to_chaos)

# Attach parser to channel
exchange_manager.add_data_parser(exchange_parser)
stash_manager.add_data_parser(stash_parser)

# Attach sink to parser
exchange_parser.add_target(timed_sink_to_local_file)
stash_parser.add_target(console_display)

# Negotiator to manage Data Channels
negotiator = RequestNegotiator(total_cycles=2)

# Attach managers to negotiator
negotiator.add_manager(exchange_manager)
negotiator.add_manager(stash_manager)

# Start
negotiator.start()
