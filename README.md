![Workflow status badge](https://github.com/berg96/foodgram-project-react/actions/workflows/main.yml/badge.svg)
# Проект Foodgram 

## Описание проекта 

Проект Foodgram позволяет зарегистрированным пользователям выкладывать свои рецепты.
[Foodgram](https://foodgram-berg.ddns.net)

TODO

### Автор проекта Артём Куликов

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
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```
