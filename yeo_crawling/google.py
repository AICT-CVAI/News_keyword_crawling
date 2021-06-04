import pandas as pd
import bs4
from urllib.request import urlopen
import urllib
import tkinter as tk
from tkinter import messagebox
import datetime
import time
import re
import numpy as np

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