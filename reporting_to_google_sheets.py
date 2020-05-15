import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd
import vk_api
import logging
from secrets import login, password

'''
TODO:
1. Добавить таймдельту на последнюю неделю

'''

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1mz92-6l51z1wFyd0b1V2pnFK1mSkm3X3NfShG5vySG0'
SAMPLE_RANGE_NAME = 'Sheet1!A3:F'

FORMAT = '[%(asctime)s] %(levelname).1s %(message)s'

log_file = 'log.log'

## Некоторые сообщества и люди:
bt = '-57536014'  # БТ
mememe = '26546404'  # я сам
jail = '-92767252'  # Подслушано в Тюрьме

active_scan = bt
count_of_executes = 8


def auth_handler():
    """ При двухфакторной аутентификации вызывается эта функция.
    """

    # Код двухфакторной аутентификации
    key = input("Enter authentication code: ")
    # Если: True - сохранить, False - не сохранять.
    remember_device = True

    return key, remember_device


def get_wall():
    """ Пример получения всех комментариев к записям со стены и их ранжирования
    по сумме лайков на каждого пользователя"""

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
    # vk = vk_session.get_api()

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
        Для людей ставить впереди знаки "-" не нужно    """

    # второй параметр тут отвечает за количество запросов в вк через execute. 1 запрос = 25 постов.
    wall = tools.get_all('wall.get', count_of_executes, {'owner_id': active_scan}, limit=1)
    return wall


def parse_wall(wall):
    data = []
    for post in wall["items"]:
        try:
            data.append(parse_post(post)) # only for post with created_by data
        except:
            print('Both ways to parse post were failed')

    mydataframe = pd.DataFrame(data)  #
    mydataframe.fillna(0, inplace=True)
    mydataframe = mydataframe.values.tolist()
    return mydataframe


def parse_post(post) -> list:
    try:
        post_id = post['id']
        created_by = post['created_by']
        likes = post['likes']['count']
        reposts = post['reposts']['count']
        views = post['views']['count']
        text_of_post = post['text'][:20]
        parsed_post = [post_id, created_by, reposts, likes, views, text_of_post]
    except:
        print('There\'s no created_by or some other parameter is this post')
        try:
            post_id = post['id']
            likes = post['likes']['count']
            reposts = post['reposts']['count']
            views = post['views']['count']
            text_of_post = post['text'][:20]
            parsed_post = [post_id, 0, reposts, likes, views, text_of_post]
        except:
            print('Both ways to parse post were failed')
    return parsed_post


class Reporting():

    def __init__(self):
        pass

    def main(self):
        """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
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
        print("values from sheets", posts_from_sheets)

        if not posts_from_sheets:
            print('No data found.')
        else:
            # print('Name, Major:')
            for row in posts_from_sheets:
                print('All clear. Let\'s get the party started...', row)

        return creds, posts_from_sheets


    def put(self, result):
        service = build('sheets', 'v4', credentials=creds)
        values = service.spreadsheets().values().batchUpdate(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": "A3:F",
                     "majorDimension":"ROWS",
                     "values": result}
                ]
            }
        ).execute()


class Statistics_work():
    """Takes postids_from_sheets as list and parsed as list
    Merge new stats (parsed) to old one (posts_from_sheets)    """

    def __init__(self):
        pass

    def compare(self, posts_from_sheets, parsed):
        cols = ['postid', 'created_by', 'reposts', 'likes', 'views', 'text_of_post']
        df_with_parsed = pd.DataFrame(parsed, columns=cols, dtype=int)
        df_with_from_sheet = pd.DataFrame(posts_from_sheets, columns=cols, dtype=int)
        df_with_from_sheet = df_with_from_sheet.iloc[:, 0:2]
        cols_to_merge = [0,2,3,4,5]
        df_with_parsed_to_merge = df_with_parsed.iloc[:,cols_to_merge]
        df_with_from_sheet['postid'] = df_with_from_sheet['postid'].astype('int32')
        df_with_from_sheet['created_by'] = df_with_from_sheet['created_by'].astype('int32')
        frames = [df_with_parsed, df_with_from_sheet]
        key = ['postid']

        # Объединим новые данные о лайках со старыми авторами
        result = pd.concat(frames).groupby(key, as_index=False)['created_by'].max()
        # И вернем сюда данные о лайках, репостах, просмотрах
        result = pd.merge(result, df_with_parsed_to_merge, how='inner', on=key, left_on=None, right_on=None,
                 left_index=False, right_index=False, sort=False,
                 suffixes=('_x', '_y'), copy=True, indicator=False,
                 validate=None)

        result = result.sort_values(by=['postid'], ascending=False)
        # take_smaller = lambda s1, s2: s1 if s1.sum() < s2.sum() else s2
        # result = df_with_parsed.combine(df_with_from_sheet, take_smaller)

        print("result!!! \n", result.head(50))
        result = result.values.tolist()
        """
        frames = [df_with_parsed, df_with_from_sheet]
        result = pd.concat(frames)
        result = result.groupby(['postid', 'created_by']).max()
        # df_with_parsed = df_with_parsed.loc[df.Weight == "155", "Name"] = "John"
        """
        return result


if __name__ == '__main__':
    wall = get_wall()
    parsed = parse_wall(wall)
    r = Reporting()
    creds, posts_from_sheets = r.main() # коннектимся к гугл-таблицам и читаем предыдущую статистику
    s = Statistics_work()
    result = s.compare(posts_from_sheets, parsed)
    # result.to_csv('test.csv', sep=';')
    r.put(result)