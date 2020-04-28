# -*- coding: utf-8 -*-
import json

results = open("Podslushano_v_T.txt", "a", encoding='utf8')

with open("data_file.json", "r", encoding='utf8') as read_file:
    data = json.load(read_file)

for i in data["items"]:
    if i["text"]:
        try:
            results.write(i["text"])
            results.write('\n'*5)
        except:
            pass
    else:
        pass

results.close()