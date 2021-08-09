import logging

from typing import List
from PyQt5 import QtCore, QtGui, QtWidgets

from ..__version__ import __title__
from ..settings import Settings


logger = logging.getLogger("logger")
settings = Settings(__title__)


class NoteEditWidget(QtWidgets.QTextEdit):
    def __init__(self, parent: QtWidgets.QWidget):
        super(NoteEditWidget, self).__init__(parent)
        self.setAcceptRichText(False)
        font = settings.value("notewidget/font/edit", type=QtGui.QFont)
        self.set_font(font)

    def set_font(self, font: QtGui.QFont):
        self.setFont(font)
        font.setFixedPitch(True)
        metrics = QtGui.QFontMetrics(font)
        self.setTabStopWidth(4 * metrics.width(' '))

    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if e.modifiers() & QtCore.Qt.ControlModifier and e.modifiers() & QtCore.Qt.ShiftModifier and e.key() == QtCore.Qt.Key_Return:
            # Ctrl + Shift + Return
            self.previous_newline_callback()
        elif e.modifiers() & QtCore.Qt.ControlModifier and e.key() == QtCore.Qt.Key_Return:
            # Ctrl + Return
            self.next_newline_callback()
        elif e.modifiers() & QtCore.Qt.AltModifier and e.key() == QtCore.Qt.Key_Up:
            # Alt + Up
            self.move_line_up_callback()
        elif e.modifiers() & QtCore.Qt.AltModifier and e.key() == QtCore.Qt.Key_Down:
            # Alt + Down
            self.move_line_down_callback()
        elif e.key() == QtCore.Qt.Key_Tab:
            # Tab
            self.indent_callback(e)
        elif e.key() == QtCore.Qt.Key_Backtab:
            # Shift + Tab
            self.dedent_callback()
        elif e.modifiers() & QtCore.Qt.ControlModifier and e.key() == QtCore.Qt.Key_T:
            # Ctrl + T
            self.insert_table_callback(5, 5)
        elif e.modifiers() & QtCore.Qt.ControlModifier and e.key() == QtCore.Qt.Key_D:
            # Ctrl + D
            self.duplicate()
        elif e.modifiers() & QtCore.Qt.ControlModifier and e.key() == QtCore.Qt.Key_B:
            # Ctrl + B
            self.encapsulate_selected("**", "**")
        elif e.modifiers() & QtCore.Qt.ControlModifier and e.key() == QtCore.Qt.Key_I:
            # Ctrl + I
            self.encapsulate_selected("*", "*")
        elif e.modifiers() & QtCore.Qt.ControlModifier and e.key() == QtCore.Qt.Key_U:
            # Ctrl + U
            self.encapsulate_selected("<u>", "</u>")
        elif e.modifiers() & QtCore.Qt.ControlModifier and e.key() == QtCore.Qt.Key_K:
            # Ctrl + K
            self.encapsulate_selected("~~", "~~")
        elif e.modifiers() & QtCore.Qt.ControlModifier and e.key() == QtCore.Qt.Key_Slash:
            # Ctrl + /
            self.toggle_checkbox_callback()
        elif e.key() == QtCore.Qt.Key_Return:
            # Return
            self.return_callback(e)
        else:
            super().keyPressEvent(e)

    def next_newline_callback(self):
        text_cursor = self.textCursor()
        text_cursor.movePosition(QtGui.QTextCursor.EndOfBlock, QtGui.QTextCursor.MoveAnchor)
        if not self.auto_indent_newline(["\t", " "]):
            text_cursor.insertText("\n")
        self.setTextCursor(text_cursor)

    def previous_newline_callback(self):
        text_cursor = self.textCursor()
        text_cursor.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.MoveAnchor)
        text_cursor.insertText("\n")
        text_cursor.movePosition(QtGui.QTextCursor.Up, QtGui.QTextCursor.MoveAnchor)
        self.setTextCursor(text_cursor)

    def move_line_up_callback(self):
        text_cursor = self.textCursor()
        position_start = text_cursor.selectionStart()
        position_end = text_cursor.selectionEnd()
        column = text_cursor.columnNumber()

        text_cursor.setPosition(position_end, QtGui.QTextCursor.MoveAnchor)
        text_cursor.movePosition(QtGui.QTextCursor.EndOfBlock, QtGui.QTextCursor.MoveAnchor)
        text_cursor.setPosition(position_start, QtGui.QTextCursor.KeepAnchor)
        text_cursor.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.KeepAnchor)
        text_first_line = text_cursor.selectedText()
        text_cursor.removeSelectedText()

        text_cursor.deleteChar()
        text_cursor.movePosition(QtGui.QTextCursor.PreviousBlock, QtGui.QTextCursor.MoveAnchor)
        text_cursor.insertText(text_first_line + "\n")

        text_cursor.movePosition(QtGui.QTextCursor.Up, QtGui.QTextCursor.MoveAnchor)
        text_cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.MoveAnchor, n=column)

        self.setTextCursor(text_cursor)

    def move_line_down_callback(self):
        text_cursor = self.textCursor()
        position_start = text_cursor.selectionStart()
        position_end = text_cursor.selectionEnd()
        column = text_cursor.columnNumber()

        text_cursor.setPosition(position_end, QtGui.QTextCursor.MoveAnchor)
        text_cursor.movePosition(QtGui.QTextCursor.EndOfBlock, QtGui.QTextCursor.MoveAnchor)
        text_cursor.setPosition(position_start, QtGui.QTextCursor.KeepAnchor)
        text_cursor.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.KeepAnchor)
        text_first_line = text_cursor.selectedText()
        text_cursor.removeSelectedText()

        text_cursor.deleteChar()
        text_cursor.movePosition(QtGui.QTextCursor.EndOfBlock, QtGui.QTextCursor.MoveAnchor)
        text_cursor.insertText("\n" + text_first_line)

        text_cursor.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.MoveAnchor)
        text_cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.MoveAnchor, n=column)

        self.setTextCursor(text_cursor)

    def indent_callback(self, e: QtGui.QKeyEvent):
        text_cursor = self.textCursor()

        if not text_cursor.hasSelection():
            super().keyPressEvent(e)
            return

        position_start = text_cursor.selectionStart()
        position_end = text_cursor.selectionEnd()

        text_cursor.setPosition(position_start)
        text_cursor.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.MoveAnchor)

        while text_cursor.position() < position_end:
            position = text_cursor.position()
            text_cursor.insertText("\t")
            text_cursor.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor)
            text_cursor.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.MoveAnchor)
            if position == text_cursor.position():
                break
            position_end += 1

    def dedent_callback(self):
        text_cursor = self.textCursor()

        position_start = text_cursor.selectionStart()
        position_end = text_cursor.selectionEnd()

        text_cursor.setPosition(position_start)
        text_cursor.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.MoveAnchor)

        while text_cursor.position() < position_end:
            position = text_cursor.position()
            text_cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor)
            if text_cursor.selectedText() == "\t":
                text_cursor.removeSelectedText()
                position_end -= 1
            text_cursor.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor)
            text_cursor.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.MoveAnchor)
            if position == text_cursor.position():
                break

    def duplicate(self):
        text_cursor = self.textCursor()
        if selected_text := text_cursor.selectedText():
            position_end = text_cursor.selectionEnd()
            text_cursor.setPosition(position_end, QtGui.QTextCursor.MoveAnchor)
            text_cursor.insertText(selected_text)
            text_cursor.setPosition(position_end, QtGui.QTextCursor.MoveAnchor)
            text_cursor.setPosition(position_end+len(selected_text), QtGui.QTextCursor.KeepAnchor)
            self.setTextCursor(text_cursor)
        else:
            text_cursor.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.MoveAnchor)
            text_cursor.movePosition(QtGui.QTextCursor.EndOfBlock, QtGui.QTextCursor.KeepAnchor)
            block_text = text_cursor.selectedText()
            text_cursor.clearSelection()
            text_cursor.insertText("\n" + block_text)

    def insert_table_callback(self, rows: int, cols: int):
        text_cursor = self.textCursor()
        position_start = text_cursor.position()
        text_cursor.insertText("|   " * cols + "|\n" + "|---" * cols + "|\n" + "".join(["|   " * cols + "|\n"] * rows))
        text_cursor.setPosition(position_start)
        text_cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.MoveAnchor, n=2)
        self.setTextCursor(text_cursor)

    def encapsulate_selected(self, start: str, end: str):
        text_cursor = self.textCursor()
        text_cursor.insertText(start + text_cursor.selectedText() + end)
        text_cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.MoveAnchor, n=len(end))
        self.setTextCursor(text_cursor)

    def toggle_checkbox_callback(self):
        text_cursor = self.textCursor()
        position_start = text_cursor.selectionStart()
        position_end = text_cursor.selectionEnd()

        text_cursor.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.MoveAnchor)
        text_cursor.movePosition(QtGui.QTextCursor.EndOfBlock, QtGui.QTextCursor.KeepAnchor)
        selected_text = text_cursor.selectedText()
        selected_text_stripped = selected_text.lstrip()

        if selected_text_stripped.startswith("- [ ]"):
            text_cursor.insertText(selected_text.replace("- [ ]", "- [x]", 1))
        elif selected_text_stripped.startswith("- [x]"):
            text_cursor.insertText(selected_text.replace("- [x]", "- [ ]", 1))
        elif selected_text_stripped.startswith("- [X]"):
            text_cursor.insertText(selected_text.replace("- [X]", "- [ ]", 1))
        else:
            return

        text_cursor.setPosition(position_start, QtGui.QTextCursor.MoveAnchor)
        text_cursor.setPosition(position_end, QtGui.QTextCursor.KeepAnchor)
        self.setTextCursor(text_cursor)

    def return_callback(self, e: QtGui.QKeyEvent):
        if self.textCursor().atBlockEnd() and self.auto_indent_newline(["\t", " "]):
            return
        super().keyPressEvent(e)

    def auto_indent_newline(self, characters: List[str]) -> bool:
        text_cursor = self.textCursor()
        text_cursor.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.MoveAnchor)
        text_cursor.movePosition(QtGui.QTextCursor.NextWord, QtGui.QTextCursor.KeepAnchor)
        selected_text = text_cursor.selectedText()
        if not selected_text:
            return False
        for character in characters:
            if (num_characters := selected_text.count(character)) == len(selected_text):
                # current line is indented
                text_cursor.movePosition(QtGui.QTextCursor.EndOfBlock, QtGui.QTextCursor.MoveAnchor)
                text_cursor.insertText("\n" + character * num_characters)
                self.setTextCursor(text_cursor)
                return True
        return False
