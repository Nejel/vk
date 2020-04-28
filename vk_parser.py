# -*- coding: utf-8 -*-
import vk_api
import json

def auth_handler():
    """ При двухфакторной аутентификации вызывается эта функция.
    """

    # Код двухфакторной аутентификации
    key = input("Enter authentication code: ")
    # Если: True - сохранить, False - не сохранять.
    remember_device = True

    return key, remember_device

def main():
    """ Пример получения всех постов со стены """

    login, password = 'тут_логин', 'тут_пароль'
    vk_session = vk_api.VkApi(
        login, password,
        # функция для обработки двухфакторной аутентификации
        auth_handler=auth_handler
    )

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    tools = vk_api.VkTools(vk_session)

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

    wall = tools.get_all('wall.get', 100, {'owner_id':-92767252})

    """
    Некоторые сообщества и люди: 
    -92767252   - Подслушано в Тюрьме
    -57536014   - БТ
    26546404    - я сам, хули
    """

    print('Posts count:', wall['count'])

    with open("data_file.json", "w", encoding='utf8') as write_file:
        json.dump(wall, write_file, ensure_ascii=False)

    # На всякий случай напечатаем в конце первый и последний пост, которые мы обработали
    if wall['count']:
        print('First post:', wall['items'][0], '\n')

    if wall['count'] > 1:
        print('Last post:', wall['items'][-1])


if __name__ == '__main__':
    main()