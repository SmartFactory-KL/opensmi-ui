from enum import Enum

from model.common_types import (
    GenericUpdateEntityType,
    GenericUpdateMessage,
    JsonBaseModel,
    JsonOutModel,
)


# Generic types


# Enums
class ServerConnectionState(str, Enum):
    Open = "open"  # connection is not established
    Pending = "pending"  # waiting for connection to be established
    Browsing = "browsing"  # connection is established, but not ready to use yet (OPC UA server needs to be browsed)
    Connected = "connected"  # connection is established and ready to use


# Requests
class ServerConnectRequest(JsonBaseModel):
    server_url: str
    username: str
    password: str


# Update Wrapper
class ServerUpdateMessage[T](GenericUpdateMessage[T]):
    entity_type: GenericUpdateEntityType = GenericUpdateEntityType.Server


# Updates
class ServerConnectionUpdate(JsonOutModel):
    connection_state: ServerConnectionState


class ServerTimeUpdate(JsonOutModel):
    new_datetime: str


# Responses
class ServerStateResponse(JsonOutModel):
    connection_state: ServerConnectionState
    server_url: str
    username: str


class ServerDefaultConnectionDataResponse(JsonOutModel):
    default_server_url: str
    default_server_username: str
    default_server_password: str
