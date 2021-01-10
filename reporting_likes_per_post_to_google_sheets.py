# -*- coding: utf-8 -*-

import logging
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
import apiclient.discovery
import pandas as pd
import vk_api
from secrets import login, password, sheet_id
from datetime import datetime, timedelta


# Define timedeltas:
from secrets import delta # 1 sec at local machine and 7 hours at productive stage
today = datetime.today()
week = timedelta(weeks=1)
twoweeksago = today - week - week

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


# CREDENTIALS TO SERVICE ACC
CREDSTOSERVICE = 'credentials.json'


# The ID and range of a sample spreadsheet.
spreadsheet_id = sheet_id
range_name = 'Likes_per_post!A3:D'

# Logging
FORMAT = '[%(asctime)s] %(levelname).1s %(message)s'
log_file = 'google_reporting.log'

bt = '-57536014'
mememe = '26546404'
jail = '-92767252'

active_scan = bt
count_of_executes = 5 # 12 is probably enough for 2 weeks of posting


def auth_handler():
    key = input("Enter authentication code: ")
    remember_device = True
    return key, remember_device


def get_session():
    vk_session = vk_api.VkApi(
        login, password,
        auth_handler=auth_handler)

    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        pass
    return vk_session


def get_wall(vk_session):
    tools = vk_api.VkTools(vk_session)
    wall = tools.get_all('wall.get', count_of_executes, {'owner_id': active_scan}, limit=1)
    return wall, tools


def parse_wall():
    """ Пример получения всех комментариев к записям со стены и их ранжирования
    по сумме лайков на каждого пользователя"""

    usersandlikes = pd.DataFrame(columns=['User', 'Posts', 'Likes'])
    toplikers = pd.DataFrame(columns=['User', 'Likes'], index=None)

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

    wall = tools.get_all('wall.get', count_of_executes, {'owner_id': active_scan}, limit=1)

    data = []
    for post in wall["items"]:
        data += parse_post(post, vk)
    usersandlikes = pd.DataFrame(data)
    result = groupbyposts(usersandlikes).reset_index()

    result.iloc[:, 0] = "https://vk.com/wall-57536014_" + result.iloc[:, 0].astype(str)
    result = result.values.tolist()
    return result, vk


def parse_post(post, vk) -> list:
    parsed_post = []
    post_id = post['id']

    comments = vk.wall.getComments(owner_id=active_scan, post_id=post_id, need_likes=1)

    if comments is not None:
        parsed_post += parse_comments(comments, post_id, vk)

    return parsed_post


def parse_comments(comments, post_id, vk):
    parsed_comments = []
    for comment in comments['items']:
        comment_id = comment['id']
        if 'from_id' in comment and 'likes' in comment and 'text' in comment:  # and replies = 0
            parsed_comments.append({'User': comment['from_id'],
                                    'Posts': post_id,
                                    'Likes': comment['likes']['count'],
                                    'Text': comment['text']})
            try:
                parsed_replies = parse_replies(post_id, comment_id, vk)
                for reply in parsed_replies:
                    parsed_comments.append({'User': reply['User'],
                                            'Posts': reply['Posts'],
                                            'Likes': reply['Likes'],
                                            'Text': reply['Text']})

                # print("appended correct, parsed_comments: ", parsed_comments)

            except:
                print("С реплаем что-то пошло не так, ветка комментария имеет айди: ", comment_id)

        else:
            print("Не удалось получить комментарий, возможно он удален или что-то пошло не так. ПостID: ",
                  post_id)
            logging.warning(f'Unexpected exception. Id: {post_id}')

    return parsed_comments

def parse_replies(post_id, comment_id, vk):
    """
    Далее мы извлекаем все респонсы для каждого комментария
    """
    replies = vk.wall.getComments(owner_id=active_scan, post_id=post_id, need_likes=1, comment_id=comment_id)

    parsed_replies = []
    for reply in replies['items']:
        comment_id = reply['id']
        if 'from_id' in reply and 'likes' in reply and 'text' in reply:  # and replies = 0
            parsed_replies.append({'User': reply['from_id'],
                                    'Posts': post_id,
                                    'Likes': reply['likes']['count'],
                                    'Text': reply['text']})
    return parsed_replies


def groupbyposts(usersandlikes):
    usersandlikes2 = usersandlikes.filter(items=['Posts', 'Likes'])
    toplikers = usersandlikes2.groupby(['Posts']).sum()
    result = toplikers.sort_values(by=['Likes'], ascending=False)
    return result

class Reporting:

    def __init__(self):
        pass

    def auth(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREDSTOSERVICE,
            ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive'])
        httpauth = credentials.authorize(httplib2.Http())
        service = apiclient.discovery.build('sheets', 'v4', http=httpauth)

        return service

    @staticmethod
    def get_values():

        # FIXME: Refactoring
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                    range=range_name).execute()

        posts_from_sheets = result.get('values', [])

        if not posts_from_sheets:
            # print('No data found.')
            logging.info('Failed to find posts in sheet')
        else:
            pass
        return posts_from_sheets

    @staticmethod
    def put_values():
        values = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": "Likes_per_post!A3:D",
                     "majorDimension":"ROWS",
                     "values": result}
                ]
            }
        ).execute()


    @staticmethod
    def put_last_updated():
        server_fixed_time = datetime.now() + delta
        d = str(datetime.date(server_fixed_time))
        t = str(datetime.time(server_fixed_time))
        stringest = ['Last Updated:', d, t]
        values = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": "Likes_per_post!A1:C1",
                     "majorDimension":"ROWS",
                     "values": [stringest]}
                ]
            }
        ).execute()

if __name__ == '__main__':
    logger = logging.getLogger(log_file)
    logging.basicConfig(level=logging.INFO, format=FORMAT, filename=log_file)


    vk_session = get_session()
    logger.info('VK parsed successfully')
    logger.info('Additional VK data parsed successfully')


    r = Reporting()
    service = r.auth()
    logger.info('Google Sheets auth successfully')

    result, vk = parse_wall()

    r.put_values()
    r.put_last_updated()
    logger.info('Process finished at %s' % {datetime.now() + delta})