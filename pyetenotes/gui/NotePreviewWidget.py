import logging

from PyQt5 import QtCore, QtGui, QtWidgets

from ..__version__ import __title__
from ..settings import Settings


logger = logging.getLogger("logger")
settings = Settings(__title__)


class NotePreviewWidget(QtWidgets.QTextBrowser):
    def __init__(self, parent: QtWidgets.QWidget):
        super(NotePreviewWidget, self).__init__(parent)

        self.setOpenExternalLinks(True)
        font = settings.value("notewidget/font/preview", type=QtGui.QFont)
        self.set_font(font)

    def set_font(self, font: QtGui.QFont):
        self.setTabStopWidth(4 * self.fontMetrics().width(' '))
        self.setFont(font)
