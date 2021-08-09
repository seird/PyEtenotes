from typing import List

from PyQt5 import QtCore, QtGui, QtWidgets

from ..__version__ import __title__
from ..etesync import Notebook
from ..utils import center_widget
from ..settings import Settings
from .designs.widget_new_note import Ui_Dialog


settings = Settings(__title__)


class NewNoteDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent: QtWidgets.QMainWindow, notebooks: List[Notebook], selected_notebook: Notebook = None):
        super(NewNoteDialog, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Add a new note")

        self.line_name.setFocus()
        self.combo_notebooks.addItems([notebook.name for notebook in notebooks])

        self.combo_notebooks.setCurrentText(selected_notebook.name if selected_notebook else settings.value("newnotedialog/selectednotebook", type=str))
        self.combo_notebooks.currentTextChanged.connect(lambda text: settings.setValue("newnotedialog/selectednotebook", text))

        center_widget(parent, self)
