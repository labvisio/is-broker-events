from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Optional

DESCRIPTOR: _descriptor.FileDescriptor

class BrokerEventsOptions(_message.Message):
    __slots__ = ["broker_uri", "management_uri"]
    BROKER_URI_FIELD_NUMBER: ClassVar[int]
    MANAGEMENT_URI_FIELD_NUMBER: ClassVar[int]
    broker_uri: str
    management_uri: str
    def __init__(self, broker_uri: Optional[str] = ..., management_uri: Optional[str] = ...) -> None: ...
