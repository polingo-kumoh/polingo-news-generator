import nltk
from crawler_en import CnnCrawler
from crawler_jp import NhkCrawler
from common.article_repository import ArticleRepository
from common.slack_bot import SlackAPI
from dotenv import load_dotenv
import os

if os.getenv('CI') != 'true':
    load_dotenv()


slack_token = os.environ["SLACK_TOKEN"]

host = os.environ["MYSQL_HOST"]
username = os.environ["MYSQL_USERNAME"]
password = os.environ["MYSQL_PASSWORD"]
database = os.environ["MYSQL_DATABASE"]

def main():
    # 최초 실행시 punkt 1번만 다운 필요
    nltk.download('punkt')

    slack_api = SlackAPI(slack_token)
    channel_id = slack_api.get_channel_id("polingo-logs")

    cnn_crawler = CnnCrawler()
    nhk_crawler = NhkCrawler()
    article_insertor = ArticleRepository(host, username, password, database)

    slack_api.post_message(channel_id, f"CRAWLER : News Crawling started")

    cnn_articles = cnn_crawler.crawl(5)
    nhk_articles = nhk_crawler.crawl(5)

    slack_api.post_message(channel_id, f"CRAWLER : News Crawling Completed : english - {len(cnn_articles)}, japanese - {len(nhk_articles)}")
    slack_api.post_message(channel_id, f"CRAWLER : News Crawling Save Started")
    try:
        for article in cnn_articles:
            article["language"] = "ENGLISH"
            article_insertor.insert(article)
        for article in nhk_articles:
            article["language"] = "JAPANESE"
            article_insertor.insert(article)
    except Exception as e:
        slack_api.post_message(channel_id, f"CRAWLER : News Crawl Save Failed")


    slack_api.post_message(channel_id, f"CRAWLER : News Crawling Save Completed : english - {len(cnn_articles)}, japanese - {len(nhk_articles)}")




if __name__ == '__main__':
    main()
