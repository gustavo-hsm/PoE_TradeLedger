import pprint
import logging

from data_sink.DataSink import DataSink


class SinkToConsole(DataSink):
    def __init__(self):
        DataSink.__init__(self)

    def sink(self, data):
        sink_status = None
        try:
            for item in data:
                pprint.pprint(data)
        except (ValueError, TypeError):
            logging.error('Unable to sink data to console')
            sink_status = super().SINK_FAILURE
        else:
            sink_status = super().SINK_SUCCESSFUL
        finally:
            return sink_status
