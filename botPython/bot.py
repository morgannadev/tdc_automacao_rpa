from botcity.web import WebBot, Browser, By
from botcity.maestro import *
from botcity.plugins.discord import BotDiscordPlugin, EmbeddedMessage, Author, Footer, Color

# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False

def main():
    maestro = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()

    bot = WebBot()
    bot.headless = False
    bot.browser = Browser.FIREFOX
    bot.driver_path = r"resources\geckodriver.exe"

    try:

        maestro.alert(
            task_id=execution.task_id,
            title="Automação Iniciada",
            message="Automação iniciou a execução",
            alert_type=AlertType.INFO
        )

        bot.browse("https://dev.to/")
        
        devto_login(bot, maestro)
        find_articles(bot, maestro)

    except Exception as error:
        maestro.error(
            task_id=execution.task_id, 
            exception=error
        )

    finally:
        bot.wait(3000)
        bot.stop_browser()

        maestro.finish_task(
            task_id=execution.task_id,
            status=AutomationTaskFinishStatus.SUCCESS,
            message="Task Finished OK."
        )


def devto_login(bot: WebBot, maestro: BotMaestroSDK):
    login_button = bot.find_element('/html/body/header/div/div[2]/div/span/a', By.XPATH)
    login_button.click()

    email_input = bot.find_element('user_email', By.ID)
    email_input.send_keys(
        maestro.get_credential(
            label="login_teste", 
            key="email"
        )
    )

    password_input = bot.find_element('user_password', By.ID)
    password_input.send_keys(
        maestro.get_credential(
            label="login_teste", 
            key="password"
        )
    )

    bot.enter()
    bot.wait(2000)

def find_articles(bot: WebBot, maestro: BotMaestroSDK):
    search_input = bot.find_element('search-input', By.ID)
    search_input.send_keys("Python")

    bot.enter()
    bot.wait(2000)

    newest_button = bot.find_element('/html/body/div[6]/div/main/div/div[1]/nav[1]/ul/li[2]/a', By.XPATH)
    newest_button.click()

    author_name = bot.find_element('//*[@id="story-author-preview-trigger-2006029"]', By.XPATH).text
    author_link = bot.find_element('//*[@id="story-author-preview-trigger-2006029"]', By.XPATH).get_attribute('href')
    article_title = bot.find_element('//*[@id="article-link-2006029"]', By.XPATH).text
    article_link = bot.find_element('//*[@id="article-link-2006029"]', By.XPATH).get_attribute('href')
    read_time = bot.find_element('/html/body/div[6]/div/main/div/div[3]/div[2]/article[1]/div/div/div[2]/div[2]/div[2]/small', By.XPATH).text

    send_to_discord(maestro, author_name, author_link, article_title, article_link, read_time)

def send_to_discord(maestro: BotMaestroSDK, author_name, author_link, article_title, article_link, read_time):
    url = maestro.get_credential(label="webhook_teste", key="url")
    discord = BotDiscordPlugin(urls=url, username="Spidey Bot")

    # Instantiating the Embedded Message
    message = EmbeddedMessage(
        title = article_title,
        description = article_link,
        color = Color.BLUE
    )

    # Set the author
    message.author = Author(
        name = author_name,
        url = author_link,
        icon_url = 'https://avatars.githubusercontent.com/u/72993825?s=200&v=4'
    )

    # Set the footer
    message.footer = Footer(
        text = read_time,
        icon_url = 'https://avatars.githubusercontent.com/u/1525981?s=200&v=4'
    )

    discord.send_embedded_message(message)

if __name__ == '__main__':
    main()
