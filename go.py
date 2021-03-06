import sqlite3
import time
import re
import collections
import os
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
kuutu_db = sqlite3.connect("kkutu.db")
cur = kuutu_db.cursor()
chromeDriverPath = os.getcwd()+"/chromedriver" #윈도우를 사용하시면 .exe를 붙여야합니다.
driver = webdriver.Chrome(chromeDriverPath)
driver.get('https://kkutu.co.kr/login?before=https://kkutu.co.kr')



while 1:
    html = driver.page_source
    soup = BeautifulSoup(html, 'html')
    word = soup.find_all('div', 'ellipse history-item expl-mother')
    if len(word) > 0:
        for div in soup.find_all("div", {'class': 'history-mean'}):
            div.decompose()
        for div in soup.find_all("label", {'class': "history-class"}):
            div.decompose()
        for div in soup.find_all("div", {'class': 'expl'}):
            div.decompose()
        for div in soup.find_all("label", {'class': 'word-m3-body'}):
            div.decompose()
        word = soup.find_all('div', 'ellipse history-item expl-mother')
        word = word[0].text
        check = 0
        row = cur.execute("select * from test where word = '"+str(word)+"'")
        for i in row:
            cur.execute("update test set use = 1 where word = '"+str(word)+"'")
            check = 1
            break
        if check == 0:
            cur.execute("insert into test values('" +
                        str(word)+"','"+str(len(word))+"','1')")
            kuutu_db.commit()
            print(word + " 단어가 db에 저장되었습니다.")

    soup2 = BeautifulSoup(driver.page_source, 'html')
    soup_turn = soup2.find_all('div', 'game-input')
    while str(soup_turn).find('block') >= 0:
        word = soup.select(
            '#GameBox > div > div.game-head > div.jjoriping > div > div.jjo-display.ellipse')
        word = word[0].text
        print(word)
        word_len1 = len(word)
        word = word.replace(")", "")
        word = word.replace("(", "")
        word_len2 = len(word)
        if word_len1 > word_len2:
            print("2개의 선택지" + word)
            kkk = cur.execute("SELECT * FROM test WHERE use = 0 AND word LIKE '" +
                              word[0] + "%' OR word LIKE '" + word[-1] + "%' ORDER BY leng DESC LIMIT 1")
            for kk in kkk:
                driver.find_element_by_xpath(
                    '/html/body/div[3]/div[32]/div/input').send_keys(kk[0])
                cur.execute("update test set use = 1 where word ='"+kk[0]+"'")
                use_word = kk[0]
                kuutu_db.commit()
                driver.find_element_by_xpath(
                    '/html/body/div[3]/div[32]/div/button').click()
                break
            time.sleep(0.15)
            soup2 = BeautifulSoup(driver.page_source, 'html')
            soup_turn = soup2.find_all('div', 'game-input')
            error_text = soup2.select(
                '#GameBox > div > div.game-head > div.jjoriping > div > div.jjo-display.ellipse > label')
            if len(str(error_text)) > 2:
                cur.execute("delete from test where word = '"+use_word+"'")
                print(use_word + " 단어가 db에서 삭제되었습니다.")
                kuutu_db.commit()

        else:
            print("1개의 선택지" + word)
            if word[-1] == '릇' or word[-1] == '늣':
                kkk = cur.execute(
                    "SELECT * FROM test WHERE use=0 AND word LIKE '" + "늣" + "%' ORDER BY leng DESC LIMIT 1")
                for kk in kkk:
                    driver.find_element_by_xpath(
                        '/html/body/div[3]/div[32]/div/input').send_keys(kk[0])
                    use_word = kk[0]
                    cur.execute(
                        "update test set use = 1 where word ='"+kk[0]+"'")
                    kuutu_db.commit()
                    driver.find_element_by_xpath(
                        '/html/body/div[3]/div[32]/div/button').click()
                    break
                time.sleep(0.15)

            else:
                kkk = cur.execute("SELECT * FROM test WHERE use=0 AND word LIKE '" +
                                  word[-1] + "%' ORDER BY leng DESC LIMIT 1")
                for kk in kkk:
                    driver.find_element_by_xpath(
                        '/html/body/div[3]/div[32]/div/input').send_keys(kk[0])
                    use_word = kk[0]
                    cur.execute(
                        "update test set use = 1 where word ='"+kk[0]+"'")
                    kuutu_db.commit()
                    driver.find_element_by_xpath(
                        '/html/body/div[3]/div[32]/div/button').click()
                    break
                time.sleep(0.15)
                soup2 = BeautifulSoup(driver.page_source, 'html')
                soup_turn = soup2.find_all('div', 'game-input')
                error_text = soup2.select(
                    '#GameBox > div > div.game-head > div.jjoriping > div > div.jjo-display.ellipse > label')
                if len(str(error_text)) > 2:
                    cur.execute("delete from test where word = '"+use_word+"'")
                    print(use_word + " 단어가 db에서 삭제되었습니다.")
                    kuutu_db.commit()
    if len(word) == 0:
        cur.execute("update test set use = 0 where use = 1")
        kuutu_db.commit()
kuutu_db.close()
