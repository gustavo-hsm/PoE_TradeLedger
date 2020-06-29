from ExchangeItem import ExchangeItem
from RequestHandler import PostHandler, GetHandler

import threading as th
from json import dump
from datetime import datetime
from time import sleep


# TODO: Enable stop conditions, such as:
# Request N times
# Request until datetime
def stop_condition():
    return True


# TODO: Create an specialized class to handle collecting data
def collect_data(*args):
    exchange = args[0]
    league = exchange.get_league()
    while stop_condition():
        # Debug
        print(exchange.json_params)

        # Create handlers
        poster = PostHandler(exchange)
        getter = GetHandler(exchange)

        # Attach subscribers to publishers
        poster.subscribe(getter)
        getter.subscribe(exchange)

        # Run
        poster.send_request()
        getter.send_request()

        # Timeout before running again
        sleep(45)


# * * Sample Requests * *
# Topics to track
exalt_to_mirror = ExchangeItem(want='mir', have='exalt')
chaos_to_exalt = ExchangeItem(want='exalt', have='chaos')
chaos_to_common = ExchangeItem(want=['alt', 'fuse', 'ancient_orb'],
                               have='chaos')
common_to_common = ExchangeItem(want=['fuse', 'ancient_orb'],
                                have=['chaos', 'alt'])

# Assign a new thread for each topic
thread1 = th.Thread(target=collect_data, args=(exalt_to_mirror,))
thread2 = th.Thread(target=collect_data, args=(chaos_to_exalt,))
thread3 = th.Thread(target=collect_data, args=(chaos_to_common,))
thread4 = th.Thread(target=collect_data, args=(common_to_common,))

# Start collecting
thread1.start()
sleep(5)
thread2.start()
sleep(5)
thread3.start()
sleep(5)
thread4.start()
