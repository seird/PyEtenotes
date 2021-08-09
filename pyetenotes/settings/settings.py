from typing import Any
from .default_settings import DEFAULT_SETTINGS


from PyQt5 import QtCore


class Settings(QtCore.QSettings):
    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)

    def value(self, key: str, defaultValue: Any = None, type: Any = None) -> Any:
        if type:
            return super().value(key, defaultValue=defaultValue or DEFAULT_SETTINGS.get(key), type=type)
        else:
            return super().value(key, defaultValue=defaultValue or DEFAULT_SETTINGS.get(key))

    def setValue(self, key: str, value: Any) -> None:
        if isinstance(value, bool):
            # True gets converted to a string by QSettings
            value = int(value)
        super().setValue(key, value)
