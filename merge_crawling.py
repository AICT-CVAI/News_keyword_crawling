import pandas as pd
import bs4
from urllib.request import urlopen
import urllib
import time
import tkinter as tk
from tkinter import messagebox
import datetime
import time
import re
import numpy as np
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from naver_google_crawling import naver,google
from digital_paper import digital_news,newspim,AItimes

import tkinter as tk
from tkinter import messagebox

def kortime2engtime(time_string):
    today = datetime.datetime.today()
    number = int(re.findall('\d+', time_string)[0])
    kortime = ''.join(re.findall("[^0-9]",time_string))
    if kortime == '일' :
        before_date = datetime.timedelta(days=number)
    elif kortime == '분':
        before_date= datetime.timedelta(minutes=number)
    elif kortime == '시간' :
        before_date = datetime.timedelta(hours=number)
    elif kortime == '초' : 
        before_date = datetime.timedelta(seconds=number)
    else:
        return time_string
    save_date = (today-before_date).strftime('%Y.%m.%d')
    return save_date


def naver(search):
    searching = '''{}'''.format(search)
    searching = searching.strip()
    df_list = []
    start = 1
    keyword = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', ' ', searching).split()
    op = re.findall('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', searching)

    plus = [keyword[0]]

    for index, value in enumerate(op):
        if value == '+':
            plus.extend([keyword[index+1]])

    new = keyword[0]
    for k,o in zip(keyword[1:],op):
        if len(keyword) ==1:
            break
        else:
            new += ' '+o+k
    word_encode = urllib.parse.quote(new)

    while True:
        url = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query={}&pd=1&start={}'.format(word_encode,
                                                                                                          start)
        source = urlopen(url).read()
        source = bs4.BeautifulSoup(source, 'html.parser')
        title_path = source.find_all('a', {'class': 'news_tit'})
        abstract_path = source.find_all('a', {'class': 'api_txt_lines dsc_txt_wrap'})
        date_path = source.find_all('span', {'class': 'info'})
        for idx,v in enumerate(date_path):
            if v.find('i'):
                date_path.pop(idx)
        
        if len(title_path) == 0:
            root = tk.Tk()
            msg = messagebox.showerror(title="Naver No news", message='please search other keyword')
            if msg == 'ok':
                root.destroy()
                break

        for i in range(len(title_path)):
            title = title_path[i].get('title')

            if all(key in title for key in plus):
                abstract = abstract_path[i].text
                link = title_path[i].get('href')
                date_txt = date_path[i].text
                
                date = kortime2engtime(date_txt.split()[0])
                df = pd.DataFrame(
                    {'title': [title], 'abstract': [abstract], 'url': [link], 'date': [date],
                        'engine': ['naver']})
                df_list.append(df)
             

        current_page = source.find_all('a', {'aria-pressed': 'true'})[0].text
        last_page = source.find_all('a', {'aria-pressed': 'false'})[-1].text
        if last_page == '문서 저장하기':
            break

        if int(current_page) >= int(last_page):
            break
        else:
            start += 10
        time.sleep(0.5)
        
        print('crawling...')

    if df_list:
            naver_df = pd.concat(df_list)
            new = new.replace('|',' ')
            naver_df.to_excel('''naver_{}_result.xlsx'''.format(new),index=False)

            root2 = tk.Tk()
            msg = messagebox.showinfo(title='Save msg',message='Naver Save!')
            if msg == 'ok':
                root2.destroy()
            return naver_df
    else:
        root3 = tk.Tk()
        msg = messagebox.showerror(title = "Naver No news",message = 'please search other keyword')
        if msg == 'ok':
            root3.destroy()


def google(search):
    searching = '''{}'''.format(search)
    searching = searching.strip()

    period = ' when:7d'
    
    keyword = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', ' ', searching).split()
    op = re.findall('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', searching)

    
    plus = [keyword[0]]

    for index, value in enumerate(op):
        if value == '+':
            plus.extend([keyword[index+1]])
    
    new = keyword[0]
    for k,o in zip(keyword[1:],op):
        if len(keyword) ==1:
            stop = True
            break

        else:
            new += o+k
 
    word_encode = urllib.parse.quote(new+period)
    

    base_url = 'https://news.google.com/'
    url = 'https://news.google.com/search?q={}&hl=ko&gl=KR&ceid=KR:ko'.format(word_encode)
    # print(url)
    source = urlopen(url).read()
    source = bs4.BeautifulSoup(source,'html.parser')
    
    df_list = []
    article_list = source.find_all('a',{'class':'DY5T1d RZIKme'})
    date_path = source.find_all('time',{'class':'WW6dff uQIVzc Sksgp'})

    if len(article_list) == 0:
        root = tk.Tk()
        msg = messagebox.showerror(title = "Google No news",message = 'please search other keyword')
        if msg == 'ok':
            root.destroy()
    else:
        for i in range(len(article_list)):
            
            title = article_list[i].text
            date = date_path[i].get('datetime').split('T')[0].replace('-','.')

            if all(key in title for key in plus):
                link = base_url + article_list[i].get('href')[1:]
                df = pd.DataFrame({'title':[title],'abstract':[np.nan],'url':[link],'date':[date],'engine':['Google']})
            
                df_list.append(df)
                print('crawling...')
        
    if df_list:
            google_df = pd.concat(df_list)
            
            new = new.replace('|',' ')
            google_df.to_excel('''google_{}_result.xlsx'''.format(new),index=False)

            root2 = tk.Tk()
            msg = messagebox.showinfo(title='Save msg',message='Google Save!')
            if msg == 'ok':
                root2.destroy()
            return google_df
    else:
        root3 = tk.Tk()
        msg = messagebox.showerror(title = "Google No news",message = 'please search other keyword')
        if msg == 'ok':
            root3.destroy()

def digital_news():
    page_num = 1
    today = datetime.datetime.now()
    until_time = time.mktime((today-datetime.timedelta(days=7)).timetuple())
    stop=False
    df_list = []
    while True:
        url = 'https://www.etnews.com/news/section.html?id1=06&page={}'.format(page_num)
        source = urlopen(url).read()
        source = bs4.BeautifulSoup(source,'html.parser')
        title_path = source.find_all('dl',{'class':'clearfix'})
        date_path = source.find_all('dd',{'class':'date'})
        for i in range(len(title_path)):
            info_path = list(filter(None,title_path[i].text.split('\n')))
            if page_num == 1 and i == 0: pass
            else:
                date_tmp = date_path[i].text.split()
                if len(date_tmp)>2:
                    tmp = list(map(lambda x: re.sub('[각-힣]','',string=x),date_tmp))
                    date = list(filter(None, tmp))[0]
                else:
                    date = re.sub('[각-힣]','',string=date_tmp[0])
                
                timestamp_date = time.mktime(datetime.datetime.strptime(date,'%Y.%m.%d').timetuple())
                if timestamp_date - until_time<0:
                    stop = True
                    break                
                title = info_path[0]
                abstract = info_path[1]
                link = title_path[i].find({'a':'href'}).get('href')[2:]
                df = pd.DataFrame({'title':[title],'abstract':[abstract],'url':[link],'date':[date],'engine':['전자신문']})
                df_list.append(df)
        page_num +=1
        if stop:
            break
    df = pd.concat(df_list)
    today_str = today.strftime('%Y%m%d')
    df.to_excel('Digital_news_{}.xlsx'.format(today_str),index=False)
    root2 = tk.Tk()
    msg = messagebox.showinfo(title='Save msg',message='Save!')
    if msg == 'ok':
        root2.destroy()
    return df

def newspim():
    today = datetime.datetime.now()
    df_list = []
    until_time = time.mktime((today-datetime.timedelta(days=7)).timetuple())
    page_num = 0
    stop = False
    while True:
        url = 'https://www.newspim.com/news/lists/?category_cd=106020&page={}'.format(page_num)
        source = urlopen(url).read()
        source = bs4.BeautifulSoup(source,'html.parser')
        title_path = source.find_all('strong',{'class':'subject_h'})
        url_path = source.find_all('p',{'class':'summary'})
        date_path = source.find_all('p',{'class':'byline'})
        for i in range(len(title_path)):
            date = date_path[i].text.split()[0]
            timestamp_date = time.mktime(datetime.datetime.strptime(date,'%Y-%m-%d').timetuple())
            if timestamp_date - until_time<0:
                stop = True
                break
            title = title_path[i].text
            abstract = url_path[i].text
            link = url_path[i].find('a').get('href')
            df = pd.DataFrame({'title':[title],'abstract':[abstract],'url':[link],'date':[date],'engine':['뉴스핌']})
            df_list.append(df) 
        page_num+=20
        if stop:
            break
    df = pd.concat(df_list)
    today_str = today.strftime('%Y%m%d')
    df.to_excel('Newspim_{}.xlsx'.format(today_str),index=False)
    root2 = tk.Tk()
    msg = messagebox.showinfo(title='Save msg',message='Save!')
    if msg == 'ok':
        root2.destroy()
    return df

def AItimes():
    today = datetime.datetime.now()
    page_num = 1
    df_list= [] 
   
    stop = False
    
    while True:
        url = 'https://www.aitimes.kr/news/articleList.html?page={}&total=104&box_idxno=&sc_sub_section_code=S2N10&view_type=sm'.format(page_num)
        source = urlopen(url).read()
        source = bs4.BeautifulSoup(source,'html.parser')
        title_path = source.find_all('h4',{'class':'titles'})
        
        for i in range(len(title_path)):
            
            title = title_path[i].find_all('a')[0].text
            abstract = source.find_all('p',{'class':'lead line-6x2'})[i].find_all('a')[0].text
            abstract = re.sub('\s','',abstract)
            link = "https://www.aitimes.kr"+source.find_all('p',{'class':'lead line-6x2'})[i].find_all('a')[0].get('href')

            url_content = urlopen(link).read()
            url_content = bs4.BeautifulSoup(url_content,'html.parser')
            date = str(url_content.find_all('article',{'class':'item'})[0].find_all('li')[1].text[4:].split(' ')[0])
            date_year = datetime.datetime.strptime(date,'%Y.%m.%d')
            
            if date_year.year != today.year:
                stop=True
                break
                
            else:
                date = date_year
                df = pd.DataFrame({'title':[title],'abstract':[abstract],'url':[link],'date':[date],'engine':['인공지능신문']})
                df_list.append(df)
                
        page_num+=1
        
        if stop:
            break
    df = pd.concat(df_list)
    today_str = today.strftime('%Y%m%d')
    df.to_excel('AItimes_{}.xlsx'.format(today_str),index=False)
    root2 = tk.Tk()
    msg = messagebox.showinfo(title='Save msg',message='Save!')
    if msg == 'ok':
        root2.destroy()
    return df


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
