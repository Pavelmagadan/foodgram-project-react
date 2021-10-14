# Учебный проект "API для сервиса "Продуктовый помощник"

Работающий сервис здесь: ["Продуктовый помощник"](http://62.84.114.83)

## Задача учебного проекта
Задачей учебного проекта являлась реализация API для сервиса "Продуктовый помощник" в соответствии со [спецификацией](http://62.84.114.83/api/docs/), настройка сайта администратора и развертывание сервиса на облачном сервере в контейнерах Docker.

Создание документации и frontend-части не входило в рамки выполнения задания и было получено в готовом виде.

## Используемые технологии
![](https://img.shields.io/badge/Python3-mediumblue) ![](https://img.shields.io/badge/Django-mediumvioletred) ![](https://img.shields.io/badge/DRF-black) ![](https://img.shields.io/badge/Nginx-purple) ![](https://img.shields.io/badge/Gunicorn-gold) ![](https://img.shields.io/badge/Docker-red) ![](https://img.shields.io/badge/YandexClaud-Lime)


## Описание проекта
Проект "Продуктовый помощник" служит для публикации и просмотра кулинарных рецептов.

Неавторизованному пользователю доступны
* главная страница со списком всех опубликованных рецептов с возможностью фильтрации по тегам;
* страницы с полным описанием каждого рецепта.

Авторизованный пользователь дополнительно получает возможности:
* публиковать рецепты;
* просматривать страницы других пользователей с их рецептами;
* подписываться на других пользователей;
* просматривать список подписок;
* добавлять рецепты в список избранного и просматривать этот список;
*  добавлять рецепты в список покупок и просматривать этот список, а также скачивать его.

Скаченный список покупок представляет собой перечень ингредиентов с указанием их количества.

## Как развернуть
Для развертывания проекта описанным ниже способом на базе Linux должны быть установлены и включены утилиты docker и docker-compose. Для развертывания на базе Windows10 должна быть установлена WSL2 и Docker-desktop.

1. Склонируйте репозиторий: ```https://github.com/palmage/foodgram-project-react```.
2. В директорию ```.../foodgram-project-react/infra``` добавьте фаил ```.env``` и заполните его следующими переменными окружения:
```PowerShell
DJANGO_SECRET_KEY='<your_DJANGO_SECRET_KEY>'
HOST_1='<your_dgango_ALLOWED_HOSTS>'
HOST_2='<your_second_dgango_ALLOWED_HOSTS>'
DB_ENGINE='django.db.backends.postgresql_psycopg2'
DB_NAME='postgres'
POSTGRES_USER='<your_db_username>'
POSTGRES_PASSWORD='<your_db_password>'
DB_HOST='db'
DB_PORT='5432'
```
3. Из дериктории ```.../foodgram-project-react/infra``` выполните команду ```sudo docker-compose up -d --build```.
4. Примените миграции: ```sudo docker-compose exec web python manage.py migrate --noinput```.
5. Выполните команду ```sudo docker-compose exec web python manage.py collectstatic --no-input```
6. Для наполнения БД начальными данными выполните команды:

``` python
sudo docker-compose exec web python3 manage.py shell 

# выполнить в открывшемся терминале:
>>> from django.contrib.contenttypes.models import ContentType
>>> ContentType.objects.all().delete()
>>> quit()

sudo docker-compose exec web python manage.py loaddata dump.json
```
7. Создайте суперпользователя: ```sudo docker-compose exec web python manage.py createsuperuser```. После развертывания проекта сайт администратора будет доступен по адресу: http://<your_host>/admin/. 

## API
После развертывания проекта станет доступна спецификация АPI по адресу http://<your_host>/api/docs/
