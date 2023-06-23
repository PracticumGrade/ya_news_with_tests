"""
- Анонимный пользователь не может отправить комментарий.
- Авторизованный пользователь может отправить комментарий.
- Если комментарий содержит запрещённые слова, он не будет опубликован, а форма вернёт ошибку.
- Авторизованный пользователь может редактировать или удалять свои комментарии.
- Авторизованный пользователь не может редактировать или удалять чужие комментарии.
"""
from http import HTTPStatus

import pytest
from django.shortcuts import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

pytestmark = [
    pytest.mark.django_db
]


class TestCommentEditDelete:
    # Обновленный текст комментария понадобится в нескольких местах кода,
    # поэтому запишем его в атрибуты класса.
    NEW_COMMENT_TEXT = 'Обновленный текст комментария'

    @pytest.fixture
    def url(self, news_pk_for_args):
        """Адрес новости."""
        return reverse('news:detail', args=news_pk_for_args)

    @pytest.fixture
    def url_to_comments(self, url):
        """# Адрес блока с комментариями."""
        return url + '#comments'

    @pytest.fixture
    def edit_url(self, news_pk_for_args):
        """URL для редактирования."""
        return reverse('news:edit', args=news_pk_for_args)

    @pytest.fixture
    def delete_url(self, news_pk_for_args):
        """URL для удаления."""
        return reverse('news:delete', args=news_pk_for_args)

    @pytest.fixture
    def form_data(self):
        """Формируем данные для POST-запроса по обновлению комментария."""
        return {
            'text': self.NEW_COMMENT_TEXT
        }

    def test_author_can_edit_comment(self, author_client, edit_url, form_data, url_to_comments, comment):
        """
        - Авторизованный пользователь может редактировать свои комментарии.
        """
        # Выполняем запрос на редактирование от имени автора комментария.
        response = author_client.post(edit_url, data=form_data)
        # Проверяем, что сработал редирект.
        assertRedirects(response, url_to_comments)
        # Обновляем объект комментария.
        comment.refresh_from_db()
        # Проверяем, что текст комментария соответствует обновлённому.
        assert comment.text == self.NEW_COMMENT_TEXT

    def test_user_cant_edit_comment_of_another_user(self, reader_client, edit_url, form_data, comment, comment_text):
        """
        - Авторизованный пользователь не может редактировать чужие комментарии.
        """
        # Выполняем запрос на редактирование от имени другого пользователя.
        response = reader_client.post(edit_url, data=form_data)
        # Проверяем, что вернулась 404 ошибка.
        assert response.status_code == HTTPStatus.NOT_FOUND
        # Обновляем объект комментария.
        comment.refresh_from_db()
        # Проверяем, что текст остался тем же, что и был.
        assert comment.text == comment_text

    def test_author_can_delete_comment(self, author_client, delete_url, url_to_comments, comment):
        """
        - Авторизованный пользователь может удалять свои комментарии.
        """
        # От имени автора комментария отправляем DELETE-запрос на удаление.
        response = author_client.delete(delete_url)
        # Проверяем, что редирект привёл к разделу с комментариями.
        # Заодно проверим статус-коды ответов.
        assertRedirects(response, url_to_comments)
        # Считаем количество комментариев в системе.
        comments_count = Comment.objects.count()
        # Ожидаем ноль комментариев в системе.
        assert comments_count == 0

    def test_user_cant_delete_comment_of_another_user(self, reader_client, delete_url, comment):
        """
        - Авторизованный пользователь не может удалять чужие комментарии.
        """
        # Выполняем запрос на удаление от пользователя-читателя.
        response = reader_client.delete(delete_url)
        # Проверяем, что вернулась 404 ошибка.
        assert response.status_code == HTTPStatus.NOT_FOUND
        # Убедимся, что комментарий по-прежнему на месте.
        comments_count = Comment.objects.count()
        assert comments_count == 1


class TestCommentCreation:
    # Текст комментария понадобится в нескольких местах кода,
    # поэтому запишем его в атрибуты класса.
    COMMENT_TEXT = 'Текст комментария'

    @pytest.fixture
    def url(self, news_pk_for_args):
        """Адрес новости."""
        return reverse('news:detail', args=news_pk_for_args)

    @pytest.fixture
    def form_data(self):
        """Формируем данные для POST-запроса по созданию комментария."""
        return {'text': self.COMMENT_TEXT}

    def test_user_cant_use_bad_words(self, auth_client, url):
        # Формируем данные для отправки формы; текст включает
        # первое слово из списка стоп-слов.
        bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
        # Отправляем запрос через авторизованный клиент.
        response = auth_client.post(url, data=bad_words_data)
        # Проверяем, есть ли в ответе ошибка формы.
        assertFormError(
            response,
            form='form',
            field='text',
            errors=WARNING
        )
        # Дополнительно убедимся, что комментарий не был создан.
        comments_count = Comment.objects.count()
        assert comments_count == 0

    def test_user_can_create_comment(self, auth_client, url, form_data, news, auth_user):
        # Совершаем запрос через авторизованный клиент.
        response = auth_client.post(url, data=form_data)
        # Проверяем, что редирект привёл к разделу с комментами.
        assertRedirects(response, f'{url}#comments')
        # Считаем количество комментариев.
        comments_count = Comment.objects.count()
        # Убеждаемся, что есть один комментарий.
        assert comments_count == 1
        # Получаем объект комментария из базы.
        comment = Comment.objects.get()
        # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
        assert comment.text == self.COMMENT_TEXT
        assert comment.news == news
        assert comment.author == auth_user

    def test_anonymous_user_cant_create_comment(self, client, url, form_data):
        # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
        # предварительно подготовленные данные формы с текстом комментария.
        client.post(url, data=form_data)
        # Считаем количество комментариев.
        comments_count = Comment.objects.count()
        # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
        assert comments_count == 0
