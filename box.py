from selenium import webdriver
import ssl
import traceback
import time
import requests
import lxml.html
import pandas as pd
import subprocess
from selenium.webdriver.common.by import By
import csv
from tqdm import tqdm

start_time = time.time()

#キーワード検索する(ワード数が多くなると比例して時間がかかるので注意)
url_search_terms = ["データ収集","スクレイピング","データエンジニア","投資分析","金融市場","個人投資家","資産運用","Fintech","投資家","金融工学","機関投資家","金融機関","内製化","創業期"]
#本文内に検索ワードがあるかどうかをチェック
another_content_search_terms = ["PL","PM","株式市場"]

#就職情報のタイトルに含まれる場合に除外するワード
title_avoid = ["食","採用","基盤"]
#就職情報の本文に含まれる場合に除外するワード
avoid_terms = ["派遣","SES","現場","常駐","犯罪","音楽"]
#実際に求人ボックスで検索する際に除外するワード
avoid_search_array = ["自動車","犯罪","ゲーム","飲食","SES","医療","広告","家電","ゲーム","建設","スマホアプリ","SaaS","現場","クラウド"]

#以前のデータがあり、新着情報だけを取得したい場合はTrueにする
avoid_url_flg = False

content_search_terms = url_search_terms + another_content_search_terms
user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
header = {'User-Agent': user_agent}
salary = "6000000"
avoid_search = "%20not:".join(avoid_search_array)
url_origin = "https://xn--pckua2a7gp15o89zb.com/adv/?keyword=%E3%82%A8%E3%83%B3%E3%82%B8%E3%83%8B%E3%82%A2%20{}%20"+avoid_search+"&area=%E6%9D%B1%E4%BA%AC%E9%83%BD&e=1&p=3&pl="+salary+"&pg={}"

urls = []
#既に取得したURLを読み込む
def read_csv(file_name):
    urls = []
    with open(file_name, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            url = row['URL']
            urls.append(url)
    return urls

avoid_urls = []
if avoid_url_flg:
    avoid_urls = read_csv("box.csv")

for term in url_search_terms:
    sum_num = 0
    loop_num = 0
    append_num = 0
    all_num = 0
    while True:
        loop_num += 1
        url_check = url_origin.format(term,loop_num)

        # Requestsを利用してWebページを取得する
        response = requests.get(url_check,headers=header)
        response.encoding = response.apparent_encoding

        # lxmlを利用してWebページを解析する
        html = lxml.html.fromstring(response.text)
        anchors = html.xpath(".//h2[contains(@class, 'title')]/a")
        len_urls = len(anchors)
        sum_num += len_urls
        if len(anchors) == 0:
            print("【"+term+"】のサイト数:"+str(append_num))
            sum_num = 0
            append_num = 0
            break

        for a in anchors:
            url = a.attrib["href"].strip()
            title = a.text_content().strip()

            #本文内にNGワードがある場合は除外
            avoid_mached_terms = [term for term in avoid_terms if term in title] or any(av_term in title for av_term in title_avoid)
            if avoid_mached_terms:
                continue

            #URLが重複していない場合は検索対象にする
            if url not in urls and "https://xn--pckua2a7gp15o89zb.com"+url not in avoid_urls:
                urls.append(a.attrib["href"])
                append_num += 1

#本文内に検索ワードがあるかどうかをチェック
def find_avoid_terms_in_text(text, terms):
    matched_terms = []
    for term in terms:
        if term in text:
            matched_terms.append(term)
    return matched_terms

print("クローリングするurlの数"+str(len(urls)))
print("--------クローリングを開始します--------")
job_data = []
for i,anchor in tqdm(enumerate(urls), total=len(urls)):
    check_url = "https://xn--pckua2a7gp15o89zb.com"+anchor
    response = requests.get(check_url,headers=header)
    html = lxml.html.fromstring(response.text)

    job_text_ele = html.xpath(".//div[@class='p-detail']/section[@class='c-panel']")
    job_text = ""
    if len(job_text_ele) > 0:
        job_text = job_text_ele[0].text_content()

    title_ele = html.xpath(".//p[@class='p-detail_head_title']")
    if len(title_ele) == 0:
        continue

    title = title_ele[0].text_content()

    #本文内に該当の条件があるか
    matched_terms = [term for term in content_search_terms if term in job_text]
    #本文内にNGワードがある場合は除外
    not_matched_ng = not any(term in job_text for term in avoid_terms)
    #本文中に「エンジニア」か「プログラマー」が含まれている場合のみ抽出
    match_programmer = "エンジニア" in title or "エンジニア" in job_text or "プログラ" in job_text
    if matched_terms and not_matched_ng and match_programmer:
        #マッチした用語を抽出
        sorted_matched_terms = [term for term in url_search_terms if term in matched_terms]
        matched_terms_str = ",".join(sorted_matched_terms[:4])

        company_name = salary = ""
        if len(title) > 30:
            title = title[:30]
        company_ele = html.xpath(".//section/div[@class='p-detail_head']/p[@class='p-detail_company']")

        if len(company_ele) > 0:
            company_name = company_ele[0].text_content()
        if company_name == "":
            continue
            
        salary_ele = html.xpath(".//section/div[@class='p-detail_head']/ul/li[@class='p-detail_summary c-icon c-icon--C']")
        if len(salary_ele) > 0:
            salary = salary_ele[0].text_content().replace("給与","").strip()

        job_data.append([matched_terms_str, title, check_url, salary, company_name])

df = pd.DataFrame(job_data, columns=['Matched Terms', 'Job Title', 'URL', 'Salary', 'Company Name'])
df['Min Salary'] = df['Salary'].str.extract(r'(\d+)(?=万円～)').astype(float)
#給料順に並び替え
df = df.sort_values(by='Min Salary', ascending=False)
df.drop('Min Salary', axis=1, inplace=True)
df['Matched Terms'] = df['Matched Terms'].apply(lambda x: ','.join(sorted(x.split(','), key=lambda y: url_search_terms.index(y) if y in url_search_terms else len(url_search_terms))))
df.to_csv("box.csv", encoding='utf_8_sig', index=False)
subprocess.call(['open', "box.csv"])

# タイマーの停止と経過時間の計算
end_time = time.time()
elapsed_time = end_time - start_time

# 経過時間を表示（時間と分）
elapsed_hours = int(elapsed_time // 3600)
elapsed_minutes = int((elapsed_time % 3600) // 60)
print(f"クローリング時間: {elapsed_hours}時間{elapsed_minutes}分")