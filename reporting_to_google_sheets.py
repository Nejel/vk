# -*- coding: utf-8 -*-

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd
import vk_api
import logging
from secrets import login, password

import tzlocal
import time
from datetime import datetime, date, timedelta
# from datetime import timedelta
week = timedelta(weeks=1)
sevenhours = timedelta(hours=7)
t = 3600 #sec

'''
#TODO 
1. Fix OAuth2
2. Quantity of comments

'''

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1xZXg3o88qFKR1M9qOUtTTzE7AsZ_i_fyZNut8EOfyEc'
SAMPLE_RANGE_NAME = 'Sheet1!A3:G'

FORMAT = '[%(asctime)s] %(levelname).1s %(message)s'

log_file = 'log.log'

bt = '-57536014'
mememe = '26546404'
jail = '-92767252'

active_scan = bt
count_of_executes = 5


def auth_handler():
    """
    """

    key = input("Enter authentication code: ")
    remember_device = True

    return key, remember_device



def get_session():
    vk_session = vk_api.VkApi(
        login, password,

        auth_handler=auth_handler
    )

    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
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
            print('Both ways to parse post were failed')

    mydataframe = pd.DataFrame(data)  #
    mydataframe.fillna(0, inplace=True)

    ## here filtering by timedelta
    today = datetime.today()
    weekago = today - week
    mydataframe = mydataframe[mydataframe[6] > weekago]
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
        #local_timezone = tzlocal.get_localzone()  # get pytz timezone
        local_time = datetime.fromtimestamp(unix_timestamp) + sevenhours #local_timezone
        parsed_post = [post_id, created_by, reposts, likes, views, text_of_post, local_time]
    except:
        # print('There\'s no created_by or some other parameter is this post')
        try:
            post_id = post['id']
            likes = post['likes']['count']
            reposts = post['reposts']['count']
            views = post['views']['count']
            text_of_post = post['text'][:20]
            postdate = post['date'] #unix timestamp
            unix_timestamp = float(postdate)
            #local_timezone = tzlocal.get_localzone()  # get pytz timezone
            local_time = datetime.fromtimestamp(unix_timestamp) + sevenhours
            parsed_post = [post_id, 0, reposts, likes, views, text_of_post, local_time]
        except:
            print('Both ways to parse post were failed')
    return parsed_post

def chunk(lst, n):
    for i in range (0, len(lst),n):
        yield lst[i:i+n]


def supply_post_with_more_data(vk_session, postids):
    chunks = chunk(postids, 30)


    # postids = postids[:30]
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
                    print("cannot add posts_enriched features for post: ", post['post_id'])
                except:
                    print("cannot add post_enriched features and even take post_id from list postids")
    return parsed_post


class Reporting:

    def __init__(self):
        pass

    def _main(self):
        """
        .
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()

        posts_from_sheets = result.get('values', [])

        if not posts_from_sheets:
            print('No data found.')
        else:
            pass
        return creds, posts_from_sheets


    def put(self, result):
        service = build('sheets', 'v4', credentials=creds)
        values = service.spreadsheets().values().batchUpdate(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": "Sheet1!A3:O",
                     "majorDimension":"ROWS",
                     "values": result}
                ]
            }
        ).execute()

    def put_last_updated(self):
        server_fixed_time = datetime.now() + sevenhours
        d = str(datetime.date(server_fixed_time))
        t = str(datetime.time(server_fixed_time))
        stringest = ['Last Updated:', d, t]
        service = build('sheets', 'v4', credentials=creds)
        values = service.spreadsheets().values().batchUpdate(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
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

    def compare(self, posts_from_sheets, parsed, morefeatures):

        cols = ['postid', 'created_by', 'reposts', 'likes', 'views', 'text_of_post', 'datetimeofpost']
        df_with_parsed = pd.DataFrame(parsed, columns=cols, dtype=int)
        df_with_from_sheet = pd.DataFrame(posts_from_sheets, columns=cols, dtype=int)

        morecolumns = ['postid', 'hide', 'join_group', 'links', 'reach_subscribers', 'to_group', 'reach_viral', 'report', 'unsubscribe']
        df_morefeatures = pd.DataFrame(morefeatures, columns=morecolumns, dtype=int)

        df_with_from_sheet = df_with_from_sheet.iloc[:, 0:2]
        cols_to_merge = [0,2,3,4,5,6]
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

        ## Check timedelta for 7 days


        result = result.sort_values(by=['postid'], ascending=False)
        result.datetimeofpost = result.datetimeofpost.astype(str)
        result = result.values.tolist()
        return result


if __name__ == '__main__':
    # for i in range (1, 3):
    vk_session = get_session()
    wall, tools = get_wall(vk_session)
    parsed, postids = parse_wall(wall)
    print("parsed VK is ok")

    morefeatures = supply_post_with_more_data(vk_session, postids)
    print("parsed additional data from VK is ok")

    r = Reporting()
    creds, posts_from_sheets = r._main()

    print("parsed GS is ok")
    s = Statistics_work()
    result = s.compare(posts_from_sheets, parsed, morefeatures)
    r.put(result)
    r.put_last_updated()

    print("All right, process is over at", datetime.now()+sevenhours)
        # time.sleep(t)