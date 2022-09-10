from datetime import datetime

import requests
from bs4 import BeautifulSoup
from pony import orm

# Title: Save Product Prices with Python
# Tagline: Where's Cheapest?

"""
IMPORTANT. this is a basic example for beginners and as it is it will be quite brittle. To improve
I recommend users add some error handling for expected errors, like site unavailable, data missing
from element selectors, along with some basic logging. These things are not included in this version
to keep the level of entry as low as possible.
"""

# Set up the Database and define the model
db = orm.Database()
db.bind(provider='sqlite', filename='database.sqlite', create_db=True)


class Price(db.Entity):
    name = orm.Required(str)
    price = orm.Required(float)
    date_created = orm.Required(datetime)


# creates the table
db.generate_mapping(create_tables=True)


# web scraping functions
def gear4(session, headers):
    url = "https://www.gear4music.com/Recording-and-Computers/Shure-SM7B-Dynamic-Studio-Microphone/G6X"
    resp = session.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    data = (
        "gear4music",
        float(soup.select_one("span.info-row-price span.c-val").text),
    )
    return data


def amazon(session, headers):
    url = "https://www.amazon.co.uk/Shure-SM7B-Microphone/dp/B0002E4Z8M"
    resp = session.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    data = (
        "amazon",
        float(soup.select_one("div.a-box-group span.a-offscreen").text.replace("£", "")),
    )
    return data


def thomann(session, headers):
    url = "https://www.thomann.de/gb/shure_sm_7b_studiomikro.htm"
    resp = session.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    data = (
        "thomann",
        float(soup.select_one("div.price-wrapper div.price").text.replace("£", "").strip()),
    )
    return data


def export_data_to_csv():
    data = Price.select_by_sql("SELECT * FROM Price")
    for d in data:
        print(d)


# main function to run everything
def main():
    # set user agent header
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 '
                      'Safari/537.36'}
    # use a session
    s = requests.Session()
    # run each of our functions storing in a list
    data = [
        (gear4(s, headers)),
        (amazon(s, headers)),
        (thomann(s, headers)),
    ]
    print(data)
    # loop through the data to save to the sqlite db
    with orm.db_session:
        for item in data:
            Price(name=item[0], price=item[1], date_created=datetime.now())
        export_data_to_csv()


if __name__ == '__main__':
    main()
