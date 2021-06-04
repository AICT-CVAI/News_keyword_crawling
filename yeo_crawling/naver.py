import pandas as pd
import bs4
from urllib.request import urlopen
import urllib
import tkinter as tk
from tkinter import messagebox
import datetime
import time
import re


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
            stop = True
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
            naver_df.to_excel('''naver_{}_result.xlsx'''.format(searching),index=False)

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

    df = pd.concat(df_list)
    new = new.replace('|',' ')
    df.to_excel('''naver_{}_result.xlsx'''.format(new), index=False)