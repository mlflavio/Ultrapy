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


def string_to_int_list(string):
    string = string.strip('[]')
    values = string.split(',')
    values = [val.strip() for val in values]
    int_list = [int(val) for val in values]
    return int_list

def concat_files(directory, from_files, to_file):
    with open(to_file, 'w') as destine:
        for file in from_files:
            with open(os.path.join(directory, file), 'r') as origem:
                content = origem.read()
                destine.write(content)


class MainWindow(QMainWindow):
    def __init__(self):
        # Inicializa as variáveis
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.center()   # centraliza janela no centro da tela

        self.df = pd.DataFrame()
        self.image = []

        # timestamp para faixa de dados que serão enviados
        self.start = str
        self.stop = str

        # conecta os elementos da janela aos seus respectivos módulos
        self.ui.toolButton.clicked.connect(self.select_file)
        self.ui.pushButton.clicked.connect(self.plot)
        self.ui.pushButton_2.clicked.connect(self.to_cloud)
        self.ui.horizontalSlider.valueChanged.connect(self.updateComboBoxValue)
        self.ui.horizontalSlider_2.valueChanged.connect(self.updateComboBoxValue2)

    def center(self):
        # centraliza janela
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def select_file(self):
        # abre uma janela para seleção do arquivo
        past_dict = self.ui.lineEdit.text()
        directory = QFileDialog.getExistingDirectory(self, "Selecionar uma pasta")
        self.ui.lineEdit.setText(directory)

        # Lista com os arquivos contidos na pasta
        concat_files(directory, sorted(os.listdir(directory)), "Concatenated_files.csv")

        self.df = pd.read_csv("Concatenated_files.csv", index_col="timestamp_str")

        # Remove linhas onde o nome é 'profile_data'
        self.df = self.df[self.df != "profile_data"].dropna()
        df_index = self.df.index.drop_duplicates()

        self.newdata_combobox(df_index)


    def newdata_combobox(self, df_index):
        self.ui.comboBox.clear()
        self.ui.comboBox_2.clear()
        self.ui.comboBox.addItems(df_index)
        self.ui.comboBox_2.addItems(df_index)

    def updateComboBoxValue(self, value):
        self.ui.comboBox.setCurrentIndex(value)

    def updateComboBoxValue2(self, value):
        self.ui.comboBox_2.setCurrentIndex(value)

    def plot(self):

        # plot mapa de calor com os dados selecionados pelo usuário
        self.start = self.ui.comboBox.currentText()
        self.stop = self.ui.comboBox_2.currentText()

        df_valid = self.df.applymap(string_to_int_list)

        data = df_valid[self.start:self.stop]
        aux = np.asarray([i for i in data["profile_data"]])

        heatmap = self.ui.heatmap.setImage(aux)
        self.ui.plot_item.addItem(heatmap)

    def to_cloud(self):

        # envia dados para nuvem
        aux = self.df["profile_data"].loc[self.start:self.stop]

        pd.DataFrame(aux).to_csv(f"toCloud_{self.start}:{self.stop}")

        file_name = f"toCloud_{self.start}:{self.stop}"
        file_content = []

        # Crie um objeto S3
        s3 = boto3.resource('s3')
        bucket_name = 'nesa-signal-transfer-data'

        try:
            s3.Bucket(bucket_name).put_object(Key=file_name, Body=file_content)
            print(f"Arquivo {file_name} enviado com sucesso para o S3!")
        except Exception as e:
            print(f"Erro ao enviar arquivo {file_name} para o S3: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
