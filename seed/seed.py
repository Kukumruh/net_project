import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timedelta, UTC
from decimal import Decimal

from sqlalchemy import select

from app.database import SessionLocal
from app.models import (
    User,
    Role,
    Category,
    Priority,
    Status,
    Request,
    RequestComment,
    Attachment,
    FaqArticle,
    ResponsibleAssignment,
    Notification,
    RolePermission,
    ClassificationKeyword,
    AuditLog,
    SystemSetting,
)

# Настройки
NOW = default=lambda: datetime.now(UTC)

# Роли
ROLES = [
    {
        "name": "Заявитель",
    },
    {
        "name": "Оператор",
    },
    {
        "name": "Администратор",
    },
]


# Категории
CATEGORIES = [
    {
        "name": "Общежитие",
        "description": "Вопросы проживания, ремонта и бытовых условий в общежитии",
    },
    {
        "name": "Учёба",
        "description": "Вопросы расписания, экзаменов, дисциплин и учебного процесса",
    },
    {
        "name": "ИТ",
        "description": "Компьютеры, Wi-Fi, личный кабинет и информационные системы",
    },
    {
        "name": "Финансы",
        "description": "Оплата обучения, договоры и финансовые вопросы",
    },
    {
        "name": "Стипендия",
        "description": "Начисление и получение академических и социальных стипендий",
    },
    {
        "name": "Библиотека",
        "description": "Книги, читательские билеты и электронные ресурсы",
    },
    {
        "name": "Деканат",
        "description": "Справки, заявления и административные документы",
    },
    {
        "name": "Инфраструктура",
        "description": "Аудитории, освещение, оборудование и помещения",
    },
]

# Приоритеты
PRIORITIES = [
    {
        "name": "Критическая",
        "sla_hours": 4,
    },
    {
        "name": "Высокая",
        "sla_hours": 12,
    },
    {
        "name": "Средняя",
        "sla_hours": 48,
    },
    {
        "name": "Низкая",
        "sla_hours": 120,
    },
]


# Статусы
STATUSES = [
    {
        "name": "Новая",
        "sort_order": 1,
    },
    {
        "name": "Назначена",
        "sort_order": 2,
    },
    {
        "name": "В работе",
        "sort_order": 3,
    },
    {
        "name": "На проверке",
        "sort_order": 4,
    },
    {
        "name": "Решена",
        "sort_order": 5,
    },
    {
        "name": "Отклонена",
        "sort_order": 6,
    },
    {
        "name": "Закрыта",
        "sort_order": 7,
    },
]


# Пользователи
USERS = [
    # Заявители

    {
        "full_name": "Иванов Иван Иванович",
        "email": "ivanov@susu.ru",
        "password_hash": "demo_hash_001",
        "role": "Заявитель",
        "telegram_chat_id": "100000001",
        "department": "Институт информационных технологий",
    },
    {
        "full_name": "Петров Пётр Сергеевич",
        "email": "petrov@susu.ru",
        "password_hash": "demo_hash_002",
        "role": "Заявитель",
        "telegram_chat_id": "100000002",
        "department": "Институт строительства",
    },
    {
        "full_name": "Сидоров Алексей Дмитриевич",
        "email": "sidorov@susu.ru",
        "password_hash": "demo_hash_003",
        "role": "Заявитель",
        "telegram_chat_id": "100000003",
        "department": "Факультет экономики",
    },
    {
        "full_name": "Кузнецов Максим Андреевич",
        "email": "kuznetsov@susu.ru",
        "password_hash": "demo_hash_004",
        "role": "Заявитель",
        "telegram_chat_id": "100000004",
        "department": "Институт информационных технологий",
    },
    {
        "full_name": "Попов Артём Михайлович",
        "email": "popov@susu.ru",
        "password_hash": "demo_hash_005",
        "role": "Заявитель",
        "telegram_chat_id": "100000005",
        "department": "Гуманитарный институт",
    },
    {
        "full_name": "Смирнов Михаил Олегович",
        "email": "smirnov@susu.ru",
        "password_hash": "demo_hash_006",
        "role": "Заявитель",
        "telegram_chat_id": "100000006",
        "department": "Институт строительства",
    },
    {
        "full_name": "Васильев Никита Викторович",
        "email": "vasiliev@susu.ru",
        "password_hash": "demo_hash_007",
        "role": "Заявитель",
        "telegram_chat_id": "100000007",
        "department": "Факультет экономики",
    },
    {
        "full_name": "Морозов Андрей Николаевич",
        "email": "morozov@susu.ru",
        "password_hash": "demo_hash_008",
        "role": "Заявитель",
        "telegram_chat_id": "100000008",
        "department": "Институт информационных технологий",
    },
    {
        "full_name": "Новиков Сергей Петрович",
        "email": "novikov@susu.ru",
        "password_hash": "demo_hash_009",
        "role": "Заявитель",
        "telegram_chat_id": "100000009",
        "department": "Гуманитарный институт",
    },
    {
        "full_name": "Фёдоров Дмитрий Алексеевич",
        "email": "fedorov@susu.ru",
        "password_hash": "demo_hash_010",
        "role": "Заявитель",
        "telegram_chat_id": "100000010",
        "department": "Институт строительства",
    },
    {
        "full_name": "Волкова Анна Сергеевна",
        "email": "volkova@susu.ru",
        "password_hash": "demo_hash_011",
        "role": "Заявитель",
        "telegram_chat_id": "100000011",
        "department": "Факультет экономики",
    },
    {
        "full_name": "Орлова Мария Дмитриевна",
        "email": "orlova@susu.ru",
        "password_hash": "demo_hash_012",
        "role": "Заявитель",
        "telegram_chat_id": "100000012",
        "department": "Институт информационных технологий",
    },
    {
        "full_name": "Козлова Екатерина Андреевна",
        "email": "kozlova@susu.ru",
        "password_hash": "demo_hash_013",
        "role": "Заявитель",
        "telegram_chat_id": "100000013",
        "department": "Гуманитарный институт",
    },
    {
        "full_name": "Михайлова Дарья Михайловна",
        "email": "mihailova@susu.ru",
        "password_hash": "demo_hash_014",
        "role": "Заявитель",
        "telegram_chat_id": "100000014",
        "department": "Институт строительства",
    },
    {
        "full_name": "Соколова Анастасия Олеговна",
        "email": "sokolova@susu.ru",
        "password_hash": "demo_hash_015",
        "role": "Заявитель",
        "telegram_chat_id": "100000015",
        "department": "Факультет экономики",
    },
    {
        "full_name": "Лебедева Полина Викторовна",
        "email": "lebedeva@susu.ru",
        "password_hash": "demo_hash_016",
        "role": "Заявитель",
        "telegram_chat_id": "100000016",
        "department": "Институт информационных технологий",
    },
    {
        "full_name": "Павлова Ольга Николаевна",
        "email": "pavlova@susu.ru",
        "password_hash": "demo_hash_017",
        "role": "Заявитель",
        "telegram_chat_id": "100000017",
        "department": "Гуманитарный институт",
    },
    {
        "full_name": "Алексеева Елена Петровна",
        "email": "alekseeva@susu.ru",
        "password_hash": "demo_hash_018",
        "role": "Заявитель",
        "telegram_chat_id": "100000018",
        "department": "Институт строительства",
    },
    {
        "full_name": "Никитина Виктория Сергеевна",
        "email": "nikitina@susu.ru",
        "password_hash": "demo_hash_019",
        "role": "Заявитель",
        "telegram_chat_id": "100000019",
        "department": "Факультет экономики",
    },
    {
        "full_name": "Захарова София Андреевна",
        "email": "zakharova@susu.ru",
        "password_hash": "demo_hash_020",
        "role": "Заявитель",
        "telegram_chat_id": "100000020",
        "department": "Институт информационных технологий",
    },
    {
        "full_name": "Романова Ксения Дмитриевна",
        "email": "romanova@susu.ru",
        "password_hash": "demo_hash_021",
        "role": "Заявитель",
        "telegram_chat_id": "100000021",
        "department": "Гуманитарный институт",
    },
    {
        "full_name": "Беляев Илья Сергеевич",
        "email": "belyaev@susu.ru",
        "password_hash": "demo_hash_022",
        "role": "Заявитель",
        "telegram_chat_id": "100000022",
        "department": "Институт строительства",
    },
    {
        "full_name": "Громов Денис Андреевич",
        "email": "gromov@susu.ru",
        "password_hash": "demo_hash_023",
        "role": "Заявитель",
        "telegram_chat_id": "100000023",
        "department": "Факультет экономики",
    },
    {
        "full_name": "Виноградова Алиса Олеговна",
        "email": "vinogradova@susu.ru",
        "password_hash": "demo_hash_024",
        "role": "Заявитель",
        "telegram_chat_id": "100000024",
        "department": "Институт информационных технологий",
    },
    {
        "full_name": "Королёв Роман Викторович",
        "email": "korolev@susu.ru",
        "password_hash": "demo_hash_025",
        "role": "Заявитель",
        "telegram_chat_id": "100000025",
        "department": "Гуманитарный институт",
    },

    # Операторы
    {
        "full_name": "Александр Смирнов",
        "email": "operator1@susu.ru",
        "password_hash": "demo_hash_026",
        "role": "Оператор",
        "telegram_chat_id": "200000001",
        "department": "Центр поддержки студентов",
    },
    {
        "full_name": "Елена Кузнецова",
        "email": "operator2@susu.ru",
        "password_hash": "demo_hash_027",
        "role": "Оператор",
        "telegram_chat_id": "200000002",
        "department": "Центр поддержки студентов",
    },
    {
        "full_name": "Дмитрий Попов",
        "email": "operator3@susu.ru",
        "password_hash": "demo_hash_028",
        "role": "Оператор",
        "telegram_chat_id": "200000003",
        "department": "ИТ-служба",
    },
    {
        "full_name": "Ольга Васильева",
        "email": "operator4@susu.ru",
        "password_hash": "demo_hash_029",
        "role": "Оператор",
        "telegram_chat_id": "200000004",
        "department": "Деканат",
    },

    # Администратор
    {
        "full_name": "Сергей Морозов",
        "email": "admin@susu.ru",
        "password_hash": "demo_hash_030",
        "role": "Администратор",
        "telegram_chat_id": "300000001",
        "department": "Администрация системы",
    },
]


# Права
ROLE_PERMISSIONS = [
    ("Заявитель", "create_request", True),
    ("Заявитель", "view_own_requests", True),
    ("Заявитель", "comment_own_request", True),
    ("Заявитель", "upload_attachment", True),
    ("Заявитель", "view_faq", True),
    ("Заявитель", "view_all_requests", False),

    ("Оператор", "create_request", True),
    ("Оператор", "view_own_requests", True),
    ("Оператор", "view_all_requests", True),
    ("Оператор", "change_request_status", True),
    ("Оператор", "assign_request", True),
    ("Оператор", "comment_request", True),
    ("Оператор", "upload_attachment", True),
    ("Оператор", "manage_faq", True),

    ("Администратор", "manage_users", True),
    ("Администратор", "manage_roles", True),
    ("Администратор", "manage_system_settings", True),
    ("Администратор", "view_audit_log", True),
    ("Администратор", "view_all_requests", True),
    ("Администратор", "assign_request", True),
    ("Администратор", "change_request_status", True),
    ("Администратор", "manage_faq", True),
]


# FAQ
FAQS = [
    (3, "Что делать, если не работает Wi-Fi?",
     "Проверьте подключение устройства и попробуйте подключиться повторно."),

    (3, "Как восстановить пароль от личного кабинета?",
     "Используйте форму восстановления пароля на странице авторизации."),

    (1, "Куда сообщить о неисправности в комнате?",
     "Создайте заявку в категории «Общежитие» и укажите номер корпуса и комнаты."),

    (1, "Что делать при отсутствии горячей воды?",
     "Создайте заявку с указанием корпуса и номера комнаты."),

    (5, "Почему не начислена стипендия?",
     "Проверьте наличие необходимых документов и статус назначения стипендии."),

    (4, "Где узнать информацию об оплате?",
     "Информация об оплате доступна в личном кабинете студента."),

    (2, "Как узнать расписание занятий?",
     "Актуальное расписание размещается в университетской информационной системе."),

    (7, "Как получить справку с места обучения?",
     "Создайте обращение в деканат с указанием необходимого вида справки."),

    (6, "Как продлить срок возврата книги?",
     "Продление возможно через библиотечную систему."),

    (8, "Куда сообщить о неисправности оборудования?",
     "Создайте заявку и укажите номер аудитории и тип неисправности."),

    (2, "Что делать, если в расписании ошибка?",
     "Создайте заявку с указанием группы, дисциплины и ошибочной информации."),

    (5, "Когда перечисляется стипендия?",
     "Срок зависит от установленного университетом графика выплат."),

    (7, "Как подать заявление?",
     "Заполните форму обращения и приложите необходимые документы."),

    (4, "Как узнать задолженность по оплате?",
     "Проверьте финансовую информацию в личном кабинете."),

    (1, "Как сообщить о протечке?",
     "Создайте срочную заявку с указанием корпуса и комнаты."),
]


# Ключевые слова для API
KEYWORDS = {
    "Общежитие": [
        "не работает отопление",
        "сломался душ",
        "протекает кран",
        "протечка в комнате",
        "горячая вода",
        "сломался замок",
        "ремонт комнаты",
        "не работает розетка",
        "сломалась мебель",
        "не закрывается окно",
    ],

    "Учёба": [
        "ошибка в расписании",
        "экзамен",
        "не отображается дисциплина",
        "проблема с зачётом",
        "не вижу оценку",
        "учебный план",
        "изменили расписание",
        "учебный процесс",
        "неверно указана группа",
        "занятие",
    ],

    "ИТ": [
        "не работает Wi-Fi",
        "не подключается интернет",
        "личный кабинет",
        "забыл пароль",
        "не работает компьютер",
        "не запускается программа",
        "не работает принтер",
        "ошибка авторизации",
        "заблокирована учётная запись",
        "не приходит код",
    ],

    "Финансы": [
        "оплата обучения",
        "неверная сумма оплаты",
        "не отображается платёж",
        "квитанция",
        "договор",
        "задолженность по оплате",
        "финансовая информация",
        "возврат денежных средств",
        "не прошёл платёж",
        "начисление",
    ],

    "Стипендия": [
        "не начислили стипендию",
        "не пришла стипендия",
        "академическая стипендия",
        "социальная стипендия",
        "размер стипендии",
        "задержка стипендии",
        "условия получения стипендии",
        "документы для стипендии",
    ],

    "Библиотека": [
        "не могу найти книгу",
        "нужна книга",
        "продлить книгу",
        "библиотечный билет",
        "электронная библиотека",
        "штраф за книгу",
        "возврат книги",
        "читательский билет",
    ],

    "Деканат": [
        "справка с места учёбы",
        "получить справку",
        "подать заявление",
        "вопрос в деканат",
        "нужен документ",
        "академический отпуск",
        "перевод на другую программу",
        "восстановление в университете",
    ],

    "Инфраструктура": [
        "не работает проектор",
        "сломался компьютер в аудитории",
        "не работает освещение",
        "сломана парта",
        "сломался стул",
        "проблема с аудиторией",
        "не работает кондиционер",
        "неисправно оборудование",
    ],
}


# Заявки
REQUEST_EXAMPLES = [
    (
        "Не работает Wi-Fi в общежитии",
        "Не удаётся подключиться к университетской сети Wi-Fi.",
        "ИТ",
        "Высокая",
    ),
    (
        "Протечка крана",
        "В санузле постоянно протекает кран.",
        "Общежитие",
        "Критическая",
    ),
    (
        "Ошибка в расписании",
        "В расписании указана неверная аудитория.",
        "Учёба",
        "Средняя",
    ),
    (
        "Не отображается оплата",
        "Произведённая оплата пока не отображается в личном кабинете.",
        "Финансы",
        "Средняя",
    ),
    (
        "Не начислена стипендия",
        "Стипендия за текущий период не поступила.",
        "Стипендия",
        "Высокая",
    ),
    (
        "Продление книги",
        "Необходимо продлить срок возврата книги.",
        "Библиотека",
        "Низкая",
    ),
    (
        "Нужна справка",
        "Необходимо получить справку с места обучения.",
        "Деканат",
        "Средняя",
    ),
    (
        "Не работает проектор",
        "Проектор в аудитории не включается.",
        "Инфраструктура",
        "Высокая",
    ),
]


# Вспомогательные функции
def get_by_name(db, model, name):
    return db.scalar(
        select(model).where(model.name == name)
    )


def get_role(db, name):
    return db.scalar(
        select(Role).where(Role.name == name)
    )


def get_category(db, name):
    return db.scalar(
        select(Category).where(Category.name == name)
    )


def get_priority(db, name):
    return db.scalar(
        select(Priority).where(Priority.name == name)
    )


def get_status(db, name):
    return db.scalar(
        select(Status).where(Status.name == name)
    )


# Основной seed
def seed():
    db = SessionLocal()

    try:
        print("Начинаем заполнение базы данных...")

        # Роли
        roles = {}

        for data in ROLES:
            role = get_role(db, data["name"])

            if role is None:
                role = Role(**data)
                db.add(role)
                db.flush()

            roles[data["name"]] = role

        print("✓ Роли")


        # Категории
        categories = {}

        for data in CATEGORIES:
            category = get_category(db, data["name"])

            if category is None:
                category = Category(**data)
                db.add(category)
                db.flush()

            categories[data["name"]] = category

        print("Категории")


        # Приоритеты
        priorities = {}

        for data in PRIORITIES:
            priority = get_priority(db, data["name"])

            if priority is None:
                priority = Priority(**data)
                db.add(priority)
                db.flush()

            priorities[data["name"]] = priority

        print("Приоритеты")


        # Статусы
        statuses = {}

        for data in STATUSES:
            status = get_status(db, data["name"])

            if status is None:
                status = Status(**data)
                db.add(status)
                db.flush()

            statuses[data["name"]] = status

        print("Статусы")


        # Пользователи
        users = {}

        for data in USERS:
            user = db.scalar(
                select(User).where(User.email == data["email"])
            )

            if user is None:
                user = User(
                    full_name=data["full_name"],
                    email=data["email"],
                    password_hash=data["password_hash"],
                    role_id=roles[data["role"]].id,
                    telegram_chat_id=data["telegram_chat_id"],
                    department=data["department"],
                    is_active=True,
                    created_at=NOW,
                )

                db.add(user)
                db.flush()

            users[data["email"]] = user

        print("✓ Пользователи")


        # Исполнители ролей
        for role_name, action_code, is_allowed in ROLE_PERMISSIONS:

            role = roles[role_name]

            existing = db.scalar(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.action_code == action_code,
                )
            )

            if existing is None:
                db.add(
                    RolePermission(
                        role_id=role.id,
                        action_code=action_code,
                        is_allowed=is_allowed,
                    )
                )

        print("✓ Права")


        # Разрешения ролей
        assignments = {
            "Общежитие": "operator1@susu.ru",
            "Учёба": "operator4@susu.ru",
            "ИТ": "operator3@susu.ru",
            "Финансы": "operator2@susu.ru",
            "Стипендия": "operator2@susu.ru",
            "Библиотека": "operator2@susu.ru",
            "Деканат": "operator4@susu.ru",
            "Инфраструктура": "operator1@susu.ru",
        }

        for category_name, email in assignments.items():

            category = categories[category_name]
            user = users[email]

            existing = db.scalar(
                select(ResponsibleAssignment).where(
                    ResponsibleAssignment.category_id == category.id
                )
            )

            if existing is None:
                db.add(
                    ResponsibleAssignment(
                        category_id=category.id,
                        user_id=user.id,
                    )
                )

        print("Ответственные")


        # FAQ
        for category_id, question, answer in FAQS:

            category = list(categories.values())[category_id - 1]

            existing = db.scalar(
                select(FaqArticle).where(
                    FaqArticle.question == question
                )
            )

            if existing is None:
                db.add(
                    FaqArticle(
                        category_id=category.id,
                        question=question,
                        answer=answer,
                        created_at=NOW,
                    )
                )

        print("FAQ")


        # Ключевые слова для классификации
        for category_name, keywords in KEYWORDS.items():

            category = categories[category_name]

            for keyword in keywords:

                existing = db.scalar(
                    select(ClassificationKeyword).where(
                        ClassificationKeyword.category_id == category.id,
                        ClassificationKeyword.keyword_or_example == keyword,
                    )
                )

                if existing is None:
                    db.add(
                        ClassificationKeyword(
                            category_id=category.id,
                            keyword_or_example=keyword,
                            created_at=NOW,
                        )
                    )

        print("Ключевые слова")


        # Запросы
        request_list = []

        for i in range(1, 101):

            applicant = list(users.values())[(i - 1) % 25]

            example = REQUEST_EXAMPLES[(i - 1) % len(REQUEST_EXAMPLES)]

            title, description, category_name, priority_name = example

            category = categories[category_name]
            priority = priorities[priority_name]

            # Разные статусы для демонстрации
            status_names = [
                "Новая",
                "Назначена",
                "В работе",
                "На проверке",
                "Решена",
                "Отклонена",
                "Закрыта",
            ]

            status = statuses[
                status_names[(i - 1) % len(status_names)]
            ]

            # Для новых заявок ответственный пока не назначен
            if status.name == "Новая":
                responsible = None
            else:
                assignment = db.scalar(
                    select(ResponsibleAssignment).where(
                        ResponsibleAssignment.category_id == category.id
                    )
                )

                responsible = assignment.user if assignment else None

            created_at = NOW - timedelta(days=i % 30)

            deadline_at = (
                created_at +
                timedelta(hours=priority.sla_hours)
            )

            # Проверяем, есть ли уже такая seed-заявка
            seed_title = f"[SEED] {title} #{i}"

            existing = db.scalar(
                select(Request).where(
                    Request.title == seed_title
                )
            )

            if existing is not None:
                request_list.append(existing)
                continue

            request = Request(
                applicant_id=applicant.id,
                category_id=category.id,
                priority_id=priority.id,
                status_id=status.id,
                responsible_id=(
                    responsible.id
                    if responsible
                    else None
                ),
                title=seed_title,
                description=description,
                ai_confidence=Decimal(
                    str(
                        round(
                            0.72 + ((i * 17) % 25) / 100,
                            3
                        )
                    )
                ),
                created_at=created_at,
                updated_at=created_at,
                deadline_at=deadline_at,
            )

            db.add(request)
            db.flush()

            request_list.append(request)

        print("Заявки")


        # Комментарии
        comments = [
            "Заявка принята в работу.",
            "Проблема передана ответственному сотруднику.",
            "Проводится проверка информации.",
            "Необходимо предоставить дополнительные сведения.",
            "Работы по обращению выполнены.",
            "Проблема устранена.",
        ]

        for i in range(80):

            request = request_list[i % len(request_list)]

            author = (
                list(users.values())[i % 25]
                if i % 3 == 0
                else list(users.values())[25 + (i % 4)]
            )

            existing = db.scalar(
                select(RequestComment).where(
                    RequestComment.request_id == request.id,
                    RequestComment.comment_text == comments[i % len(comments)],
                )
            )

            if existing is not None:
                continue

            db.add(
                RequestComment(
                    request_id=request.id,
                    author_id=author.id,
                    comment_text=comments[i % len(comments)],
                    is_internal=(i % 7 == 0),
                    created_at=NOW - timedelta(days=i % 20),
                )
            )

        print("Комментарии")


        # Вложения
        for i in range(50):

            request = request_list[(i * 2) % len(request_list)]

            uploader = (
                list(users.values())[i % 25]
                if i % 4 != 0
                else list(users.values())[25 + (i % 4)]
            )

            extension = (
                ".pdf"
                if i % 3 == 0
                else ".jpg"
                if i % 2 == 0
                else ".png"
            )

            file_name = f"seed_attachment_{i + 1}{extension}"

            existing = db.scalar(
                select(Attachment).where(
                    Attachment.file_name == file_name
                )
            )

            if existing is not None:
                continue

            db.add(
                Attachment(
                    request_id=request.id,
                    file_name=file_name,
                    file_path=(
                        f"uploads/requests/"
                        f"{request.id}/"
                        f"{file_name}"
                    ),
                    uploaded_by=uploader.id,
                    uploaded_at=NOW - timedelta(days=i % 15),
                )
            )

        print("Вложения")


        # Уведомления
        for i in range(120):

            request = request_list[i % len(request_list)]

            if i % 3 == 0:
                recipient = request.applicant_id
            else:
                recipient = request.responsible_id

            if recipient is None:
                recipient = users["operator1@susu.ru"].id

            channel = "email" if i % 4 == 0 else "telegram"

            existing = db.scalar(
                select(Notification).where(
                    Notification.request_id == request.id,
                    Notification.recipient_id == recipient,
                    Notification.channel == channel,
                )
            )

            if existing is not None:
                continue

            db.add(
                Notification(
                    request_id=request.id,
                    recipient_id=recipient,
                    channel=channel,
                    telegram_message_id=(
                        None
                        if channel == "email"
                        else f"seed_msg_{i + 1}"
                    ),
                    status=(
                        "failed"
                        if i % 10 == 0
                        else "sent"
                    ),
                    sent_at=NOW - timedelta(days=i % 15),
                )
            )

        print("Уведомления")


        # Журнал аудита (audit log)
        actions = [
            "create_request",
            "assign_request",
            "change_status",
            "add_comment",
            "upload_attachment",
            "update_request",
            "close_request",
        ]

        for i in range(150):

            request = request_list[i % len(request_list)]

            if i % 5 == 0:
                user = users["admin@susu.ru"]
            elif i % 2 == 0:
                user = list(users.values())[25 + (i % 4)]
            else:
                user = list(users.values())[i % 25]

            db.add(
                AuditLog(
                    user_id=user.id,
                    action=actions[i % len(actions)],
                    entity_type="request",
                    entity_id=request.id,
                    created_at=NOW - timedelta(days=i % 30),
                )
            )

        print("Audit log")


        # Системные настройки
        SETTINGS = [
            (
                "sla_default_hours",
                "48",
                "Срок обработки заявки по умолчанию в часах.",
            ),
            (
                "telegram_notifications_enabled",
                "true",
                "Включение уведомлений Telegram.",
            ),
            (
                "email_notifications_enabled",
                "true",
                "Включение уведомлений по электронной почте.",
            ),
            (
                "ai_classification_enabled",
                "true",
                "Включение автоматической классификации заявок.",
            ),
            (
                "ai_confidence_threshold",
                "0.70",
                "Минимальная уверенность модели классификации.",
            ),
            (
                "max_attachment_size_mb",
                "20",
                "Максимальный размер вложения в мегабайтах.",
            ),
            (
                "backup_schedule",
                "daily",
                "Периодичность резервного копирования.",
            ),
            (
                "request_auto_close_days",
                "7",
                "Количество дней до автоматического закрытия заявки.",
            ),
            (
                "system_name",
                "SUSU HelpDesk",
                "Название системы.",
            ),
            (
                "support_email",
                "support@susu.ru",
                "Электронная почта службы поддержки.",
            ),
            (
                "maintenance_mode",
                "false",
                "Режим технического обслуживания.",
            ),
        ]

        for key, value, description in SETTINGS:

            existing = db.scalar(
                select(SystemSetting).where(
                    SystemSetting.param_key == key
                )
            )

            if existing is None:
                db.add(
                    SystemSetting(
                        param_key=key,
                        param_value=value,
                        description=description,
                        updated_at=NOW,
                    )
                )

        print("Системные настройки")

        # Сохранение
        db.commit()

        print()
        print("=" * 50)
        print("SEED УСПЕШНО ВЫПОЛНЕН")
        print("=" * 50)
        print("Роли:                 3")
        print("Категории:            8")
        print("Приоритеты:           4")
        print("Статусы:              7")
        print("Пользователи:         30")
        print("Заявки:               100")
        print("Комментарии:          80")
        print("Вложения:             50")
        print("FAQ:                  15")
        print("Уведомления:          120")
        print("Ключевые слова:       72")
        print("Audit log:            150")
        print("Системные настройки:  11")
        print("=" * 50)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()