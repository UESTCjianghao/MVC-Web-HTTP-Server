import json
from enum import (
    Enum,
    auto,
)


class UserRole(Enum):
    guest = auto()
    normal = auto()

    # 让 mysql 支持我们的枚举
    def translate(self, _escape_table):
        return self.name

