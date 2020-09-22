import logging
import json
import os
import errno
from datetime import datetime

from data_sink.DataSink import DataSink


class SinkToLocal(DataSink):
    def __init__(self, dir, prefix=None, write_function=json.dump):
        DataSink.__init__(self)
        self.dir = dir
        self.prefix = prefix
        self.write_function = write_function
        if not os.path.isdir(dir):
            logging.warning('Directory %s does not exist. ' +
                            'Attempting to create.' % dir)
            try:
                os.makedirs(dir)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise Exception('Unable to create directory', e)
                pass

    def sink(self, data):
        try:
            filename = self.prefix + '_'\
                + str(int(datetime.timestamp(datetime.now()))) + '.json'
            with open(self.dir + filename, 'w') as out:
                self.write_function(data, out)
        except Exception:
            return super().SINK_FAILURE
        else:
            return super().SINK_SUCCESSFUL
