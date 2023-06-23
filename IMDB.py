import requests
from bs4 import BeautifulSoup


class Title:
    def __init__(self, title, genre, release_date, runtime, story, cover) -> None:
        self.title = title
        self.genre = genre
        self.release_date = release_date
        self.runtime = runtime
        self.story = story
        self.cover = cover
        self.fullTitle = self.title + " " + str(self.release_date)


class IMDB:
    def __init__(self) -> None:
        self.url = "https://www.imdb.com"
        self.searchAddress = "/search/title"

    def searchTitles(self, query):
        searchUrl = self.url+self.searchAddress+query
        payload = {}
        headers = {}
        response = requests.request(
            "GET", searchUrl, headers=headers, data=payload)
        soup = BeautifulSoup(response.content, 'html.parser')
        titles = []
        for title in soup.find_all('div', class_='lister-item'):
            try:
                release_date = title.find(
                    'span', class_="lister-item-year").text
            except:
                release_date = ""
            try:
                genre = title.find('span', class_="genre").text.strip()
            except:
                genre = ""
            try:
                runtime = title.find(
                    'span', class_="runtime").text.replace("min", "دقیقه")
            except:
                runtime = ""
            try:
                story = title.find('div', class_="lister-item-content").findAll("p", class_="text-muted")[
                    1].text.replace("»", "").replace("See full summary", "").strip()

            except:
                story = ""
            try:
                cover = title.find("img", class_="loadlate")["loadlate"].replace(
                    "._V1_UX67_CR0,0,67,98_AL_.jpg", ".jpg")
            except:
                cover = ""
            titles.append(Title(
                title.find('h3').find("a").text,
                genre,
                release_date,
                runtime,
                story,
                cover)
            )
        return titles
