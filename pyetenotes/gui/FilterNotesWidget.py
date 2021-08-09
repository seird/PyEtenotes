from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal

from ..__version__ import __title__
from ..settings import Settings


settings = Settings(__title__)


class FilterNotesWidget(QtWidgets.QLineEdit):
    hidden = pyqtSignal()

    def __init__(self, height: int = 32):
        super(FilterNotesWidget, self).__init__()
        self.setClearButtonEnabled(True)
        self.setFixedHeight(height)
        self.setVisible(settings.value("filternoteswidget/visible", type=bool))
        self.setPlaceholderText(f"Filter notes ({settings.value('shortcuts/toggle_filter', type=str)} to toggle)")

    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if e.key() == QtCore.Qt.Key_Escape:
            self.clear()
        else:
            super().keyPressEvent(e)

    def toggle(self):
        self.clear()
        self.setVisible(not self.isVisible())
        settings.setValue("filternoteswidget/visible", self.isVisible())
        if self.isVisible():
            self.setFocus()
        else:
            self.hidden.emit()
