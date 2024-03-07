from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class BrokerEventsOptions(_message.Message):
    __slots__ = ["broker_management_api", "broker_uri"]
    BROKER_MANAGEMENT_API_FIELD_NUMBER: ClassVar[int]
    BROKER_URI_FIELD_NUMBER: ClassVar[int]
    broker_management_api: BrokerManagementApi
    broker_uri: str
    def __init__(self, broker_uri: Optional[str] = ..., broker_management_api: Optional[Union[BrokerManagementApi, Mapping]] = ...) -> None: ...

class BrokerManagementApi(_message.Message):
    __slots__ = ["max_retries", "timeout", "uri"]
    MAX_RETRIES_FIELD_NUMBER: ClassVar[int]
    TIMEOUT_FIELD_NUMBER: ClassVar[int]
    URI_FIELD_NUMBER: ClassVar[int]
    max_retries: int
    timeout: float
    uri: str
    def __init__(self, uri: Optional[str] = ..., timeout: Optional[float] = ..., max_retries: Optional[int] = ...) -> None: ...
