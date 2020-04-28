# -*- coding: utf-8 -*-
import pandas as pd
import vk_api
# import xlsxwriter
# import time
# import json

## Глобальные переменные
# max_counts = 1 #пока что не работает, потом пофикшу, сейчас задается на входе в функцию ниже
login = 'логин_тут'
password = 'тут_пароль'

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


def main():
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

    for i in wall["items"]:
        if i["id"]:
            try:
                print("POST_ID: ", i['id'])  # , "TEXT: ", i['text']
                comments = vk.wall.getComments(owner_id=active_scan, post_id=i['id'], need_likes=1)
                print("Count of comments: ", comments['count'])
                try:
                    for ii in comments['items']:
                        # print(ii['likes']['count'], ii['text'], ii['from_id'])
                        usersandlikes = usersandlikes.append({'User': ii['from_id'],
                                                              'Posts': i['id'],
                                                              'Likes': ii['likes']['count'],
                                                              'Text': ii['text']},
                                                             ignore_index=True)
                except:
                    print("Не удалось получить комментарий, возможно он удален или что-то пошло не так. ПостID: ",
                          i['id'])
                # time.sleep(6)
            except:
                print("Не удалось получить пост")
        else:
            pass
    # print("Type of usersandlikes ", type(usersandlikes))
    print("Количество проанализированный комментариев", len(usersandlikes))
    result = groupbyusers(usersandlikes).reset_index()
    # print("Type of result ", type(result))

    # result['LinkToUser'] = "https://vk.com/id"+result['User'].astype(str)

    # result.rename(columns=result.iloc[:;0])
    # result.reindex(axis=0)
    result.iloc[:, 1] = "https://vk.com/id" + result.iloc[:, 1].astype(str)
    print(result.head(20))

    return result


def groupbyusers(usersandlikes):
    ###
    topcomment = usersandlikes.filter(items=['User', 'Likes', 'Text'])
    topcomment = topcomment.sort_values('Likes', ascending=False).drop_duplicates(['User'])
    topcomment = topcomment.filter(items=['User', 'Text', 'Likes'])
    topcomment = topcomment.rename(columns={"Likes": "Most_likeable_comment", "Text": "Comment_text"})
    print("top comments", len(topcomment))
    ### Дописать тут функционал вывода самого залайканного комментария
    ###

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
    toplikers = main()
    # print(usersandlikes)
    # usersandlikes.to_csv('usersandlikes.csv', sep=';')
    # print(toplikers)
    toplikers.to_excel('toplikers.xlsx', sheet_name='Sheet_name_1', engine='xlsxwriter')
    # toplikers.to_csv('toplikers.csv', sep=';')