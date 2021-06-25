"""

Library DOCS will be here

"""

# !pip3 install --upgrade pandas
# !pip3 install --upgrade numpy
# !pip3 install --upgrade httplib2
# !pip3 install --upgrade instabot
# !pip3 install --upgrade google-api-python-client
# !pip3 install --upgrade vk-api
# !pip3 install --upgrade facebook-sdk

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
import vk_api


class Vkontakte:

    def __init__(self):
        pass

    def auth_handler(self):
        key = input("Enter authentication code: ")
        remember_device = True
        return key, remember_device

    def get_session(self, login, password):
        vk_session = vk_api.VkApi(
            login, password,
            auth_handler=self.auth_handler)

        try:
            vk_session.auth(token_only=True)
        except vk_api.AuthError as error_msg:
            pass
            # logging.error(error_msg)
        return vk_session

    def get_wall(self, vk_session, count_of_executes, active_scan):
        tools = vk_api.VkTools(vk_session)
        wall = tools.get_all('wall.get', count_of_executes,
                             {'owner_id': active_scan}, limit=1)
        return wall, tools

    @staticmethod
    def parse_wall(vk, wall, delta):

        today = datetime.today()
        week = timedelta(weeks=1)
        twoweeksago = today - week - week
        data = []
        postids = []

        for post in wall["items"]:
            postids.append(post['id'])
            # print(post['id'])
            try:
                data.append(vk.parse_post(post, delta))
            # print("post and data: ", post, data, delta)

                # only for post with created_by data
            except:
                pass
                # logging.error('Post parsing failed with 2 ways')

        mydataframe = pd.DataFrame(data)  #
        mydataframe.fillna(0, inplace=True)

        # print("mydataframe is: ", mydataframe)

        mydataframe = mydataframe[mydataframe[6] > twoweeksago]
        mydataframe = mydataframe.values.tolist()

        return mydataframe, postids

    @staticmethod
    def parse_post(post, delta) -> list:
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

            local_time = datetime.fromtimestamp(unix_timestamp) + delta

            parsed_post = [post_id, created_by, reposts,
                           likes, views, text_of_post,
                           local_time, count_of_comments]
        except Exception as e:
            # print('There\'s no created_by or some other parameter is this post')
            # logging.info('There is some post with no info about redach')
            # logging.error(e)
            try:
                post_id = post['id']
                likes = post['likes']['count']
                reposts = post['reposts']['count']
                views = post['views']['count']
                text_of_post = post['text'][:20]
                count_of_comments = post['comments']['count']

                postdate = post['date'] # unix timestamp
                unix_timestamp = float(postdate)
                local_time = datetime.fromtimestamp(unix_timestamp) + delta

                parsed_post = [post_id, 0, reposts, likes,
                               views, text_of_post,
                               local_time, count_of_comments]
            except:
                pass
                # logging.error('Post parsing failed with 2 ways')
                # print('Both ways to parse post were failed')
        return parsed_post

    def chunk(self, lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i+n]

    def supply_post_with_more_data(self, vk_session, postids, active_scan):
        chunks = self.chunk(postids, 30)
        vk = vk_session.get_api()
        parsed_post = []
        for postids_group in chunks:
            posts_enriched = vk.stats.getPostReach(owner_id=active_scan,
                                                   post_ids=postids_group)
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
                    listoffeatures = [post_id, hide, join_group, links,
                                      reach_subscribers, to_group, reach_viral,
                                      report, unsubscribe]
                    parsed_post.append(listoffeatures)
                except:
                    try:
                        pass
                        # print("cannot add posts_enriched features for post: ",
                        # post['post_id'])
                        # logging.error('cannot add posts_enriched features for post
                        # {post["post_id"]}')

                    except:
                        pass
                        # logging.error('post_enriched features failed while
                        # taking post_id from list postids')
                        # print("cannot add post_enriched features and even
                        # take post_id from list postids")
        return parsed_post


class FaceBook:

    def __init__(self):
        pass


class GoogleSheets:

    def __init__(self):
        pass

    def auth(self, CREDSTOSERVICE):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREDSTOSERVICE,
            ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive'])
        httpauth = credentials.authorize(httplib2.Http())
        service = apiclient.discovery.build('sheets', 'v4', http=httpauth)

        return service

    @staticmethod
    def get_values(service, range_name, spreadsheet_id):

        # FIXME: Refactoring
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                    range=range_name).execute()

        posts_from_sheets = result.get('values', [])

        if not posts_from_sheets:
            # pass
            print('No data found.')
            # logging.info('Failed to find posts in sheet')
        else:
            pass
        return posts_from_sheets

    @staticmethod
    def get_values_as_df(service, range_name, spreadsheet_id):

        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                    range=range_name).execute()

        posts_from_sheets = result.get('values', [])

        if not posts_from_sheets:
            # pass
            print('No data found.')
            # logging.info('Failed to find posts in sheet')
        else:
            pass

        posts_from_sheets = pd.DataFrame(posts_from_sheets,
                                         columns=['ID', 'Count_of_comments',
                                                  'Likes',
                                                  'Text', 'url', 'Date'])
        posts_from_sheets['Date'] = posts_from_sheets['Date'].astype('datetime64[ns]')

        return posts_from_sheets

    @staticmethod
    def put_values(service, range_to_put, spreadsheet_id, result):
        """
        range should be list and values name like "Sheet1!A3:P" or ""

        """
        values = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            # TODO: Range should be var
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": range_to_put,
                     "majorDimension":"ROWS",
                     "values": result}
                ]
            }
        ).execute()

    @staticmethod
    def put_last_updated(service, range_to_put_LU, spreadsheet_id, delta):
        """
        range should be 3 cells in a row left to right like "Sheet1!E1:G1"
        """
        server_fixed_time = datetime.now() + delta
        d = str(datetime.date(server_fixed_time))
        t = str(datetime.time(server_fixed_time))

        stringest = ['Last Updated:', d, t]

        values = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": range_to_put_LU,
                     "majorDimension":"ROWS",
                     "values": [stringest]}
                ]
            }
        ).execute()


class Insta:
    def __init__(self):
        pass

    def some_func(self):
        pass

    @staticmethod
    def inst_get_posts(user_media_list, bot):
        df = pd.DataFrame(columns=['ID', 'Text', 'Date',
                                   'Count_of_comments', 'Likes', 'url'])
        for i in range(0, len(user_media_list)):
            info = bot.get_media_info(user_media_list[i])

            try:
                text = info[0]['caption']['text'][:20]
            except:
                text = ''

            url = "https://www.instagram.com/p/" + str(info[0]['code'])

            df = df.append({'ID': info[0]['id'],
                            'url': url,
                            'Text': text,
                            'Date': info[0]['taken_at'],
                            'Count_of_comments': info[0]['comment_count'],
                            'Likes': info[0]['like_count']},
                           ignore_index=True)

        df['Date'] = pd.to_datetime(df['Date'], unit='s', origin='unix')

        """"
        Here should be date format:
        Or not
        """

        return df


class DF_works:

    """Takes postids_from_sheets as list and parsed as list
    Merge new stats (parsed) to old one (posts_from_sheets)    """

    def __init__(self):
        pass

    def unixtimestamp_to_datetime(x):
        return datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def vk_compare(posts_from_sheets, parsed, morefeatures):

        cols = ['postid', 'created_by', 'reposts', 'likes',
                'views', 'text_of_post', 'datetimeofpost',
                'count_of_comments']
        df_with_parsed = pd.DataFrame(parsed, columns=cols, dtype=int)
        df_with_from_sheet = pd.DataFrame(posts_from_sheets, columns=cols, dtype=int)

        morecolumns = ['postid', 'hide', 'join_group',
                       'links', 'reach_subscribers', 'to_group',
                       'reach_viral', 'report', 'unsubscribe']
        df_morefeatures = pd.DataFrame(morefeatures, columns=morecolumns, dtype=int)

        df_with_from_sheet = df_with_from_sheet.iloc[:, 0:2]
        cols_to_merge = [0,2,3,4,5,6,7]
        df_with_parsed_to_merge = df_with_parsed.iloc[:,cols_to_merge]

        df_with_from_sheet['postid'] = df_with_from_sheet['postid'].astype('int32')
        # maybe is not needed anymore


        df_with_from_sheet['created_by'] = df_with_from_sheet['created_by'].astype('int32')

        frames = [df_with_parsed, df_with_from_sheet]
        key = ['postid']

        result = pd.concat(frames, sort=False).groupby(key, as_index=False)['created_by'].max()

        result = pd.merge(result, df_with_parsed_to_merge,
                          how='inner', on=key, left_on=None, right_on=None,
                 left_index=False, right_index=False, sort=False,
                 suffixes=('_x', '_y'), copy=True, indicator=False,
                 validate=None)


        result = pd.merge(result, df_morefeatures,
                          how='inner', on=key, left_on=None, right_on=None,
                 left_index=False, right_index=False, sort=False,
                 suffixes=('_x', '_y'), copy=True, indicator=False,
                 validate=None)

        result = result.sort_values(by=['postid'], ascending=False)

        result['datetimeofpost'] = pd.to_datetime(result['datetimeofpost'])
        result['datetimeofpost'] = result.datetimeofpost.dt\
                                .strftime('%Y-%m-%d').astype(str)
        result = result.values.tolist()

        return result


    @staticmethod
    def inst_merge_dfs_max_likes(df1, df2):
        df1 = df1[['ID', 'Count_of_comments', 'Likes']]

        df1['Count_of_comments'] = df1['Count_of_comments'].astype('int32').fillna(0)
        df1['Likes'] = df1['Likes'].astype('int32').fillna(0)

        df2 = df2[['ID', 'Count_of_comments', 'Likes']]

        df2['Count_of_comments'] = df2['Count_of_comments'].astype('int32').fillna(0)
        df2['Likes'] = df2['Likes'].astype('int32').fillna(0)

        frames = [df2, df1]
        key = ['ID']

        result = pd.concat(frames, sort=False).groupby(key, as_index=False).max()

        return result

    @staticmethod
    def inst_merge_dfs_text_cols(df1, df2):
        df1 = df1[['ID', 'Text', 'Date', 'url']]
        df2 = df2[['ID', 'Text', 'Date', 'url']]
        result = df1.merge(df2, on=['ID'], how='outer')

        return result

    @staticmethod
    def inst_final_merge(df1, df2):
        result = df1.merge(df2, on=['ID'])

        result['Text'] = np.where((pd.notna(result['Text_x'])),
                                  result['Text_x'],
                                  result['Text_y'])

        result['url'] = np.where((pd.notna(result['url_x'])),
                                 result['url_x'],
                                 result['url_y'])

        result['Date'] = np.where((pd.notna(result['Date_x'])),
                                  result['Date_x'],
                                  result['Date_y'])

        result = result.sort_values(by=['Date'], ascending=False)

        result = result.drop(columns=['Date_x', 'Date_y',
                                      'url_x', 'url_y', 'Text_y', 'Text_x'])

        return result