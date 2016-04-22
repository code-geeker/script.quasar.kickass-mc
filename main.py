# coding: utf-8
__author__ = 'mancuniancol'

import common
from bs4 import BeautifulSoup
from quasar import provider
import json,urllib
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
    provider.log.info(data)
    if data is not None:
        soup = BeautifulSoup(data, 'html5lib')
        links = soup.table.tbody.find_all('tr', {'class': ['odd', 'even']})
        for link in links:
            columns = link.select('td')
            if len(columns) == 6:
                name = columns[0].find('a', class_='cellMainLink').text.strip()  # name
                magnet = columns[0].find('a', {'title': 'Torrent magnet link'})['href']  # magnet
                size = columns[1].text.strip()  # size
                seeds = columns[4].text  # seeds
                peers = columns[5].text  # peers
                # info_magnet = common.Magnet(magnet)
                if filters.verify(name, size):
                    cont += 1
                    # magnet = common.getlinks(page)  # magnet
                    results.append({"name": name,
                                    "uri": magnet,
                                    # "info_hash": info_magnet.hash,
                                    "size": size,
                                    "seeds": sint(seeds),
                                    "peers": sint(peers),
                                    "language": settings.value.get("language", "en"),
                                    "provider": settings.name,
                                    "icon": settings.icon,
                                    })  # return the torrent
                    # if cont >= int(settings.value.get("max_magnets", 10)):  # limit magnets
                    if cont >= 100:  # limit magnets
                        break
                else:
                    provider.log.warning(filters.reason)
    provider.log.info('>>>>>>' + str(cont) + ' torrents sent to Quasar<<<<<<<')
    return results




def new_extract_torrents(data):
    filters.information()  # print filters settings
    sint = common.ignore_exception(ValueError)(int)
    results = []
    cont = 0
    if data is not None:
        jsondata = json.loads(data)
        # provider.log.info(jsondata)
        for link in jsondata['list']:
            if link is not None:
                name = link['title'].encode('utf-8').strip()
                provider.log.info(name)
                magnet = 'magnet:?xt=urn:btih:'+ link['hash']
                size = str(link['size'])
                seeds = sint(link['seeds'])
                peers = sint(link['leechs'])
                # info_magnet = common.Magnet(magnet)
                # if filters.verify(name, size):
                if name is not None:
                    cont += 1
                    # magnet = common.getlinks(page)  # magnet
                    results.append({"name": name,
                                    "uri": magnet,
                                    # "info_hash": info_magnet.hash,
                                    "size": size,
                                    # "seeds": sint(seeds),
                                    # "peers": sint(peers),
                                    "language": settings.value.get("language", "en"),
                                    "provider": settings.name,
                                    "icon": settings.icon,
                                    })  # return the torrent
                    # if cont >= int(settings.value.get("max_magnets", 10)):  # limit magnets
                    if cont >= 100:  # limit magnets
                        break
                else:
                    provider.log.warning(filters.reason)
    provider.log.info('>>>>>>' + str(cont) + ' torrents sent to Quasar<<<<<<<')
    return results


def search(query):
    info = {"query": query,
            "type": "general"}
    # return search_general(info)
    data = search_general(info)
    provider.log.info(data)
    return data


def search_general(info):
    info["extra"] = settings.value.get("extra", "")  # add the extra information
    query = filters.type_filtering(info, '%20')  # check type filter and set-up filters.title
    # url_search = "%s/usearch/%s/?field=seeders&sorder=desc" % (settings.value["url_address"], query)
    url_search = "%s/json.php?q=%s&field=seeders&sorder=desc&page=1" % (settings.value["url_address"], query)
    provider.log.info(url_search)
    browser.open(url_search)
    return new_extract_torrents(browser.content)


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


def search_season(info):
    provider.log.info(info)
    info["type"] = "show"
    info["query"] = info['title'].encode('utf-8') + ' %s %s' % (
        common.season_names[settings.value.get("language", "en")], info['season'])  # define query
    return search_general(info)


# This registers your module for use
if "false" == settings.value.get("episodes", "false"):
    provider.register(search, search_movie, search_episode, search_season)
else:
    provider.register(search, search_movie, search_season, search_season)

del settings
del browser
del filters
