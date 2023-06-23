import pytest

from ..models import News, Comment


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
    return news.pk,


@pytest.fixture
def comment(author, news):
    """Создаём объект комментария к новости."""
    news = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return news


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
