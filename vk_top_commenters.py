# -*- coding: utf-8 -*-
import pandas as pd
import vk_api
import logging
from secrets import login, password

import xlsxwriter
import time
import json

## Глобальные переменные
# max_counts = 1 #пока что не работает, потом пофикшу, сейчас задается на входе в функцию ниже

FORMAT = '[%(asctime)s] %(levelname).1s %(message)s'
log_file = 'log.log'

## Некоторые сообщества и люди:
bt = '-57536014'  # БТ
mememe = '26546404'  # я сам
jail = '-92767252'  # Подслушано в Тюрьме

active_scan = bt
count_of_executes = 10


def auth_handler():
    """ При двухфакторной аутентификации вызывается эта функция.
    """

    # Код двухфакторной аутентификации
    key = input("Enter authentication code: ")
    # Если: True - сохранить, False - не сохранять.
    remember_device = True

    return key, remember_device


def parse_wall():
    """ Пример получения всех комментариев к записям со стены и их ранжирования
    по сумме лайков на каждого пользователя"""

    usersandlikes = pd.DataFrame(columns=['User', 'Posts', 'Likes'])
    toplikers = pd.DataFrame(columns=['User', 'Likes'], index=None)

    # login, password = login, password
    vk_session = vk_api.VkApi(
        login, password,

        auth_handler=auth_handler  # функция для обработки двухфакторной аутентификации
    )

    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    tools = vk_api.VkTools(vk_session)
    vk = vk_session.get_api()

    """ VkTools.get_all позволяет получить все объекты со всех страниц.
        Соответственно get_all используется только если метод принимает
        параметры: count и offset.
        Например может использоваться для получения всех постов стены,
        всех диалогов, всех сообщений, etc.
        При использовании get_all сокращается количество запросов к API
        за счет метода execute в 25 раз.
        Например за раз со стены можно получить 100 * 25 = 2500, где
        100 - максимальное количество постов, которое можно получить за один
        запрос (обычно написано на странице с описанием метода)

        https://vk.com/dev/wall.get

        Обратите внимание, идентификатор сообщества в параметре owner_id 
        необходимо указывать со знаком "-" 
        — например, owner_id=-1 соответствует идентификатору сообщества ВКонтакте API (club1)
        Для людей ставить впереди знаки "-" не нужно
    """

    wall = tools.get_all('wall.get', count_of_executes, {'owner_id': active_scan}, limit=1)

    """
    второй параметр тут отвечает за количество запросов в вк через execute. 1 запрос = 25 постов.
    """
    data = []
    for post in wall["items"]:
        data += parse_post(post, vk)
    usersandlikes = pd.DataFrame(data)
    print("Количество проанализированных комментариев", len(usersandlikes))
    result = groupbyusers(usersandlikes).reset_index()

    # print("Type of result ", type(result))
    # result['LinkToUser'] = "https://vk.com/id"+result['User'].astype(str)
    # result.rename(columns=result.iloc[:;0])
    # result.reindex(axis=0)
    result.iloc[:, 1] = "https://vk.com/id" + result.iloc[:, 1].astype(str)
    print(result.head(20))

    return result, vk

def parse_post(post, vk) -> list:
    parsed_post = []
    post_id = post['id']
    comments = vk.wall.getComments(owner_id=active_scan, post_id=post_id, need_likes=1)
    if comments is not None:
        parsed_post += parse_comments(comments, post_id)
    return parsed_post

def parse_comments(comments, post_id):
    parsed_comments = []
    for comment in comments['items']:
        if 'from_id' in comment and 'likes' in comment and 'text' in comment:
            parsed_comments.append({'User': comment['from_id'],
                                    'Posts': post_id,
                                    'Likes': comment['likes']['count'],
                                    'Text': comment['text']})
        else:
            print("test-syyyyt")
            print("Не удалось получить комментарий, возможно он удален или что-то пошло не так. ПостID: ",
                  post_id)
            logging.warning(f'Unexpected exception. Id: {post_id}')
    return parsed_comments






def groupbyusers(usersandlikes):
    ### тут топ коментов наших юзеров с лайками этих комментов
    topcomment = usersandlikes.filter(items=['User', 'Likes', 'Text'])
    topcomment = topcomment.sort_values('Likes', ascending=False).drop_duplicates(['User'])
    topcomment = topcomment.filter(items=['User', 'Text', 'Likes'])
    topcomment = topcomment.rename(columns={"Likes": "Most_likeable_comment", "Text": "Comment_text"})
    print("top comments", len(topcomment))

    def get_top_comment(usersandlikes):
        top_comments = usersandlikes.groupby('Text', as_index=False).aggregate({'Likes': 'count'}).sort_values(
            'Likes')
        return top_comments.loc[0]['Text'], top_comments.loc[0]['Likes']
    top_1 = get_top_comment(usersandlikes)
    print(f'Top 1 comment: {top_1[0]} with {top_1[1]} likes')

    usersandlikes2 = usersandlikes.filter(items=['User', 'Likes'])
    toplikers = usersandlikes2.groupby(['User']).sum()
    toplikers = toplikers.sort_values(by=['Likes'], ascending=False)

    usersandlikes3 = usersandlikes.filter(items=['User', 'Posts'])
    usersandlikes3 = usersandlikes3.groupby(['User']).count()

    print("Количество проанализированных постов", usersandlikes['Posts'].nunique())
    usersandlikes3 = usersandlikes3.sort_values(by=['Posts'], ascending=False)

    # объединим и получим итоговый фрейм с результатами
    result = pd.merge(toplikers, usersandlikes3, left_on='User', right_on='User', how='left')
    result = pd.merge(result, topcomment, left_on='User', right_on='User', how='left')

    # print(type(toplikers))
    # toplikers = toplikers.to_frame()
    # print(type(toplikers))
    # toplikers.to_csv('toplikers.csv', sep=';')
    # print(toplikers)
    return result


# toplikers = pd.DataFrame()
if __name__ == '__main__':
    logging.getLogger(log_file)
    logging.basicConfig(level=logging.INFO, format=FORMAT, filename=log_file)
    toplikers, vk = parse_wall()
    # print(usersandlikes)
    # usersandlikes.to_csv('usersandlikes.csv', sep=';')
    print(toplikers.columns)
    print(toplikers.head(1))
    toplikers.to_excel('toplikers.xlsx', sheet_name='Sheet_name_1', engine='xlsxwriter')
    # toplikers.to_csv('toplikers.csv', sep=';')
