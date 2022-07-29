
import json

with open("data.json") as file:
    news_dict = json.load(file)

search_id = "520908123"

if search_id in news_dict:
    print("Новость уже есть в словаре, пропускаем итерацию")
else:
    print("Свежая новость, добавляем в словарь")