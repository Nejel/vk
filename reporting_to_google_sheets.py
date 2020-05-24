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
range_name = 'Sheet1!A3:H'

# Logging
FORMAT = '[%(asctime)s] %(levelname).1s %(message)s'
log_file = 'google_reporting.log'

bt = '-57536014'
mememe = '26546404'
jail = '-92767252'

active_scan = bt
count_of_executes = 5


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
        # logging.error(error_msg)
    return vk_session


def get_wall(vk_session):
    tools = vk_api.VkTools(vk_session)
    wall = tools.get_all('wall.get', count_of_executes, {'owner_id': active_scan}, limit=1)
    return wall, tools


def parse_wall(wall):
    data = []
    postids = []
    for post in wall["items"]:
        postids.append(post['id'])
        try:
            data.append(parse_post(post)) # only for post with created_by data
        except:
            logging.error('Post parsing failed with 2 ways')

    mydataframe = pd.DataFrame(data)  #
    mydataframe.fillna(0, inplace=True)

    ## here filtering by timedelta

    mydataframe = mydataframe[mydataframe[6] > twoweeksago]
    mydataframe = mydataframe.values.tolist()
    return mydataframe, postids


def parse_post(post) -> list:
    try:
        post_id = post['id']
        created_by = post['created_by']
        likes = post['likes']['count']
        reposts = post['reposts']['count']
        views = post['views']['count']
        text_of_post = post['text'][:20]
        postdate = post['date']
        unix_timestamp = float(postdate)
        count_of_comments = post['comments']['count']
        #local_timezone = tzlocal.get_localzone()  # get pytz timezone
        local_time = datetime.fromtimestamp(unix_timestamp) + delta
        parsed_post = [post_id, created_by, reposts, likes, views, text_of_post, local_time, count_of_comments]
    except Exception as e:
        # print('There\'s no created_by or some other parameter is this post')
        logging.info('There is some post with no info about redach')
        logging.error(e)
        try:
            post_id = post['id']
            likes = post['likes']['count']
            reposts = post['reposts']['count']
            views = post['views']['count']
            text_of_post = post['text'][:20]
            postdate = post['date'] # unix timestamp
            unix_timestamp = float(postdate)
            count_of_comments = post['comments']['count']
            #local_timezone = tzlocal.get_localzone()  # get pytz timezone
            local_time = datetime.fromtimestamp(unix_timestamp) + delta
            parsed_post = [post_id, 0, reposts, likes, views, text_of_post, local_time, count_of_comments]
        except:
            logging.error('Post parsing failed with 2 ways')
            # print('Both ways to parse post were failed')
    return parsed_post


def chunk(lst, n):
    for i in range (0, len(lst),n):
        yield lst[i:i+n]


def supply_post_with_more_data(vk_session, postids):
    chunks = chunk(postids, 30)
    vk = vk_session.get_api()
    parsed_post = []
    for postids_group in chunks:
        posts_enriched = vk.stats.getPostReach(owner_id=active_scan, post_ids=postids_group)
        for post in posts_enriched:
            try:
                post_id = post['post_id']
                hide = post['hide']
                join_group = post['join_group']
                links = post['links']
                reach_subscribers = post['reach_subscribers']
                to_group = post['to_group']
                reach_viral = post['reach_viral']
                report = post['report']
                unsubscribe = post['unsubscribe']
                listoffeatures = [post_id, hide, join_group, links, reach_subscribers, to_group, reach_viral, report, unsubscribe]
                parsed_post.append(listoffeatures)
            except:
                try:
                    # print("cannot add posts_enriched features for post: ", post['post_id'])
                    logging.error('cannot add posts_enriched features for post {post["post_id"]}')
                except:
                    logging.error('post_enriched features failed while taking post_id from list postids')
                    # print("cannot add post_enriched features and even take post_id from list postids")
    return parsed_post


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
                    {"range": "Sheet1!A3:P",
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
                    {"range": "Sheet1!E1:G1",
                     "majorDimension":"ROWS",
                     "values": [stringest]}
                ]
            }
        ).execute()

class Statistics_work():
    """Takes postids_from_sheets as list and parsed as list
    Merge new stats (parsed) to old one (posts_from_sheets)    """

    def __init__(self):
        pass

    @staticmethod
    def compare(posts_from_sheets, parsed, morefeatures):

        cols = ['postid', 'created_by', 'reposts', 'likes', 'views', 'text_of_post', 'datetimeofpost', 'count_of_comments']
        df_with_parsed = pd.DataFrame(parsed, columns=cols, dtype=int)
        df_with_from_sheet = pd.DataFrame(posts_from_sheets, columns=cols, dtype=int)

        morecolumns = ['postid', 'hide', 'join_group', 'links', 'reach_subscribers', 'to_group', 'reach_viral', 'report', 'unsubscribe']
        df_morefeatures = pd.DataFrame(morefeatures, columns=morecolumns, dtype=int)

        df_with_from_sheet = df_with_from_sheet.iloc[:, 0:2]
        cols_to_merge = [0,2,3,4,5,6,7]
        df_with_parsed_to_merge = df_with_parsed.iloc[:,cols_to_merge]

        df_with_from_sheet['postid'] = df_with_from_sheet['postid'].astype('int32') # maybe is not needed anymore
        df_with_from_sheet['created_by'] = df_with_from_sheet['created_by'].astype('int32')

        frames = [df_with_parsed, df_with_from_sheet]
        key = ['postid']

        result = pd.concat(frames, sort=False).groupby(key, as_index=False)['created_by'].max()

        result = pd.merge(result, df_with_parsed_to_merge, how='inner', on=key, left_on=None, right_on=None,
                 left_index=False, right_index=False, sort=False,
                 suffixes=('_x', '_y'), copy=True, indicator=False,
                 validate=None)


        result = pd.merge(result, df_morefeatures, how='inner', on=key, left_on=None, right_on=None,
                 left_index=False, right_index=False, sort=False,
                 suffixes=('_x', '_y'), copy=True, indicator=False,
                 validate=None)

        result = result.sort_values(by=['postid'], ascending=False)
        result.datetimeofpost = result.datetimeofpost.astype(str)
        result = result.values.tolist()
        return result


if __name__ == '__main__':
    logger = logging.getLogger(log_file)
    logging.basicConfig(level=logging.INFO, format=FORMAT, filename=log_file)


    vk_session = get_session()
    wall, tools = get_wall(vk_session)
    parsed, postids = parse_wall(wall)
    logger.info('VK parsed successfully')


    morefeatures = supply_post_with_more_data(vk_session, postids)
    logger.info('Additional VK data parsed successfully')


    r = Reporting()
    service = r.auth()
    posts_from_sheets = r.get_values()
    logger.info('Google Sheets parsed successfully')


    s = Statistics_work()
    result = s.compare(posts_from_sheets, parsed, morefeatures)


    r.put_values()
    r.put_last_updated()
    logger.info('Process finished at %s' % {datetime.now() + delta})