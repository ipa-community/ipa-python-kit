from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class MixinTimestamp(Generic[T]):
    created_at: T
    updated_at: T
    deleted_at: Optional[T] = None


class MixinIdentity(Generic[T]):
    id: T
