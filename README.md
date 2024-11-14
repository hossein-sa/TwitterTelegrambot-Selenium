# Twitter Scraper Telegram Bot

This project is a Telegram bot that fetches tweets from a provided Twitter URL using Selenium WebDriver, then sends the tweets to a specified Telegram channel. The bot fetches the latest tweets and formats them for easy reading.

## Features

- **Fetch Tweets**: Provides a `/fetch <Twitter_URL>` command to scrape tweets from a Twitter user's profile or a tweet's URL.
- **Telegram Channel Integration**: Sends the scraped tweets directly to a specified Telegram channel.
- **MarkdownV2 Formatting**: Tweets are formatted with MarkdownV2 for better readability.
- **Rate Limiting**: Implements rate limiting to avoid sending requests to Twitter too frequently.
- **Headless Mode**: Runs Selenium in headless mode for optimal performance on servers.

## Requirements

- Python 3.7+
- ChromeDriver (for Selenium)
- `chromedriver-win64/chromedriver.exe` (or appropriate version for your platform)
- **Telegram Bot Token** (from @BotFather on Telegram)
- **Telegram Channel ID** (where tweets will be posted)


## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/twitter-scraper-bot.git
   cd twitter-scraper-bot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   - Create a `.env` file in the project root directory with the following content:
     ```env
     TELEGRAM_TOKEN=<Your_Telegram_Bot_Token>
     CHANNEL_ID=<Your_Telegram_Channel_ID>
     ```

4. Download the appropriate version of **ChromeDriver** from [here](https://sites.google.com/chromium.org/driver/), and place it in the `chromedriver-win64` directory (or the corresponding folder for your platform).


## Usage

- Start the bot:
  ```bash
  python bot.py
  ```

- In Telegram, send the `/start` command to the bot to begin interaction.
  
- Use the `/fetch <Twitter_URL>` command to scrape tweets and send them to the Telegram channel:
  ```plaintext
  /fetch https://twitter.com/elonmusk
  ```

## Example

1. The bot scrapes the tweets from the provided URL.
2. It formats the tweets and sends them to your Telegram channel.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

