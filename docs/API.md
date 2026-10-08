# REST API SUSU HelpDesk

Реализован первый этап: вход, приём обращений в PostgreSQL, просмотр и редактирование собственных заявок. Во всех ролях эти маршруты сейчас показывают только заявки текущего пользователя. Операторские маршруты, назначение исполнителей, NLP, вложения и уведомления в этот этап не входят.

## Запуск

Python 3.12+; PostgreSQL 15+. Из корня проекта:

```powershell
git checkout new_lisin
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

В `.env` задайте собственные `POSTGRES_PASSWORD`, соответствующий `DATABASE_URL` и случайный `SECRET_KEY` из последней команды. Не используйте значение-заглушку. Затем:

```powershell
docker volume create student_requests_data
docker compose up -d
alembic upgrade head
```

Для **демонстрационной БД** задайте `DEMO_PASSWORD` длиной от 12 символов и выполните:

```powershell
$env:DEMO_PASSWORD = "Your-demo-password-123"
python seed/seed.py
uvicorn app.main:app --reload
```

Повторный seed не меняет настоящие пароли. Он обновляет только точные старые заглушки `demo_hash_*` у известных демонстрационных пользователей. Пароль из `DEMO_PASSWORD` получают новые демонстрационные пользователи и такие старые аккаунты. Общий demo-пароль предназначен для тестовой базы.

Интерфейс проверки: http://127.0.0.1:8000/docs. Миграции применяются отдельно, приложение не создаёт таблицы при запуске.

## Контракт

| Метод | Путь | Назначение |
|---|---|---|
| POST | `/api/v1/auth/login` | JSON email/password, JWT на 30 минут |
| GET | `/api/v1/categories` | Список категорий |
| POST | `/api/v1/requests` | Создание обращения, 201 и Location |
| GET | `/api/v1/requests?limit=20&offset=0` | Свои обращения: items, total, limit, offset |
| GET | `/api/v1/requests/{id}` | Своя заявка |
| PATCH | `/api/v1/requests/{id}` | Заголовок и/или описание своей новой заявки |

Все маршруты, кроме входа и документации, требуют `Authorization: Bearer <token>`. Пользователь каждый раз проверяется по БД, заблокированный пользователь теряет доступ и с действующим токеном. Логин использует JSON, это Bearer JWT, не OAuth2 form endpoint.

Вход:

```json
{"email":"ivanov@susu.ru","password":"Your-demo-password-123"}
```

Создание:

```json
{"title":"Не работает личный кабинет","description":"После входа появляется ошибка.","category_id":3}
```

ID категории получите из `/categories`; не полагайтесь на порядок seed. Сервер задаёт автора, статус «Новая», приоритет «Средняя», даты и срок: время создания + sla_hours календарных часов. В текущей схеме дата хранится как UTC без timezone, API отдаёт UTC с суффиксом Z. Ответственного пока нет. Категория обязательна.

Заголовок: 1–200 символов после удаления пробелов по краям. Описание: 1–10000. Дополнительные поля запрещены: нельзя подменить автора, статус, приоритет, исполнителя или ai_confidence. PATCH принимает только title/description, пустой объект и null отклоняются. Список сортируется по created_at и id по убыванию; limit 1–100, offset >= 0.

Ошибки: 401 — вход/токен; 404 — заявка отсутствует или принадлежит другому; 409 — редактирование не новой заявки; 422 — некорректные поля/категория; 503 — ошибка БД или отсутствуют справочники. Детали ошибок БД не выдаются клиенту. Заявка и её аудит записываются одной транзакцией. PATCH блокирует строку заявки до commit в PostgreSQL.

## Ручная проверка через Swagger

1. Выполните POST `/auth/login` с демонстрационным аккаунтом и вашим DEMO_PASSWORD.
2. Скопируйте access_token, нажмите Authorize и вставьте токен.
3. Получите категории, создайте заявку. Проверьте 201, Location, статус, приоритет и срок.
4. Откройте список и созданную заявку, исправьте заголовок через PATCH.
5. Войдите другим аккаунтом (например, petrov@susu.ru). Первая заявка не должна появиться в его списке, её GET/PATCH должны вернуть 404.
6. Отправьте пустой заголовок, неизвестную категорию или applicant_id: ожидается 422.
7. Уберите авторизацию: ожидается 401.
8. В тестовой БД переведите заявку в «В работе»; PATCH должен вернуть 409.

Проверка записи:

```sql
SELECT id, applicant_id, title, status_id, priority_id, deadline_at FROM requests ORDER BY id DESC LIMIT 5;
SELECT user_id, action, entity_id FROM audit_log WHERE action IN ('request.create', 'request.update') ORDER BY id DESC LIMIT 5;
```

## Автоматические тесты

```powershell
pytest -q
```

По умолчанию тесты используют отдельную SQLite в памяти с внешними ключами. Тестируется HTTP-контракт, JWT, изоляция пользователей, пагинация, валидация, срок, аудит, редактирование и откат при отказе записи аудита.

Для интеграционного прогона создайте **отдельную одноразовую PostgreSQL БД**:

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg://postgres:password@localhost:5432/helpdesk_test"
$env:ALLOW_TEST_DATABASE_RESET = "1"
pytest -q
```

Этот режим создаёт и удаляет таблицы в указанной БД. Никогда не указывайте рабочую БД. `DATABASE_URL` приложения тестами не используется для данных; тестовая сессия подменяется через dependency override.

GitHub Actions отдельно применяет настоящие Alembic-миграции на PostgreSQL 15, выполняет seed дважды, затем запускает тесты. Миграции существующей схемы SQLite не поддерживают; для них необходим PostgreSQL.

Основа реализации авторизации: [официальная документация FastAPI](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/). Здесь вход JSON адаптирован под контракт приложения.
