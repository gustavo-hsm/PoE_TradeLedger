from ExchangeItem import ExchangeItem
from RequestHandler import PostHandler, GetHandler

from json import dump
from datetime import datetime
from time import sleep


def stop_condition():
    return True


def collect_data(poster, getter, ExchangeItem):
    print(ExchangeItem.json_params)
    # Ensure all entities are subscribed to one another
    poster.subscribe(getter)
    getter.subscribe(ExchangeItem)

    # Send and process requests
    poster.send_request()
    getter.send_request()


league = 'harvest'

# Topics to track
exalt_to_mirror = ExchangeItem(want='mir', have='exalt')
chaos_to_exalt = ExchangeItem(want='exalt', have='chaos')
chaos_to_common = ExchangeItem(want=['alt', 'fuse', 'ancient_orb'],
                               have='chaos')
common_to_common = ExchangeItem(want=['fuse', 'ancient_orb'],
                                have=['chaos', 'alt'])

# Request Handlers
chaos_to_exalt_poster = PostHandler(chaos_to_exalt, league)
chaos_to_exalt_getter = GetHandler(chaos_to_exalt, league)


while stop_condition():
    collect_data(chaos_to_exalt_poster, chaos_to_exalt_getter, chaos_to_exalt)

    # Wait 2 minutes before trying again
    print('Processing is done. Waiting...')
    sleep(45)
