"""
@File  : analyze_steam.py

@Author: no.1fansubgroup@gmail.com

@Date  : 2020/7/16

@Description  : analyze the data from steamdb
"""

import os
import pandas as pd
import numpy as np
import math
import os
import re
from urllib import request, error
# from bs4 import BeautifulSoup
from numpy import *
import matplotlib.pyplot as plt


def initialize_history():
    game_info = pd.DataFrame(columns=['rank', 'id', 'free', 'd1_abs', 'd3_abs'])
    game_info.to_csv('steam_history.csv')


# def collect_genre_and_recommend(steam_history):
#     game_info = pd.read_csv('steam_history.csv')
#     flag = 0
#     for record in steam_history:
#         rank_pattern = re.compile(r'(\d\d\d\d)_.*')
#         id_pattern = re.compile(r'\d\d\d\d_(\d*).*')
#         if record.find('free') != -1:
#             rank = re.findall(rank_pattern, record)[0]
#             app_id = re.findall(id_pattern, record)[0]
#             primary_genre, recommend_percentage = get_genre_and_recommend(app_id)
#             game_info[game_info['rank'] == rank]['primary_genre'] = primary_genre
#             game_info[game_info['rank'] == rank]['recommend_percentage'] = recommend_percentage
#         else:
#             rank = re.findall(rank_pattern, record)[0]
#             app_id = re.findall(id_pattern, record)[0]
#             primary_genre, recommend_percentage = get_genre_and_recommend(app_id)
#             game_info[game_info['rank'] == rank]['primary_genre'] = primary_genre
#             game_info[game_info['rank'] == rank]['recommend_percentage'] = recommend_percentage
#         flag += 1
#         if flag > 5:
#             break
#     game_info.to_csv('steam_history.csv')


def calculate_absolute(steam_history):
    game_info = pd.read_csv('steam_history.csv', index_col=0)
    for record in steam_history:
        rank_pattern = re.compile(r'(\d\d\d\d)_.*')
        id_pattern = re.compile(r'\d\d\d\d_(\d*).*')
        if record.find('free') != -1:
            rank = re.findall(rank_pattern, record)[0]
            app_id = re.findall(id_pattern, record)[0]
            game_info = game_info.append({'rank': rank,
                                          'id': app_id,
                                          'free': 'true',
                                          'd1_abs': 0,
                                          'd3_abs': 0,
                                          'd7_abs': 0},
                                         ignore_index=True)
        else:
            rank = re.findall(rank_pattern, record)[0]
            app_id = re.findall(id_pattern, record)[0]
            d1_abs, d3_abs, d7_abs = change_abs(record)
            game_info = game_info.append({'rank': rank,
                                          'id': app_id,
                                          'free': 'false',
                                          'd1_abs': d1_abs,
                                          'd3_abs': d3_abs,
                                          'd7_abs': d7_abs},
                                         ignore_index=True)
    game_info.to_csv('steam_history.csv')


def statistic_part():
    game_info = pd.read_csv('steam_history.csv', index_col=0)
    valid_data = game_info[game_info['d1_abs'] != 0]
    const_game = valid_data[valid_data['d1_abs'] <= 2]
    print(len(const_game) / len(valid_data))
    const_game = valid_data[valid_data['d3_abs'] <= 2]
    print(len(const_game) / len(valid_data))
    const_game = valid_data[valid_data['d7_abs'] <= 2]
    print(len(const_game) / len(valid_data))
    print(f"d1_abs mean = {valid_data['d1_abs'].mean()} max = {valid_data['d1_abs'].max()}")
    print(f"d3_abs mean = {valid_data['d3_abs'].mean()} max = {valid_data['d3_abs'].max()}")
    print(f"d7_abs mean = {valid_data['d7_abs'].mean()} max = {valid_data['d7_abs'].max()}")


def plot_part(steam_history):
    discounts = pd.DataFrame(columns=['discounts', 'd1_abs', 'd3_abs', 'd7_abs'])
    for record_filename in steam_history:
        # read record, extract price and players data as list
        record = pd.read_csv(f'../steamdb/{record_filename}').fillna(method='ffill')
        price = record['price']
        players = record['players']

        # set current price to 0 and create a 8 day sublist to calculate
        current_price = 0
        players_7d = []

        # enumerate the three parameter
        for date in range(len(price)):
            if price[date] < current_price:
                if date + 7 > len(price):
                    continue
                for i in range(8):
                    players_7d.append(players[date + i - 1])

                d1_abs = players_7d[1] / players_7d[0]
                d3_abs = (players_7d[1] + players_7d[2] + players_7d[3]) / (players_7d[0] * 3)
                d7_abs = (players_7d[1] + players_7d[2] + players_7d[3] + players_7d[4] +
                          players_7d[5] + players_7d[6] + players_7d[7]) / (players_7d[0] * 7)
                discounts = discounts.append({'discount': (current_price - price[date]) / current_price,
                                              'd1_abs': (d1_abs - 1) * 100,
                                              'd3_abs': (d3_abs - 1) * 100,
                                              'd7_abs': (d7_abs - 1) * 100},
                                             ignore_index=True)
                players_7d.clear()

            # set current price to the latest price and clear the sublist
            current_price = price[date]
    plt.scatter(discounts['discount'], discounts['d7_abs'])
    plt.savefig('discount_d7.png', dpi=600)


def main():
    data_path = r'D:\python\douban\steamdb'
    steam_history = os.listdir(data_path)
    initialize_history()
    calculate_absolute(steam_history)
    # collect_genre_and_recommend(steam_history)
    # statistic_part()
    # plot_part(steam_history)


# def get_genre_and_recommend(app_id):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
#         'cookie': '__cfduid=d474ef9194e131543de5dd0e4f4ee0d371593403954; '
#                   '_ga=GA1.2.2142496135.1593403954; _gid=GA1.2.1433550441.1594637627',
#         'accept': 'text/html,application/xhtml+xml,application/xml;'
#                   'q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
#     }
#     url = f'https://steamdb.info/app/{app_id}/info/'
#     request_steam = request.Request(url, headers=headers)
#     html = ""
#     try:
#         response = request.urlopen(request_steam)
#         html = response.read().decode("utf-8")
#     except error.URLError as e:
#         if hasattr(e, "code"):
#             print(e.code)
#         if hasattr(e, "reason"):
#             print(e.reason)
#     soup = BeautifulSoup(html, 'html.parser')
#     genre_pattern = re.compile(r'Primary Genre</td>\n<td><b>(.*)</b>.*</td>')
#     recommend_pattern = re.compile(r'review_percentage</td>\n<td>(.*)</td>')
#     genre = ''
#     recommend = ''
#     for item in soup.find_all('div', class_='tab-pane selected'):
#         genre_list = re.findall(genre_pattern, str(item))
#         if len(genre_list) == 0:
#             genre = 'other'
#         else:
#             genre = genre_list[0]
#
#     for item in soup.find_all('div', class_='tab-pane selected'):
#         recommend_list = re.findall(recommend_pattern, str(item))
#         if len(recommend_list) == 0:
#             recommend = 'other'
#         else:
#             recommend = recommend_list[0]
#     print(f'{app_id} genre: {genre} recommend: {recommend}')
#     return genre, recommend


def change_abs(record_filename):
    # initialize online players list
    d1_absolute = []
    d3_absolute = []
    d7_absolute = []
    d1_mean = 0
    d3_mean = 0
    d7_mean = 0

    # read record, extract price and players data as list
    record = pd.read_csv(f'../steamdb/{record_filename}').fillna(method='ffill')
    price = record['price']
    players = record['players']

    # set current price to 0 and create a 8 day sublist to calculate
    current_price = 0
    players_7d = []

    # enumerate the three parameter
    for date in range(len(price)):
        if price[date] < current_price:
            if date + 7 > len(price):
                continue
            for i in range(8):
                players_7d.append(players[date + i - 1])

            d1_absolute.append(players_7d[1] / players_7d[0])
            d3_absolute.append((players_7d[1] + players_7d[2] + players_7d[3]) / (players_7d[0] * 3))
            d7_absolute.append((players_7d[1] + players_7d[2] + players_7d[3] + players_7d[4] +
                                players_7d[5] + players_7d[6] + players_7d[7]) / (players_7d[0] * 7))
            players_7d.clear()

        # set current price to the latest price and clear the sublist
        current_price = price[date]
    # calculate the mean value from parameter list
    if len(d1_absolute) == 0:
        print(record_filename)
        return 0, 0, 0
    for d1 in d1_absolute:
        d1_mean += d1
    d1_mean /= len(d1_absolute)
    for d3 in d3_absolute:
        d3_mean += d3
    d3_mean /= len(d3_absolute)
    for d7 in d7_absolute:
        d7_mean += d7
    d7_mean /= len(d7_absolute)
    return d1_mean, d3_mean, d7_mean


def change_rel(record):
    return 0


if __name__ == '__main__':
    main()
