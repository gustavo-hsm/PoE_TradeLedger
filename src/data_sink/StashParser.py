import json
import threading as th
from datetime import datetime

from data_sink.SinkToJSON import SinkToJSON
from objects.Observer import Publisher


class StashParser(SinkToJSON, Publisher):
    def __init__(self, dir, id=0):
        SinkToJSON.__init__(self, dir)
        Publisher.__init__(self)
        self.id = id

    def append_data(self, data):
        super().append_data(data)

    def remove_data(self, data):
        super().remove_data(data)

    def copy_data(self):
        return super().copy_data()

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def publish(self):
        args = {
            'publisher': self,
            'next_change_id': self.get_id()
        }
        return super().publish(args)

    def parse(self, response_object):
        change_id = self.get_id()
        stashes = None
        try:
            if '__getitem__' in dir(response_object):
                payload = json.loads(response_object[0].text)
            else:
                payload = json.loads(response_object.text)
            # Dispatch ID for the next worker
            self.set_id(payload['next_change_id'])
            stashes = payload['stashes']
            th.Thread(target=self.publish).start()
        except KeyError:
            print('Unable to find "next_change_id" or "stashes" within ' +
                  'text response. Most likely an incompatible DataSink is ' +
                  'being used to perform this operation', flush=True)
            raise

        # TODO: Parse stash data!!
        # Simple Use case I thought about for now:
        # Query which leagues were found on all stashes.
        leagues = set([data['league'] for data in stashes])
        data = {
            'change_id': change_id,
            'stash_count': len(stashes),
            'leagues': list(leagues)
        }
        self.append_data(data)

    def sink(self):
        super().sink()
