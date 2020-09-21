def sync(lock):
    def wrap(f):
        def do_function(*args, **kw):
            lock.acquire()
            try:
                return f(*args, **kw)
            finally:
                lock.release()
        return do_function
    return wrap
