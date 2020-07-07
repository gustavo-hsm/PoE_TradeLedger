from enum import Enum


class EventType(Enum):
    HANDLER_READY = 1
    HANDLER_NEXT = 2
    HANDLER_FINISHED = 3
    HANDLER_ERROR = 4
