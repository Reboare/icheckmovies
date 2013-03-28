#iCheckMovies in Python


##Introduction

A basic API providing access to the icheckmovies website.

##Usage
```python
from icheckmovies import ICM

icm = ICM("User", "Password")

via_imdb = icm.imdb("tt0137523")
via_url = icm.get_movie("Fight Club")
```

##Dependencies
[Requests](http://docs.python-requests.org/en/latest/)

[Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/)
