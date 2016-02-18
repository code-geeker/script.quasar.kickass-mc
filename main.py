# coding: utf-8
__author__ = 'mancuniancol'

import common
from bs4 import BeautifulSoup
from quasar import provider

# this read the settings
settings = common.Settings()
# define the browser
browser = common.Browser()
# create the filters
filters = common.Filtering()


def extract_torrents(data):
    filters.information()  # print filters settings
    sint = common.ignore_exception(ValueError)(int)
    results = []
    cont = 0
    if data is not None:
        soup = BeautifulSoup(data, 'html5lib')
        links = soup.table.tbody.find_all('tr', {'class': ['odd', 'even']})
        for link in links:
            columns = link.select('td')
            if len(columns) == 6:
                name = columns[0].find('a', class_='cellMainLink').text  # name
                magnet = columns[0].find('a', {'title': 'Torrent magnet link'})['href']  # magnet
                size = columns[1].text  # size
                seeds = columns[4].text  # seeds
                peers = columns[5].text  # peers
                # info_magnet = common.Magnet(magnet)
                if filters.verify(name, size):
                    cont += 1
                    results.append({"name": name.strip(),
                                    "uri": magnet,
                                    # "info_hash": info_magnet.hash,
                                    "size": size.strip(),
                                    "seeds": sint(seeds),
                                    "peers": sint(peers),
                                    "language": settings.value.get("language", "en"),
                                    "provider": settings.name,
                                    "icon": settings.icon,
                                    })  # return the torrent
                    if cont >= int(settings.value.get("max_magnets", 10)):  # limit magnets
                        break
                else:
                    provider.log.warning(filters.reason)
    provider.log.info('>>>>>>' + str(cont) + ' torrents sent to Quasar<<<<<<<')
    return results


def search(query):
    info = {"query": query,
            "type": "general"}
    return search_general(info)


def search_general(info):
    info["extra"] = settings.value.get("extra", "")  # add the extra information
    query = filters.type_filtering(info, '%20')  # check type filter and set-up filters.title
    url_search = "%s/usearch/%s/?field=seeders&sorder=desc" % (settings.value["url_address"], query)
    provider.log.info(url_search)
    browser.open(url_search)
    return extract_torrents(browser.content)


def search_movie(info):
    info["type"] = "movie"
    if settings.value.get("language", "en") == 'en':  # Title in english
        query = info['title'].encode('utf-8')  # convert from unicode
        if len(info['title']) == len(query):  # it is a english title
            query += ' ' + str(info['year'])  # Title + year
        else:
            query = common.IMDB_title(info['imdb_id'])  # Title + year
    else:  # Title en foreign language
        query = common.translator(info['imdb_id'], settings.value["language"])  # Just title
    info["query"] = query
    return search_general(info)


def search_episode(info):
    if info['absolute_number'] == 0:
        info["type"] = "show"
        info["query"] = info['title'].encode('utf-8') + ' s%02de%02d' % (
            info['season'], info['episode'])  # define query
    else:
        info["type"] = "anime"
        info["query"] = info['title'].encode('utf-8') + ' %02d' % info['absolute_number']  # define query anime
    return search_general(info)


# This registers your module for use
provider.register(search, search_movie, search_episode)

del settings
del browser
del filters
