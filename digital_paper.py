import datetime
import time
import re
import pandas as pd
import bs4
from urllib.request import urlopen
import tkinter as tk
from tkinter import messagebox
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