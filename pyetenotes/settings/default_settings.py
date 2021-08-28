import os

from PyQt5 import QtCore, QtGui

from ..__version__ import __title__


font_edit = QtGui.QFont()
font_edit.setFamily("Noto Mono")
font_edit.setStyleHint(QtGui.QFont.Monospace)
font_edit.setFixedPitch(True)
font_edit.setPointSize(10)


font_preview = QtGui.QFont()
font_preview.setFamily("Noto Sans")
font_preview.setPointSize(10)


path = QtCore.QStandardPaths.standardLocations(QtCore.QStandardPaths.CacheLocation)[0]
os.makedirs(path, exist_ok=True)
cache_path = os.path.join(path, f"{__title__}-cache.bytes")


DEFAULT_SETTINGS = {
    "style": "default",
    "cache/path": cache_path,
    "tasks/interval": 60,
    "export/extension": "txt",
    "export/path": QtCore.QStandardPaths.standardLocations(QtCore.QStandardPaths.HomeLocation)[0],
    "notestabwidget/showcolors": True,
    "notestreewidget/showcolors": True,
    "notestreewidget/color/alpha": 100,
    "filternoteswidget/visible": True,
    "notewidget/font/edit": font_edit,
    "notewidget/font/preview": font_preview,
    "shortcuts/new_note": "Ctrl+N",
    "shortcuts/new_notebook": "Ctrl+Shift+N",
    "shortcuts/save": "Ctrl+S",
    "shortcuts/save_all": "Ctrl+Shift+S",
    "shortcuts/quit": "Ctrl+Q",
    "shortcuts/preview": "Ctrl+P",
    "shortcuts/live_preview": "Ctrl+L",
    "shortcuts/edit": "Ctrl+E",
    "shortcuts/close_tab": "Ctrl+W",
    "shortcuts/next_tab": "Ctrl+Tab",
    "shortcuts/previous_tab": "Ctrl+Shift+Tab",
    "shortcuts/toggle_filter": "Ctrl+Shift+F",
    "tasks/update_notebooks/interval": 0,
}
