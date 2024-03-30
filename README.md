![Workflow status badge](https://github.com/berg96/foodgram-project-react/actions/workflows/main.yml/badge.svg)
# Проект Foodgram 

## Описание проекта 

Проект Foodgram позволяет зарегистрированным пользователям публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
Пользователям также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
На главной странице список первых шести рецептов, отсортированных по дате публикации «от новых к старым», а при нажатии на один из них появится полное описание.
На некоторых страницах осуществлена фильтрация по тегам. При нажатии на название тега выводится список рецептов, отмеченных этим тегом. Фильтрация может проводиться по нескольким тегам в комбинации «или»: если выбрано несколько тегов — в результате показываются рецепты, которые отмечены хотя бы одним из этих тегов.

[Foodgram](https://foodgram-berg.ddns.net) [(https://foodgram-berg.ddns.net)](https://foodgram-berg.ddns.net)

### Автор backend Артём Куликов

tg: [@Berg1005](https://t.me/berg1005)

[GitHub](https://github.com/berg96)

## Используемые технологии 

Проек реализован на языке python c использованием следующих библиотек:

* Django (v 3.2.16) 
* djangorestframework(v 3.12.4) 
* djoser (v 2.1.0) 
* gunicorn (v 20.1.0)
* webcolors (v 1.11.1)
* Pillow (v 9.0.0)
* django-filter (v 23.5)


## Как запустить проект

Клонировать репозиторий:
```
git clone git@github.com:berg96/foodgram-project-react.git
```
Запустить Docker compose:
```
docker compose -f docker-compose.yml up -d
```
Собрать миграции и собрать статику:
```
docker compose -f docker-compose.yml exec backend python manage.py migrate
docker compose -f docker-compose.yml exec backend python manage.py collectstatic
```
Наполнить БД ингредиентами и тегами:
```
docker compose -f docker-compose.yml exec backend python manage.py import_ingredients_json
sudo docker compose -f docker-compose.yml exec backend python manage.py import_tags_json
```
