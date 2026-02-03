from enum import StrEnum

class JobProgressValues(StrEnum):
    READY = "ready"
    FAILED = "failed"
    RUNNING = "running"
