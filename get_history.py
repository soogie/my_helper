import requests
from bs4 import BeautifulSoup
from lxml import etree
import csv

def scrape_wordle_history():
    url = "https://www.rockpapershotgun.com/wordle-past-answers"
    
    # ブラウザからのアクセスを装うためのヘッダー
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # ページの取得
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # HTMLの解析
        soup = BeautifulSoup(response.content, 'html.parser')
        dom = etree.HTML(str(soup))
        
        # 指定されたXPathで要素を取得
        # ※ 指定のXPathは ul[2] (2番目の箇条書きリスト) を指しています
        xpath_query = '//*[@id="content_above"]/div[1]/main/div/div/article/div/div/ul[2]'
        ul_element = dom.xpath(xpath_query)

        if not ul_element:
            print("指定された要素が見つかりませんでした。サイトの構造が変わっている可能性があります。")
            return

        # <li>要素からテキスト（単語）を抽出
        words = [li.text.strip() for li in ul_element[0].xpath('./li') if li.text]

        if not words:
            # text属性で取れない場合は、子要素を含めた全テキストを取得
            words = ["".join(li.itertext()).strip() for li in ul_element[0].xpath('./li')]

        # カンマ区切りのCSVとして保存
        with open('history.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # 全単語を1行にカンマ区切りで書き込む場合
            writer.writerow(words)
            
        print(f"成功: {len(words)} 個の単語を history.csv に保存しました。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    scrape_wordle_history()