# API списка задач

REST API для управления задачами на Django REST framework. API использует
токенную аутентификацию: для работы с задачами нужен заголовок
`Authorization: Token <ключ>`.

## Установка и запуск

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Для получения токена отправьте `POST` на `/api/token/` с полями `username` и
`password`. Django admin доступен по адресу `/admin/`.

Для ручной проверки через браузер откройте `/api/tasks/` и войдите через ссылку
`Log in` (страница входа DRF доступна по `/api-auth/login/`).

## Эндпоинты

- `GET /api/tasks/` список задач; поддерживает `?completed=true` или `false`.
- `POST /api/tasks/` создание задачи.
- `GET /api/tasks/{id}/` получение задачи.
- `PUT/PATCH /api/tasks/{id}/` обновление задачи.
- `DELETE /api/tasks/{id}/` удаление задачи.

Список разбит на страницы по 10 задач. Номер страницы передаётся параметром
`?page=2`; размер страницы можно изменить параметром `?page_size=20` (максимум
100).

## Тесты

```bash
python manage.py test tasks
```