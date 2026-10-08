# net_project

# SUSU HelpDesk

## Единая система приёма и обработки заявок ЮУрГУ

Веб-система для регистрации, классификации, распределения и обработки заявок студентов и сотрудников Южно-Уральского государственного университета.

Система предназначена для централизованной работы с обращениями в различные подразделения университета: техническую поддержку, деканаты, бухгалтерию, общежития и другие службы.

Проект разрабатывается как командный backend-проект с использованием PostgreSQL, Python, SQLAlchemy и Alembic.

---

## Возможности системы

Планируемая система должна обеспечивать:

* регистрацию и хранение пользователей;
* создание и обработку заявок;
* классификацию заявок по категориям;
* назначение приоритетов и статусов;
* назначение ответственных сотрудников;
* добавление комментариев к заявкам;
* прикрепление файлов;
* отправку уведомлений;
* хранение часто задаваемых вопросов (FAQ);
* ведение журнала действий пользователей;
* хранение системных настроек;
* автоматическую классификацию заявок;
* интеграцию с Telegram.

На текущем этапе реализованы структура базы данных, ORM-модели, миграции, демонстрационное заполнение и первый REST API: JWT-вход, создание, просмотр и редактирование собственных заявок.

**Запуск API и проверка: [docs/API.md](docs/API.md).**

---

## Технологический стек

### Backend

* Python 3.13
* SQLAlchemy 2.0
* Alembic
* FastAPI
* Pydantic

### Database

* PostgreSQL 15
* Docker
* Docker Volume

### Frontend

Планируется:

* Vue 3
* JavaScript
* SPA

### Дополнительные технологии

Планируется использование:

* JWT / OAuth2
* pytest
* scikit-learn
* Telegram Bot API

Для совместной разработки используется Git и GitHub.

---

## Структура проекта

```text
DOT_NET/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   │
│   └── models/
│       ├── __init__.py
│       ├── user.py
│       ├── role.py
│       ├── category.py
│       ├── priority/
│       ├── status/
│       ├── request.py
│       ├── request_comment.py
│       ├── attachment.py
│       ├── faq_article.py
│       ├── responsible_assignment.py
│       ├── notification.py
│       ├── role_permission.py
│       ├── classification_keyword.py
│       ├── audit_log.py
│       └── system_setting.py
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   ├── README
│   └── script.py.mako
│
├── seed/
│   └── seed.py
│
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
├── docker-compose.yml
└── README.md
```

> Файл `.env` содержит локальные настройки и пароли и не должен загружаться в GitHub.

---

## Структура базы данных

В базе данных реализованы следующие таблицы:

| Таблица                   | Назначение                       |
| ------------------------- | -------------------------------- |
| `users`                   | Пользователи системы             |
| `requests`                | Заявки                           |
| `request_comments`        | Комментарии к заявкам            |
| `attachments`             | Прикреплённые файлы              |
| `faq_articles`            | Статьи FAQ                       |
| `categories`              | Категории заявок                 |
| `priorities`              | Приоритеты                       |
| `statuses`                | Статусы заявок                   |
| `responsible_assignments` | Назначение ответственных         |
| `notifications`           | Уведомления                      |
| `roles`                   | Роли пользователей               |
| `role_permissions`        | Права ролей                      |
| `classification_keywords` | Ключевые слова для классификации |
| `audit_log`               | Журнал действий                  |
| `system_settings`         | Системные настройки              |

Для изменения структуры базы данных используется Alembic.

---

## Требования

Для запуска проекта необходимы:

* Python 3.13 или совместимая версия;
* Docker Desktop;
* Git.

Проверить установленные версии:

```powershell
python --version
docker --version
docker compose version
git --version
```

---

## Установка

### 1. Клонирование репозитория

```powershell
git clone https://github.com/Kukumruh/net_project.git
cd net_project
```

Переключение на backend-ветку:

```powershell
git checkout feature/backend
```

---

### 2. Создание виртуального окружения

```powershell
python -m venv .venv
```

Активация виртуального окружения:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

### 3. Установка зависимостей

```powershell
pip install -r requirements.txt
```

---

## Настройка PostgreSQL

PostgreSQL запускается в Docker.

Для хранения данных используется внешний Docker Volume:

```text
student_requests_data
```

Создание Volume:

```powershell
docker volume create student_requests_data
```

Запуск PostgreSQL:

```powershell
docker compose up -d
```

Проверка запущенных контейнеров:

```powershell
docker ps
```

Ожидаемый контейнер:

```text
student_requests_postgres
```

---

## Настройка `.env`

Создайте файл `.env` на основе `.env.example`.

Пример:

```env
POSTGRES_DB=student_requests
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/student_requests
```

Значения `POSTGRES_PASSWORD` и другие секретные данные необходимо заменить на собственные.

Файл `.env` не должен добавляться в Git.

---

## Миграции базы данных

После запуска PostgreSQL необходимо применить миграции:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

Проверить текущую версию базы данных:

```powershell
.\.venv\Scripts\alembic.exe current
```

Для создания новой миграции после изменения моделей:

```powershell
.\.venv\Scripts\alembic.exe revision --autogenerate -m "описание изменения"
```

После проверки миграции:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

---

## Заполнение тестовыми данными

Для заполнения базы данных демонстрационными данными используется:

```text
seed/seed.py
```

Запуск на демонстрационной БД (общий demo-пароль):

```powershell
$env:DEMO_PASSWORD = "Your-demo-password-123"
.\.venv\Scripts\python.exe seed\seed.py
```

Текущий набор тестовых данных:

* 3 роли;
* 8 категорий;
* 4 приоритета;
* 7 статусов;
* 30 пользователей;
* 100 заявок;
* 80 комментариев;
* 50 вложений;
* 15 FAQ-записей;
* 120 уведомлений;
* 72 ключевых слова;
* 150 записей журнала аудита;
* 11 системных настроек.

---

## Ограничения целостности

В базе данных реализованы:

* первичные ключи (`PRIMARY KEY`);
* внешние ключи (`FOREIGN KEY`);
* ограничения `NOT NULL`;
* ограничения уникальности (`UNIQUE`).

В частности, уникальными являются:

* email пользователя;
* Telegram Chat ID пользователя;
* название роли;
* название категории;
* название приоритета;
* название статуса;
* ключ системной настройки;
* комбинация роли и разрешения;
* комбинация категории и пользователя в назначениях;
* комбинация категории и ключевого слова.

---

## Проверка базы данных

Для проверки количества записей можно использовать SQL-запросы:

```sql
SELECT COUNT(*) FROM users;
```

```sql
SELECT COUNT(*) FROM requests;
```

```sql
SELECT COUNT(*) FROM categories;
```

Для просмотра всех таблиц:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

Для проверки уникальных ограничений:

```sql
SELECT
    conname AS constraint_name,
    conrelid::regclass AS table_name,
    pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE contype = 'u'
ORDER BY conrelid::regclass::text, conname;
```

---

## Работа с Git

Проверить состояние репозитория:

```powershell
git status
```

Получить последние изменения:

```powershell
git pull
```

Добавить изменения:

```powershell
git add .
```

Создать коммит:

```powershell
git commit -m "Описание изменений"
```

Отправить изменения на GitHub:

```powershell
git push
```

Основная backend-ветка:

```text
feature/backend
```

---

## Работа команды

GitHub используется для хранения исходного кода и совместной разработки.

Важно: Git синхронизирует исходный код, но не синхронизирует содержимое локальной PostgreSQL-базы данных.

После получения изменений из GitHub необходимо обновить структуру базы данных:

```powershell
git pull
```

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

При необходимости загрузить тестовые данные:

```powershell
.\.venv\Scripts\python.exe seed\seed.py
```

---

## Текущий статус проекта

### Реализовано

* [x] Создан Python-проект
* [x] Настроен Docker
* [x] Запущен PostgreSQL 15
* [x] Создан внешний Docker Volume
* [x] Настроен SQLAlchemy 2.0
* [x] Созданы ORM-модели
* [x] Реализованы связи между таблицами
* [x] Настроен Alembic
* [x] Создана начальная миграция
* [x] Добавлены ограничения уникальности
* [x] Создана миграция уникальных ограничений
* [x] Заполнена база тестовыми данными
* [x] Код размещён в GitHub

### Планируется

* [x] Базовый REST API на FastAPI
* [x] JWT-авторизация и доступ к собственным заявкам
* [x] Создание, чтение и редактирование новых собственных заявок
* [ ] Операторские маршруты и управление статусами
* [ ] Разработка frontend на Vue 3
* [ ] Автоматическая классификация заявок
* [ ] Telegram-уведомления
* [ ] Автоматическое распределение заявок
* [x] Тесты базового API и PostgreSQL CI
* [ ] Развёртывание системы на сервере

---

## Назначение проекта

Проект разрабатывается в рамках учебной командной работы и предназначен для создания единой системы обработки обращений студентов и сотрудников ЮУрГУ.

Основная задача системы — объединить регистрацию заявок, их классификацию, назначение ответственных, контроль статусов и уведомление пользователей в едином информационном пространстве.

