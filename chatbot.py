"""
Базовый бот для отправки сообщения в редакционный чят.
Версия 0.000001 найтли.

После запуска забирает ячейку из дашборда в гугл-листах и отправляет её в чат редакции.
Предполагается на постановку на ежесуточный автозапуск.

TODO:
    1. Система генерации рандомных "званий" из набора заранее написанных прилагательных+существительных+наречий
    2. Более умный механизм посуточного расчета лучшего редактора

"""


from oauth2client.service_account import ServiceAccountCredentials
import apiclient.discovery
import httplib2
from telegram.bot import Bot
from secrets import login, password, sheet_id, tg_token, chat_id


def auth():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDSTOSERVICE,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
    httpauth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=httpauth)
    return service


def get_values(service):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range=range_name).execute()

    posts_from_sheets = result.get('values', [])

    if not posts_from_sheets:
        pass
        # print('No data found.')
        # logging.info('Failed to find posts in sheet')
    else:
        pass
    return posts_from_sheets


# CREDENTIALS TO SERVICE ACC
CREDSTOSERVICE = 'credentials.json'


# The ID and range of a sample spreadsheet.
spreadsheet_id = sheet_id
range_name = 'Dashboard!I42:I42'


if __name__ == '__main__':
    service = auth()
    best_editor = get_values(service)
    Bot(token=tg_token).send_message(chat_id=chat_id, text=f'{best_editor}, ты просто космос')

