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
1. Проверять массив на наличие сломанных постов (возвращает 0 вместо редактора) +

2. Выгружать уже залитую стату из гугл.шитов, смотреть какие посты там есть (записывать в df), 
после этого в этот массив добавлять и обновлять новую статистику

3. Получать также 20 первых букв текста поста и отправлять в гугл дерьмо

'''

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1mz92-6l51z1wFyd0b1V2pnFK1mSkm3X3NfShG5vySG0'
SAMPLE_RANGE_NAME = 'Sheet1!A3:A'

FORMAT = '[%(asctime)s] %(levelname).1s %(message)s'

log_file = 'log.log'

## Некоторые сообщества и люди:
bt = '-57536014'  # БТ
mememe = '26546404'  # я сам
jail = '-92767252'  # Подслушано в Тюрьме

active_scan = bt
count_of_executes = 2


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

    # usersandlikes = pd.DataFrame(columns=['User', 'Posts', 'Likes'])
    # toplikers = pd.DataFrame(columns=['User', 'Likes'], index=None)

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
        Для людей ставить впереди знаки "-" не нужно
    """

    wall = tools.get_all('wall.get', count_of_executes, {'owner_id': active_scan}, limit=1)

    """
    второй параметр тут отвечает за количество запросов в вк через execute. 1 запрос = 25 постов.
    """

    return wall


def parse_wall(wall):
    data = []
    for post in wall["items"]:
        try:
            data.append(parse_post(post))
        except:
            pass
    mydataframe = pd.DataFrame(data)  #
    mydataframe.fillna("0", inplace=True)
    return mydataframe


def parse_post(post) -> list:
    try:
        post_id = post['id']
        created_by = post['created_by']
        likes = post['likes']['count']
        reposts = post['reposts']['count']
        views = post['views']['count']
        parsed_post = [post_id, created_by, reposts, likes, views]
    except:
        print('There\'s no created_by or some other parameter is this post')
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

        values = result.get('values', [])
        print("values", values)

        if not values:
            print('No data found.')
        else:
            # print('Name, Major:')
            for row in values:
                print('All clear. Let\'s get the party started...', row)
                # Print columns A and B, which correspond to indices 0 and 1.
                # print('%s, %s' % (row[0], row[1]))

        return creds, values

    def put(self, values, start_cell_idx, creds):
        value_range_body = {
            'majorDimension': 'ROWS',
            'values': values}

        RANGE = 'R%sC%s:R%sC%s' % (tuple(start_cell_idx) + \
                                   tuple(pd.Series(start_cell_idx) + \
                                         pd.Series((len(values),
                                                    max(map(len, values))))))

        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range=RANGE,
                                        valueInputOption='RAW',
                                        body=value_range_body)
        response = request.execute()


if __name__ == '__main__':
    wall = get_wall()
    parsed = parse_wall(wall)
    df = parsed.values.tolist()
    r = Reporting()
    creds, postids_from_sheets = r.main()  # коннектимся к гугл-таблицам и читаем предыдущую статистику
    # функция мерджа старой и новой статистики
    r.put(df, [3, 1], creds)  # добавляем данные в лист Sheet1
