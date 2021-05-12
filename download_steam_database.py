"""
@File  : download_steam_database.py

@Author: no.1fansubgroup@gmail.com

@Date  : 2020/7/12

@Description  : to collect data from steam database
"""
from bs4 import BeautifulSoup
from urllib import request, response, error
from openpyxl import load_workbook
import json
import re
import pandas as pd
import time
import math


def main():
    game_ids = get_1000('steam1000.html')
    for i in range(596, 600):
        request_api(app_id=game_ids[i], rank=str(i + 1).zfill(4))

    # request_api(app_id=696370, rank=str(10).zfill(4))


# read the full list page and return top 1000 game ids
def get_1000(list_page):
    game_id = []
    soup = BeautifulSoup(open(list_page, encoding='utf-8'), 'html.parser')
    id_pattern = re.compile(r'data-appid="(.*)" data-cache')
    for item in soup.find_all('tr'):
        app_id = re.findall(id_pattern, str(item))
        if len(app_id) == 0:
            continue
        game_id.append(app_id[0])
    return game_id


def set_hour_to_8(raw_time):
    struct_time = time.localtime(raw_time)
    return time.mktime((struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday, 8, 0, 0,
                        struct_time.tm_wday, struct_time.tm_yday, 0))


def pass_day(time_start, time_end):
    return math.ceil((time_end - time_start) / 86400)


# from the api url request history player data
def request_api(app_id, rank):
    # headers needed to request api
    players_url = f'https://steamdb.info/api/GetGraph/?type=concurrent_max&appid={app_id}'
    price_url = f'https://steamdb.info/api/GetPriceHistory/?appid={app_id}&cc=cn'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/83.0.4103.116 Safari/537.36,',
        'cookie': '__cfduid=d474ef9194e131543de5dd0e4f4ee0d371593403954; _ga=GA1.2.2142496135.1593403954; '
                  '_gid=GA1.2.1433550441.1594637627,',
        'accept': 'application/json, text/javascript, */*; q=0.01,',
        'referer': 'https://steamdb.info/app/271590/graphs/'
    }

    # try to fetch data from api as json string
    request_players = request.Request(players_url, headers=headers)
    request_price = request.Request(price_url, headers=headers)
    players_json = ''
    price_json = ''
    try:
        response_players = request.urlopen(request_players)
        response_price = request.urlopen(request_price)
        players_json = response_players.read().decode("utf-8")
        price_json = response_price.read().decode("utf-8")
    except error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)

    # extract online players data from the json string
    # extract online players data from the json string
    history_players = json.loads(players_json)['data']
    players_start = history_players['start']
    interval = history_players['step']
    online_players = history_players['values']

    # if the game is always free like dota2, save it as an empty file
    history_price = json.loads(price_json)['data']['final']

    if len(history_price) == 0:
        free_pd = pd.DataFrame({'date': [],
                                'players': [],
                                'price': []})
        free_pd.to_csv(f'{rank}_{app_id}_free.csv')

        print(f'The {rank} game data has been saved successfully')
        return

    # extract price data from json string and turn it into a continuous list, using 08:00:00 7/14/2020 as end time
    end_time = 1594684800
    price_list = []
    for i in range(len(history_price) - 1):
        price_start = set_hour_to_8(history_price[i][0] / 1000)
        price_end = set_hour_to_8(history_price[i + 1][0] / 1000)
        for j in range(pass_day(price_start, price_end)):
            price_list.append(history_price[i][1])
    latest_interval = pass_day(history_price[-1][0] / 1000, end_time)
    for j in range(latest_interval + 1):
        price_list.append(history_price[-1][1])

    # find the first date with both players and price data
    price_start = history_price[0][0] / 1000
    start_date = set_hour_to_8(max(price_start, players_start))
    valid_records = pass_day(start_date, end_time) + 1

    # clean the data, trim to save records with both price and players
    time_table = []
    players_trimmed = []
    price_trimmed = []
    for i in range(valid_records):
        time_table.append(time.localtime(start_date + i * interval))
        players_trimmed.append(online_players[-(valid_records - i)])
        price_trimmed.append(price_list[-(valid_records - i)])

    time_pd = pd.DataFrame({'date': time_table,
                            'players': players_trimmed,
                            'price': price_trimmed})
    time_pd.to_csv(f'{rank}_{app_id}.csv')
    print(f'The {rank} game data has been saved successfully')


if __name__ == '__main__':
    main()
