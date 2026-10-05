import uuid

from opensmi.client import BaseRemoteComponent
from opensmi.client.remote_callable import RemoteCallable
from opensmi.client.remote_variable_container import RemoteVariable


class GenericCache[T1, T2]:
    def __init__(self):
        self.cache_1_2: dict[T1, T2] = {}
        self.cache_2_1: dict[T2, T1] = {}

    def clear(self) -> None:
        self.cache_1_2.clear()
        self.cache_2_1.clear()

    def add(self, key: T1, val: T2) -> None:
        # Remove an existing value associated with this key.
        old_val = self.cache_1_2.get(key)
        if old_val is not None:
            self.cache_2_1.pop(old_val, None)

        # Remove an existing key associated with this value.
        old_key = self.cache_2_1.get(val)
        if old_key is not None:
            self.cache_1_2.pop(old_key, None)

        # Add the new bidirectional mapping.
        self.cache_1_2[key] = val
        self.cache_2_1[val] = key

    def get_by_key(self, key: T1) -> T2 | None:
        return self.cache_1_2.get(key)

    def get_by_val(self, val: T2) -> T1 | None:
        return self.cache_2_1.get(val)

    def remove_by_key(self, key: T1) -> T2 | None:
        val = self.cache_1_2.pop(key, None)

        if val is not None:
            self.cache_2_1.pop(val, None)

        return val

    def remove_by_val(self, val: T2) -> T1 | None:
        key = self.cache_2_1.pop(val, None)

        if key is not None:
            self.cache_1_2.pop(key, None)

        return key

    def contains_key(self, key: T1) -> bool:
        return key in self.cache_1_2

    def contains_val(self, val: T2) -> bool:
        return val in self.cache_2_1

    def __len__(self) -> int:
        return len(self.cache_1_2)

    def __str__(self) -> str:
        if not self.cache_1_2:
            return f"{type(self).__name__}(empty)"

        entries = ", ".join(
            f"{key!s} -> {val!r}"
            for key, val in self.cache_1_2.items()
        )

        return f"{type(self).__name__}({entries})"


class NodeIdEntityIdCache(GenericCache[str, uuid.UUID]):
    pass


class EntityIdCallableCache(GenericCache[uuid.UUID, RemoteCallable]):
    pass


class EntityIdComponentCache(GenericCache[uuid.UUID, BaseRemoteComponent]):
    pass


class EntityIdVariableCache(GenericCache[uuid.UUID, RemoteVariable]):
    pass
