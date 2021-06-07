import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from naver_google_crawling import naver,google
from digital_paper import digital_news,newspim,AItimes
import pandas as pd
import tkinter as tk
from tkinter import messagebox
# form_class = uic.loadUiType(r"D:\crawling\crawling.ui")[0]
form_class = uic.loadUiType("crawling.ui")[0]
class WindowClass(QMainWindow, form_class) :
    def __init__(self):
    
        super().__init__()
        self.setupUi(self)

        self.naver_check = 0
        self.google_check = 0
        self.keyword = ''''''
        self.other = 0
        self.checkBox.clicked.connect(self.check_naver)
        self.checkBox2.clicked.connect(self.check_google)
        self.save_button.clicked.connect(self.other_information)
        self.Search.clicked.connect(self.crawling)

    def check_naver(self):
        if self.checkBox.isChecked() == True:
            self.naver_check = 1
        else:
            self.naver_check = 0
        print('naver check!')
    def check_google(self):
        if self.checkBox2.isChecked() == True:
            self.google_check = 1
        else:
            self.google_check = 0
        print('google check!')
    def other_information(self):
        self.other = 1
    def crawling(self):
        self.keyword = self.textEdit.toPlainText()
        df = pd.DataFrame()
        if self.naver_check:
            naver_df = naver(self.keyword)
            if len(naver_df):
                df = pd.concat([df,naver_df])
        elif self.google_check:
            google_df = google(self.keyword)
            if len(google_df):
                df = pd.concat([df,google_df])
        elif self.naver_check and self.google_check:
            naver_df = naver(self.keyword)
            google_df = google(self.keyword)
            if len(naver_df) or len(google_df):
                df = pd.concat([df,naver_df,google_df])
        if self.other:
            digital_df = digital_news()
            digital_df2 = newspim()
            digital_df3 = AItimes()
            df=pd.concat([df,digital_df,digital_df2,digital_df3])
        if len(df)>0:
            df.to_excel('merge_data.xlsx',index=False)
            root2 = tk.Tk()
            msg = messagebox.showinfo(title='Complete',message='Complete!')
            if msg == 'ok':
                root2.destroy()
        else:
            root2 = tk.Tk()
            msg = messagebox.showerror(title='Nothing',message='Nothing')
            if msg == 'ok':
                root2.destroy()
if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
    app.exec_()
