<<<<<<< HEAD
<p style="display:flex;justify-content:end;">
  <img src="https://img.shields.io/badge/-Python-F2C63C.svg?logo=python&style=for-the-badge">
</p>

## ◾️使い方
### ①pipでインストール

```python: python
pip install selenium
pip install requests
pip install lxml
pip install pandas
pip install tqdm
```
### ②下記配列変数の変更

```python: python
=======
このコードはポートフォリオとしてgit上にあげたものです
スクレイピングのコードですので、使用の際は相手のサイトに負荷がかからないよう気をつけて使用して下さい

①pipでパッケージをインストール
②下記配列変数の変更
>>>>>>> c571b74 (readme追加)
###検索ワードの設定###
url_search_terms = ["データ収集","スクレイピング",...] #キーワード検索
another_content_search_terms = ["PL","PM","株式市場",...] #本文内に検索ワードがあるかどうか

###除外ワードの設定###
title_avoid = ["食","採用","基盤",...] #就職情報のタイトルに含まれるワードを除外
avoid_terms = ["派遣","SES","現場","常駐",...] #就職情報の本文に含まれるワードを除外
avoid_search_array = ["自動車","飲食","SES"] #求人ボックスの除外ワード検索
<<<<<<< HEAD
```

### ③処理完了後、csvが自動で開きます

### ※追加機能
avoid_url_flgをTrueにすると、前回のデータの差分のみを取得できます
```python: python
avoid_url_flg = True #True or False
```
=======

③処理完了後、csvが自動で開きます

詳細は以下を参照して下さい
https://github.com/meitekku/scraping/tree/master
>>>>>>> c571b74 (readme追加)
