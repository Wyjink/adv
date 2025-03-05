1.Создать миграции python manage migrate
2.Запустить сервер. python manage runserver
3.Загрузка обьявлений Пример: POST [
  {"location": "New York", "ad_text": "Посетите Нью-Йорк!"},
  {"location": "New York", "ad_text": "Бродвейские шоу"},
  {"location": "London", "ad_text": "Увидеть Лондонский Тауэр"}
]
4. Проверка: GET http://127.0.0.1:8000/ads/ads/New%20York/
