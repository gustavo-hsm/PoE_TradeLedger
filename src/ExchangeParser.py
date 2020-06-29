import json
import sys
from datetime import datetime


def parse_exchange_response(league, response_text):
    payload = json.loads(response_text)['result']
    response_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    results = []

    for item in payload:
        trade_register = {
            'offer_id': item['id'],
            'trade_league': item['item']['league'],
            'buying_currency': None,
            'buying_price': None,
            'offer_currency': item['item']['typeLine'],
            'offer_amount': 1,
            'offer_total_stock': item['item']['stackSize'],
            'acc_user': item['listing']['account']['name'],
            'acc_user_online': item['listing']
            ['account']['online'] is not None,
            'indexed_time': item['listing']['indexed'],
            'processed_time': response_time,
        }

        if item['listing'] is not None:
            trade_register['buying_currency'] = item['listing'][
                'price']['currency']
            trade_register['buying_price'] = item['listing'][
                'price']['amount']
        results.append(trade_register)
    # TODO: Improve file writing by assigning proper names and register count
    write_json(f'output/{league}/{response_time}.json', results)


def write_json(file_dir, content):
    with open(file_dir, 'a') as out:
        json.dump(content, out)
    sys.stdout.flush()
