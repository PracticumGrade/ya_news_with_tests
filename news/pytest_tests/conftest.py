from datetime import date, timedelta

import pytest
from django.conf import settings

from ..models import News, Comment

COMMENTS_FOR_NEWS = 15


@pytest.fixture
def news():
    """Создаём объект новости."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def news_pk_for_args(news):
    """Фикстура для получения позиционных аргументов для разрешения url по имени"""
    return news.pk,


@pytest.fixture
def comment_text():
    """Текст комментария нужен будет в нескольких местах, поэтому вынесен в отдельную фикстуру."""
    return 'Текст комментария'


@pytest.fixture
def comment(author, news, comment_text):
    """Создаём объект комментария к новости."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text=comment_text,
    )
    return comment


@pytest.fixture
def comment_pk_for_args(comment):
    """Фикстура для получения позиционных аргументов для разрешения url по имени"""
    return comment.pk,


@pytest.fixture
def all_news(author):
    """Список всех новостей. Список новостей делаем заведомо больше, чем может поместиться на странице."""
    day = timedelta(days=1)
    start_date = date(2000, 1, 1)

    news_list = [
        News(
            title=f'Заголовок_{i}',
            text='Текст заметки',
            date=start_date+day*i,  # каждый день публикуем новую запись
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(news_list)

    return news_list


@pytest.fixture
def all_comments_for_news(author, news):
    """Создаём объект комментария к новости."""
    comments_list = [
        Comment(news=news, author=author, text=f'Текст комментария {i}',)
        for i in range(COMMENTS_FOR_NEWS)
    ]
    Comment.objects.bulk_create(comments_list)

    return comments_list


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):  # Вызываем фикстуру автора и клиента.
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def reader_client(reader, client):  # Вызываем фикстуру читателя и клиента.
    client.force_login(reader)  # Логиним читателя в клиенте.
    return client


@pytest.fixture
def auth_user(django_user_model):
    auth_user = django_user_model.objects.create(username='auth_user')
    return auth_user


@pytest.fixture
def auth_client(auth_user, client):
    client.force_login(auth_user)  # Логиним пользователя в клиенте.
    return client
