"""Usage service."""

from app.logger import L


def calculate_longrun_usage_value(
    instances: int,
    instance_type: str | None,
    duration: float,
) -> int:
    """Return the usage_value.

    Args:
        instances: number of instances.
        instance_type: type of instance.
        duration: duration in seconds.
    """
    if instance_type:
        # TODO: consider instance_type?
        L.warning("instance_type is ignored")
    return int(instances * duration)


def calculate_oneshot_usage_value(count: int) -> int:
    """Return the usage_value.

    Args:
        count: number representing the usage.
    """
    return count


def calculate_storage_usage_value(size: int, duration: float) -> int:
    """Return the usage_value.

    Args:
        size: number of bytes.
        duration: duration in seconds.
    """
    return int(size * duration)
