import logging
import json
import threading as th

from data_parser.DataParser import DataParser
from objects.Observer import Publisher


class StashParser(DataParser, Publisher):
    def __init__(self, target=None, stash_id=0):
        DataParser.__init__(self, target=target)
        Publisher.__init__(self)
        self.stash_id = stash_id

    def set_stash_id(self, id):
        self.stash_id = id

    def get_stash_id(self):
        return self.stash_id

    def publish(self):
        args = {
            'publisher': self,
            'next_change_id': self.get_stash_id()
        }
        return super().publish(args)

    def parse(self, data):
        try:
            current_stash_id = self.get_stash_id()
            stashes = None

            # Read the payload
            if '__getitem__' in dir(data):
                payload = json.loads(data[0].text)
            else:
                payload = json.loads(data.text)

            # Dispatch a signal to require the next stash
            self.set_stash_id(payload['next_change_id'])
            stashes = payload['stashes']
            th.Thread(target=self.publish).start()

        except json.JSONDecodeError as e:
            logging.error('Unable to read the data provided: %s' % e)
            raise

        except KeyError:
            logging.error('Unable to find "next_change_id" or "stashes"' +
                          'within text response. Most likely an incompatible' +
                          ' DataParse is being used to perform this operation')
            raise

        else:
            # TODO: This is a sample usage to count the number of stashes
            # across all leagues involved on this specific stash ID.
            #
            # In the future, this snippet will refer to an abstract function
            # to be overwritten with desired specifications by use-case
            leagues = set([data['league'] for data in stashes])
            data = {
                'change_id': current_stash_id,
                'stash_count': len(stashes),
                'leagues': list(leagues)
            }
            self.append_data(data)
            self.dispatch()
