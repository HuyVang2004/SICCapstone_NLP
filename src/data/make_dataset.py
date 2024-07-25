
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from newspaper import Article
import pandas as pd
import time
import requests

driver = webdriver.Chrome()
driver.implicitly_wait(10)

# Hàm lấy liên kết từ menu
def get_menu():
    links_menu = []
    driver.get('https://cafef.vn/')

    menu_items = driver.find_elements(By.CSS_SELECTOR, '.acvmenu a, .menucategory_right a')

    for item in menu_items:
        try:
            link = item.get_attribute('href')
            if link and (link not in links_menu):
                links_menu.append(link)
        except NoSuchElementException as e:
            print(f"Error extracting menu info: {e}")
            pass

    return links_menu

# Hàm lấy liên kết các bài báo từ các liên kết menu
def get_articles(links_menu):
    links_article = []
    
    for link in links_menu:
        driver.get(link)
        news_links = driver.find_elements(By.CSS_SELECTOR, '.item a, .tagnamecate a, .list-news-main a')
        for l in news_links:
            href = l.get_attribute('href')
            if href and href not in links_article:
                links_article.append(href)
        
    return links_article

def download_article(links_article):
    temp_df = {
        'Title': [],
        'Text': [],
        'Summary': [],
        'Published_Date': [],
        'Source': []
    }

    for link in links_article:
        try:
            response = requests.get(link, timeout=10)  # Kiểm tra URL trước
            response.raise_for_status()  # Kiểm tra xem yêu cầu có thành công không

            article = Article(link)
            article.set_html(response.text)
            article.parse()
            article.nlp()

            temp_df['Title'].append(article.title)
            temp_df['Text'].append(article.text)
            temp_df['Summary'].append(article.summary)
            temp_df['Published_Date'].append(article.publish_date)
            temp_df['Source'].append(article.source_url)

        except Exception as e:
            print(f"Error processing article {link}: {e}")
            time.sleep(1)  # Thêm thời gian nghỉ giữa các yêu cầu để tránh quá tải server

    final_df = pd.DataFrame(temp_df)
    
    final_df.to_csv('data\\raw\\scraped_articles.csv', index=False)

if __name__ == '__main__':
    try:
        links_menu = get_menu() 
        links_art = get_articles(links_menu)
        download_article(links_art)
    finally:
        driver.quit() 

