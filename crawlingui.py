import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from naver_google_crawling import naver,google
from digital_paper import digital_news,newspim
import pandas as pd
# form_class = uic.loadUiType(r"D:\crawling\crawling.ui")[0]
form_class = uic.loadUiType("crawling.ui")[0]
class WindowClass(QMainWindow, form_class) :
    def __init__(self):
    
        super().__init__()
        self.setupUi(self)

        self.naver_check = 0
        self.google_check = 0
        self.keyword = ''''''
        self.op = ''
        self.other = 0
        self.checkBox.clicked.connect(self.check_naver)
        self.checkBox2.clicked.connect(self.check_google)
        self.radioButton3.clicked.connect(self.AND_check)
        self.radioButton4.clicked.connect(self.OR_check)
        self.radioButton5.clicked.connect(self.None_check)
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
    def AND_check(self):
        self.op = 'AND'
    def None_check(self):
        self.op = 'None'
    def OR_check(self):
        self.op = 'OR'
    def other_information(self):
        self.other = 1
    def crawling(self):
        self.keyword = self.textEdit.toPlainText()
        df = pd.DataFrame()
        if self.naver_check:
            naver_df = naver(self.keyword,self.op)
            df = pd.concat([df,naver_df])
        elif self.google_check:
            google_df = google(self.keyword,self.op)
            df = pd.concat([df,google_df])
        elif self.naver_check and self.google_check:
            naver_df = naver(self.keyword,self.op)
            google_df = google(self.keyword,self.op)
            df = pd.concat([df,naver_df,google_df])
        if self.other:
            digital_df = digital_news()
            digital_df2 = newspim()
            df=pd.concat([df,digital_df,digital_df2])
        df.to_excel('merge_data.xlsx',index=False)

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
    app.exec_()
