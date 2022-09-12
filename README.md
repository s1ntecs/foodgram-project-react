![foodgram-project-react Workflow Status](https://github.com/s1ntecs/foodgram-project-react/actions/workflows/main.yml/badge.svg?branch=master&event=push)
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)
# Продуктовый помощник - Foodgram
Проект запущен и доступен по [адресу]http://84.201.152.71
## Самая актуальная версия всемирно известного портала Foodgram.

«Продуктовый помощник»: приложение, на котором пользователи публикуют рецепты, подписываться на публикации других авторов и добавлять рецепты в избранное. Сервис «Список покупок» позволит пользователю создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Особенности
- Вы сможете найти любой рецепт, поделиться своими рецептами
- Подписывайтесь на любимых авторов.
- Добавляйте любимые рецепты в избранное.
- Вы можете добавить рецепт в список покупок, вы сможете скачать файл с суммированным перечнем и количеством необходимых ингредиентов для всех рецептов, сохранённых в «Списке покупок»
- Авторизация происходит по токену. 
- Токен можно получить введя код подтверждения из электронного письма.

## Технологии
Клонировать GitHub репозиторий на ваш локальный компьютер:

```
git clone https://github.com/s1ntecs/foodgram-project-react.git

```

```
Необходимо создать файл переменных окружения .env без переменных окружения наш сервис не будет работать.
Образец заполнения файла можете посмотреть в example.env в директории infra.

```
### Как запустить проект на вашем сервере Linux:
Войдите в ваш Сервер:

Остановите службу nginx:

```
 sudo systemctl stop nginx
```
Установите docker:

```
 sudo apt install docker.io
```

Установите docker-compose https://docs.docker.com/compose/install/

Скопируйте файлы infra/docker-compose.yaml и infra/nginx/default.conf с локального репозитория на ваш сервер в home/<ваш_username>/docker-compose.yaml и home/<ваш_username>/nginx/default.conf соответственно.
* Локально отредактируйте файл infra/default.conf и в строке server_name впишите свой IP
* Скопируйте файлы docker-compose.yml и default.conf из директории infra на сервер:
```
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp default.conf <username>@<host>:/home/<username>/nginx.conf
```
## Добавьте в Secrets GitHub Actions переменные окружения для работы базы данных.
    DB_ENGINE - указываем, что работаем с postgresql
    DB_HOST - имя базы данных
    DB_NAME - логин для подключения к базе данных
    DB_PORT - порт для подключения к БД
    DOCKER_PASSWORD - Пароль от Docker
    DOCKER_USERNAME - Логин от аккакнта Docker
    HOST - адрес вашего сервера
    PASSPHRASE - контрольная фраза для входа в сервер
    POSTGRES_PASSWORD - пароль Posgress
    POSTGRES_USER - логин Posgress
    SSH_KEY - ssh ключь для входа в сервер можете получить введя в консоль: cat ~/.ssh/id_rsa
    TELEGRAM_TO - Телеграм id аккаунта в телеграмм
    TELEGRAM_TOKEN - Телеграм токен
    USER - логин для входа на ваш сервер

### При первом запуске проекта на сервере.
```
sudo docker-compose up -d --build
```
Нужно выполнить миграции, создать суперпользователя и собрать статику:

```
sudo docker-compose exec web python manage.py migrate

```
Создадим суперпользователя:

```
sudo docker-compose exec web python manage.py createsuperuser

```

Соберем Статику:

```
sudo docker-compose exec web python manage.py collectstatic --no-input

```
- Загрузите ингридиенты  в базу данных (необязательно):
sudo docker-compose exec web python manage.py load_data
*Если файл не указывать, по умолчанию выберется ingredients.json*
```
 - Проект будет доступен по вашему IP

## Лицензия

**MIT**

**Free Software, Hell Yeah!**
