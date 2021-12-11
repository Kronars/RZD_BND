"""
PyQt приложение с выбором папки для входных и выходного файлов.
"""
import sys
import os
import pandas as pd
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QPlainTextEdit
from modules.data_worker import get_dataframes
from modules.draw import draw_nomogramma


class Form(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.input_path = ''
        self.output_path = ''

        self.user_path_choice_text_edit = QPlainTextEdit()
        self.user_path_choice_text_edit.setFont(QFont('Arial', 11))
        self.user_path_choice_text_edit.setReadOnly(True)

        openInputDirButton = QPushButton("Выбрать папку с входящими данными")
        openInputDirButton.clicked.connect(lambda x: self.getDirectory('input'))

        openOutputDirButton = QPushButton("Выбрать папку для результата")
        openOutputDirButton.clicked.connect(lambda x: self.getDirectory('output'))

        layoutV = QVBoxLayout()
        layoutV.addWidget(openInputDirButton)
        layoutV.addWidget(openOutputDirButton)

        layoutH = QHBoxLayout()
        layoutH.addLayout(layoutV)
        layoutH.addWidget(self.user_path_choice_text_edit)

        self.runButton = QPushButton("Запуск")
        self.runButton.clicked.connect(self.calculate_nomogramma)
        layoutV.addWidget(self.runButton)

        centerWidget = QWidget()
        centerWidget.setLayout(layoutH)
        self.setCentralWidget(centerWidget)

        self.resize(740, 480)
        self.setWindowTitle("PyQt5-QFileDialog")

    def getDirectory(self, kind):
        dirlist = QFileDialog.getExistingDirectory(self, "Выбрать папку", ".")
        if kind == 'input':
            text = "<br>Папка с входными данными: <b>{}</b>"
            self.input_path = dirlist
        elif kind == 'output':
            text = "<br>Папка для файла с результатом: <b>{}</b>"
            self.output_path = dirlist
        self.user_path_choice_text_edit.appendHtml(text.format(dirlist))

    def calculate_nomogramma(self):
        result_df,  start, end = get_dataframes(self.input_path)
        # result_df.to_excel(self.output_path + "/result_df.xlsx", index=False)
        draw_nomogramma(result_df, self.output_path,  start, end)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Form()
    ex.show()
    sys.exit(app.exec_())
