#!/usr/bin/env python
from Kiwi2 import Delegates
from Kiwi2.Widgets.List import List, Column
from Kiwi2.initgtk import gtk

class NewsItem:
    """An instance that holds information about a news article."""
    def __init__(self, title, author, url):
        self.title, self.author, self.url = title, author, url

# Assemble friendly Pigdog.org news into NewsItem instances so they can
# be used in the CListDelegate
news = [
 NewsItem("Smallpox Vaccinations for EVERYONE", "JRoyale",
          "http://www.pigdog.org/auto/Power_Corrupts/link/2700.html"),
 NewsItem("Is that uranium in your pocket or are you just happy to see me?",
          "Baron Earl",
          "http://www.pigdog.org/auto/bad_people/link/2699.html"),
 NewsItem("Cut 'n Paste", "Baron Earl",
          "http://www.pigdog.org/auto/ArtFux/link/2690.html"),
 NewsItem("A Slippery Exit", "Reverend CyberSatan",
          "http://www.pigdog.org/auto/TheCorporateFuck/link/2683.html"),
 NewsItem("Those Crazy Dutch Have Resurrected Elvis", "Miss Conduct",
          "http://www.pigdog.org/auto/viva_la_musica/link/2678.html")
]

# Specify the columns: one for each attribute of NewsItem, the URL
# column invisible by default
my_columns = [ Column("title", sorted=True), 
               Column("author"), 
               Column("url", title="URL", visible=False) ]

kiwilist = List(my_columns, news)
slave = Delegates.SlaveDelegate(toplevel=kiwilist)
slave.show_all()
gtk.main()
