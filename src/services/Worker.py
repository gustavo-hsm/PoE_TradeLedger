class Worker():
    def __init__(self):
        self.main_task = None
        self.healthy = None

    def is_healthy(self):
        raise NotImplementedError

    def set_main_task(self, main_task):
        assert callable(main_task)
        self.main_task = main_task

    def do_main_task(self, *args):
        assert callable(self.main_task)
        self.main_task(*args)
