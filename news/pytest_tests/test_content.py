"""
- Количество новостей на главной странице — не более 10.
- Новости отсортированы от самой свежей к самой старой. Свежие новости в начале списка.
- Комментарии на странице отдельной новости отсортированы в хронологическом порядке: старые в начале списка, новые — в конце.
- Анонимному пользователю недоступна форма для отправки комментария на странице отдельной новости, а авторизованному доступна.
"""
from operator import attrgetter

import pytest
from django.shortcuts import reverse
from django.conf import settings
from pytest_django.asserts import assertQuerysetEqual

pytestmark = [
    pytest.mark.django_db
]


class TestNewsDetailPage:
    NEWS_DETAIL_NAME = 'news:detail'

    @pytest.mark.parametrize(
        'user_client, form_in_context',
        (
                (pytest.lazy_fixture('client'), False),
                (pytest.lazy_fixture('author_client'), True),
        )
    )
    def test_pages_contains_form(self, user_client, form_in_context, news_pk_for_args):
        """
        - Анонимному пользователю недоступна форма для отправки комментария на странице отдельной новости,
            а авторизованному доступна.
        """
        # Формируем URL.
        url = reverse(self.NEWS_DETAIL_NAME, args=news_pk_for_args)
        # Запрашиваем нужную страницу:
        response = user_client.get(url)
        # Проверяем, есть ли объект формы в словаре контекста:
        assert ('form' in response.context) is form_in_context

    def test_comments_order(self, author_client, news_pk_for_args, all_comments_for_news):
        """
        - Комментарии на странице отдельной новости отсортированы в хронологическом порядке:
        старые в начале списка, новые — в конце.
        """
        url = reverse(self.NEWS_DETAIL_NAME, args=news_pk_for_args)
        response = author_client.get(url)
        # Проверяем, что объект новости находится в словаре контекста
        # под ожидаемым именем - названием модели.
        assert 'news' in response.context
        # Получаем объект новости.
        news = response.context['news']
        # Получаем все комментарии к новости.
        all_comments = news.comment_set.all()

        ordered_comments = sorted(  # сортируем все комментарии по дате создания в хронологическом порядке
            all_comments_for_news,
            key=attrgetter('created'),
        )

        assertQuerysetEqual(all_comments, ordered_comments)


class TestNewsOnHomePage:
    HOME_NAME = 'news:home'

    def test_news_count(self, client, all_news):
        """
        - Количество новостей на главной странице — не более 10.
        """
        url = reverse(self.HOME_NAME)
        response = client.get(url)  # Код ответа не проверяем, его уже проверили в тестах маршрутов.

        # Получаем список объектов из словаря контекста.
        object_list = response.context['object_list']
        # Определяем длину списка.
        news_count = len(object_list)
        # Проверяем, что на странице именно 10 новостей.
        assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE

    def test_news_order(self, client, all_news):
        """
        - Новости отсортированы от самой свежей к самой старой. Свежие новости в начале списка.
        """
        url = reverse(self.HOME_NAME)
        response = client.get(url)
        object_list = response.context['object_list']

        ordered_news = sorted(  # сортируем все записи по дате публикации от самой свежей к самой старой
            all_news,
            key=attrgetter('date'),
            reverse=True
        )[:settings.NEWS_COUNT_ON_HOME_PAGE]

        assertQuerysetEqual(object_list, ordered_news)
