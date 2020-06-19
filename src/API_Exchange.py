import API_RequestHandler as rh
import sys
from json import dump
from datetime import datetime

# Sample request: Buying Mirror / Offering Exalts in Standard
# Search for players selling Mirrors
league = 'standard'
exalt_to_mirror = {
    "exchange": {
        "status": {
            "option": "any"
        },
        "want": ['mir'],
        "have": ['exalt']
    }
}

while True:
    handler = rh.RequestHandler(league=league)
    cur_time = datetime.now().strftime('%d-%m-%Y-%H-%M-%S')
    print('[%s] Processing...' % cur_time)

    query_response = handler.query_api('exchange', exalt_to_mirror)
    with open(f'output/{league}/{cur_time}_exalt_to_mirror.json', 'w') as out:
        dump(query_response, out)
    sys.stdout.flush()
