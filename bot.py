import os
import time
import logging
import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Configure bot token and channel ID securely
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

if not TELEGRAM_TOKEN or not CHANNEL_ID:
    raise ValueError("Please set TELEGRAM_TOKEN and CHANNEL_ID in your .env file.")

# Path to the ChromeDriver executable
driver_path = 'chromedriver-win64/chromedriver.exe'
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run Chrome in headless mode for servers

# Enable logging with more detailed output
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Thread pool for running Selenium operations asynchronously
executor = ThreadPoolExecutor(max_workers=5)

# Rate limiting variables
last_request_time = 0
REQUEST_DELAY = 10  # Minimum delay between requests to avoid rate limiting

async def start(update: Update, context):
    """Handler for the /start command."""
    await update.message.reply_text(
        "Hello! Send me the Twitter URL to fetch tweets using the /fetch command followed by the URL."
    )

async def fetch_tweets(update: Update, context):
    if len(context.args) == 0:
        await update.message.reply_text("Please provide a Twitter URL after the /fetch command.")
        return

    twitter_url = context.args[0]
    await update.message.reply_text("Fetching tweets...")

    # Run Selenium in a separate thread to avoid blocking the bot's main loop
    try:
        tweets_data = await asyncio.get_running_loop().run_in_executor(
            executor, scrape_tweets, twitter_url
        )

        if tweets_data:
            account_name, account_url, extracted_tweets = tweets_data
            bot = Bot(token=TELEGRAM_TOKEN)

            # Escape special characters for MarkdownV2
            def escape_markdown_v2(text):
                """Escape MarkdownV2 special characters."""
                return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

            # Escape account name and URL
            account_name = escape_markdown_v2(account_name)
            account_url = escape_markdown_v2(account_url)

            for tweet in extracted_tweets[:5]:  # Sending the first 5 tweets
                # Escape tweet text
                tweet = escape_markdown_v2(tweet)

                # Construct message with link preview enabled
                message = f"{tweet}\n\n— [{account_name}]({account_url})"
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=message,
                    parse_mode='MarkdownV2',
                    disable_web_page_preview=True  # Enable link previews
                )
            await update.message.reply_text("Tweets sent to the channel.")
        else:
            await update.message.reply_text("No tweets found or an error occurred.")

    except Exception as e:
        logger.error(f"Error fetching tweets: {e}")
        await update.message.reply_text("An unexpected error occurred while fetching tweets.")

def scrape_tweets(twitter_url):
    global last_request_time
    current_time = time.time()
    driver = None  # Ensure the driver is properly initialized before usage.

    try:
        # Enforce rate limiting
        if current_time - last_request_time < REQUEST_DELAY:
            wait_time = REQUEST_DELAY - (current_time - last_request_time)
            logger.warning(f"Rate limiting active, waiting {wait_time:.1f} seconds.")
            time.sleep(wait_time)

        # Selenium scraping logic...
        service = Service(driver_path)  # Initialize the Service with the path to ChromeDriver
        driver = webdriver.Chrome(service=service, options=options)  # Initialize the WebDriver

        driver.get(twitter_url)
        time.sleep(5)  # Allow time for the page to load

        # Log the page source for debugging (optional)
        print(driver.page_source)

        # Try to extract tweets
        tweets = driver.find_elements(By.XPATH, '//div[@data-testid="tweetText"]')
        if not tweets:
            raise ValueError("No tweets found on this page.")

        extracted_tweets = [tweet.text for tweet in tweets]
        account_name_element = driver.find_element(By.XPATH, '//div[@data-testid="UserName"]//span')
        account_name = account_name_element.text
        account_url = twitter_url.split('/status/')[0]  # Base URL of the Twitter account

        last_request_time = time.time()  # Update last request time
        return account_name, account_url, extracted_tweets

    except Exception as e:
        logger.error(f"An error occurred while scraping: {e}")
        return None

    finally:
        if driver:
            driver.quit()  # Ensure driver is properly quit to avoid hanging processes.

def main():
    # Set up the Telegram application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("fetch", fetch_tweets))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
