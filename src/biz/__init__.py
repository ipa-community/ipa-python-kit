from ipa.decorator import deprecated
from ipa.math import add


@deprecated("use ipa.math.add instead")
def demo_biz_add(a: int, b: int) -> int:
    return add(a, b)
