from bs4 import BeautifulSoup
from requests import get
import requests

class ICM(object):
    """A global class to provide an easy API to various functions, and a convenient
    way of using sessions without constantly passing it around.
    """
    session = None

    def __init__(self, user=None, password=None):
        if user != None and password != None:
            self.session = login(user, password)

    def get_movie(self, url):
        """Returns a Movie object exposing parts"""
        request = get(url, session = self.session)
        cont = request.content
        mov = Movie(url)
        mov._parse(cont)
        return mov

    def imdb(self, ttid):
        url = "http://www.icheckmovies.com/search/movies/?query=%s"%ttid
        return get_movie(url, self.session)

    def user(self, name):
        name = "+".join(name.split())
        url = "http://www.icheckmovies.com/profiles/"+name
        cont = get(url).content
        user = User(url)
        user._parse(cont)
        return user


class User(object):
    def __init__(self, url):
        self.url = url

    def _parse(self, cont):
        mapping = User.parse(cont)
        for key, value in mapping.iteritems():
            setattr(self, key, value)


    @staticmethod
    def parse(cont):
        mapping = {}
        soup = BeautifulSoup(cont)
        profile = soup.body.find("div", {"id":"profileBox"}).a.text
        if profile.strip() == "Login":
            loggedin = False
        else:
            loggedin = True

        stats_area = soup.find("div", {"class" : "span-7"})
        stats_vals = stats_area.findAll("dd")
        indices_matches = ["account", "joined", "checks", "rank", 
                           "title", "awards", "favorites", "dislikes",
                           "owned"]
        
        for key, val in zip(indices_matches, stats_vals):
            value = val.text
            mapping[key] = value if value.isdigit() == False else int(value)
        mapping['rank'] = int(mapping['rank'][1:])
        
        if loggedin == True:
            mapping["compatibility"] = soup.find("div", {"class":"compatibility"}).span.strong.text
            shared = soup.findAll("div", {"class" : "span-7"})[1].p.findAll("strong")
            
            mapping["shared"] = {"movies" : int(shared[0].text.split(" ")[0]),
                                 "favorites" : int(shared[1].text.split(" ")[0]),
                                 "dislikes" : int(shared[2].text.split(" ")[0])
                                 }
        return mapping

class Movie(object):
    """
    title = "Unknown"
    imdb = "Unknown"
    lists = []

    year = 0
    runtime = 0
    director = []
    genres = []
    rating = 0.0
    votes = 0
    checks = 0
    favs = 0
    dislikes = 0

    checked = False
    disliked = False
    favourited = False
    in_watchlist = False
    owned = False"""

    def __init__(self, url):
        self.url = url
        self.attributes = ["title",  "imdb", "lists", "year", "runtime", "director", "genres", "rating", "votes",
                            "checks", "favs", "dislikes", "checked", "disliked", "favourited", "in_watchlist", "owned"]
        for each in self.attributes:
            setattr(self, each, None)
        

    def _parse(self, cont):
        attrs = Movie.parse(cont)
        for key, value in attrs.iteritems():
            setattr(self, key, value)

    @staticmethod
    def parse(cont):
        attributes = {}
        soup = BeautifulSoup(cont)
        #Extract the main block containing all the content
        main = soup.find("div", id = "content")
        #Extract the title and year
        title, year = main.div.div.h1.text.split("(")
        attributes['year'] = int(year.strip(")   "))
        attributes['title'] = title.strip(" ")
        #Extract the main info
        info = soup.find("div", {"class" : "span-7 last"})
        #Get rid of values we don't want
        keys = info.dl.find_all("dt")[1:-2]
        keys = [key.string.lower() for key in keys]
        values = info.dl.find_all("dd")[1:-2]
        vals = []

        for each in values:
            if each.string == None:
                a = each.find_all("a")
                vals.append([each.string for each in a])
            else:
                vals.append(each.string)

        for key, value in zip(keys, vals):
            attributes[key] = value

        attributes.update(Movie._titlebar(soup))
        attributes.update(Movie._lists(soup))

        attributes["imdb"] = soup.find("a",class_="icon iconSmall iconIMDB external")['href']
        return attributes

    @staticmethod
    def _titlebar(souped):
        top = souped.find("div", id = "content")
        attrs = top.div.find("div", id="movie")['class']
        final = {
        "disliked": False if "nothated" in attrs else True,
        "checked": False if "unchecked" in attrs else True,
        "owned": False if "notowned" in attrs else True,
        "favourited": False if "notfavorite" in attrs else True
        }
        return final

    @staticmethod
    def _lists(souped):
        first = souped.find("ol", class_ = "itemList itemListCompact clearfix")
        titles = first.find_all("h3")
        final = {"lists":[h.a['href'] for h in titles]}
        return final

    def __iter__(self):
        return ((x,(getattr(self, x))) for x in self.attributes)

    
def login(self, user, password):
        """Returns a requests.Session object with the user logged into
        the icm website.  Assuming all the details are correct it 
        will return a session that will allow you to be logged in.
        """
        
        session = requests.session()
        login_data = {
                      'login[username]': user,
                      'login[password]': password,
                      'submit': 'login',
                      }

        session.post("https://www.icheckmovies.com/login/", data=login_data)
        return session


if __name__ == "__main__":
    for each in ICM().get_movie("http://www.icheckmovies.com/movies/fight+club/"):
        print each


