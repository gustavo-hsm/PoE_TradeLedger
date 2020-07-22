import json
import os
import errno
from datetime import datetime

from data_sink.DataSink import DataSink


class SinkToJSON(DataSink):
    def __init__(self, dir):
        DataSink.__init__(self)
        self.dir = dir
        if not os.path.isdir(dir):
            print('Directory %s does not exist. Attempting to create..' % dir)
            try:
                os.mkdir(dir)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise Exception('Unable to create directory', e)
                pass

    def append_data(self, data):
        super().append_data(data)

    def remove_data(self, data):
        super().append_data(data)

    def copy_data(self):
        return super().copy_data()

    def parse(self):
        raise NotImplementedError

    def sink(self):
        try:
            sink_data = self.copy_data()
            filename = str(int(datetime.timestamp(datetime.now()))) + '.json'
            with open(self.dir + filename, 'w') as out:
                json.dump(sink_data, out)
            [self.remove_data(x) for x in sink_data]
        except Exception as e:
            raise (e)
