class DataSink():
    SINK_SUCCESSFUL = 0
    SINK_FAILURE = 1

    def __init__(self):
        super().__init__()

    def sink(self, data):
        raise NotImplementedError
