from pyrogram import Client, filters
from pyrogram.types import InlineQuery, InlineQueryResultPhoto, InlineQueryResultArticle, InputTextMessageContent
import requests
from bs4 import BeautifulSoup

# function to scrape the drama synopsis and poster
def scrape_drama_info(drama_name):
    url = f"https://mydramalist.com/search?q={drama_name}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    results = soup.find_all("div", {"class": "box-search"})

    for result in results:
        title_element = result.find("h6", {"class": "text-primary"})
        if title_element and drama_name.lower() in title_element.text.lower():
            drama_url = "https://mydramalist.com" + title_element.find("a")["href"]
            drama_response = requests.get(drama_url)
            drama_soup = BeautifulSoup(drama_response.content, "html.parser")
            synopsis = drama_soup.find("div", {"class": "show-synopsis"}).text.strip()
            poster_url = drama_soup.find("div", {"class": "poster"}).find("img")["src"]
            return synopsis, poster_url

# define the Ultroid plugin
@Client.on_inline_query()
async def search_drama(client, query):
    if query.query == "":
        return
    results = []
    drama_name = query.query.lower()

    # scrape the drama synopsis and poster
    synopsis, poster_url = scrape_drama_info(drama_name)

    # create an InlineQueryResultPhoto object for the drama poster
    poster_result = InlineQueryResultPhoto(
        title=drama_name,
        description=synopsis,
        thumb_url=poster_url,
        photo_url=poster_url
    )
    results.append(poster_result)

    # create an InlineQueryResultArticle object for the drama synopsis
    synopsis_result = InlineQueryResultArticle(
        title=drama_name,
        description="Click to view the drama synopsis",
        input_message_content=InputTextMessageContent(synopsis)
    )
    results.append(synopsis_result)

    await query.answer(results, cache_time=1)
