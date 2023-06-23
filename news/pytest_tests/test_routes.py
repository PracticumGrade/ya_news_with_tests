"""
- Главная страница доступна анонимному пользователю.
- Страница отдельной новости доступна анонимному пользователю.
- Страницы удаления и редактирования комментария доступны автору комментария.
- При попытке перейти на страницу редактирования или удаления комментария анонимный пользователь
    перенаправляется на страницу авторизации.
- Авторизованный пользователь не может зайти на страницы редактирования или удаления
    чужих комментариев (возвращается ошибка 404).
- Страницы регистрации пользователей, входа в учётную запись и выхода из неё доступны анонимным пользователям.
"""

from http import HTTPStatus

from django.shortcuts import reverse
import pytest
from pytest_django.asserts import assertRedirects

pytestmark = [
    pytest.mark.django_db
]


@pytest.mark.parametrize(
    'name,args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_pk_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
def test_pages_availability_for_anonymous_user(client, name, args):
    """
    - Главная страница доступна анонимному пользователю.
    - Страница отдельной новости доступна анонимному пользователю.
    - Страницы регистрации пользователей, входа в учётную запись и выхода из неё доступны анонимным пользователям.
    """
    url = reverse(name, args=args)
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client,expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'name',
    (
        'news:edit',
        'news:delete'
    ),
)
def test_pages_availability_for_author(parametrized_client, expected_status, name, comment):
    """
    - Страницы удаления и редактирования комментария доступны автору комментария.
    - Авторизованный пользователь не может зайти на страницы редактирования или удаления
        чужих комментариев (возвращается ошибка 404).
    """
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    (
        'news:edit',
        'news:delete'
    ),
)
def test_redirects_for_anonymous_user(client, name, news):
    """
    - При попытке перейти на страницу редактирования или удаления комментария анонимный пользователь
        перенаправляется на страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(news.pk,))

    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    # Ожидаем, что со всех проверяемых страниц анонимный клиент
    # будет перенаправлен на страницу логина:
    assertRedirects(response, expected_url)
