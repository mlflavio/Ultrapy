import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import QDateTime, Qt
from datetime import datetime
from ultrapy_window import Ui_MainWindow
import pandas as pd
import numpy as np
import boto3
import pickle
import os
import configparser

def mining(data):

    aux = [i.split(",") for i in data]

    for i in range(len(aux)):
        aux[i][0] = aux[i][0].replace("[", "")
        aux[i][-1] = aux[i][-1].replace("]", "")
        for j in range(200):
            aux[i][j] = int(aux[i][j])

    return np.array(aux)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.center()

        self.df = pd.DataFrame()
        self.image = []
        self.start = str
        self.stop = str

        self.ui.toolButton.clicked.connect(self.select_file)
        self.ui.pushButton.clicked.connect(self.plot)
        self.ui.pushButton_2.clicked.connect(self.to_cloud)

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def select_file(self):
        # abre uma janela para seleção do arquivo

        file_name, _ = QFileDialog.getOpenFileName(self, "Selecionar arquivo", "", "CSV Files (*.csv)")
        self.ui.lineEdit.setText(file_name)

        self.df = pd.read_csv(file_name, index_col="timestamp_str")

        date_format = "%Y-%m-%d %H:%M:%S"

        start = self.df.index[0]
        end = self.df.index[-1]

        datetime_start = datetime.strptime(start, date_format)
        qdatetime_start = QDateTime(datetime_start)

        datetime_end = datetime.strptime(end, date_format)
        qdatetime_end = QDateTime(datetime_end)

        self.ui.dateTimeEdit.setDateTime(qdatetime_start)
        self.ui.dateTimeEdit_2.setDateTime(qdatetime_end)

    def plot(self):

        self.start = self.ui.dateTimeEdit.text()
        self.stop = self.ui.dateTimeEdit_2.text()

        self.image = mining(self.df["profile_data"].loc[self.start:self.stop])

        heatmap = self.ui.heatmap.setImage(self.image)
        self.ui.plot_item.addItem(heatmap)

    def to_cloud(self):

        aux = self.df["profile_data"].loc[self.start:self.stop]

        pd.DataFrame(aux).to_csv(f"toCloud_{self.start}:{self.stop}")

        # file_name = f"toCloud_{self.start}:{self.stop}"
        # file_content = []
        #
        # # Crie um objeto S3
        # s3 = boto3.resource('s3')
        # bucket_name = 'nesa-signal-transfer-data'
        #
        # try:
        #     s3.Bucket(bucket_name).put_object(Key=file_name, Body=file_content)
        #     print(f"Arquivo {file_name} enviado com sucesso para o S3!")
        # except Exception as e:
        #     print(f"Erro ao enviar arquivo {file_name} para o S3: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
