# HR Telegram Bot для завода готовой еды Яндекс Лавки

---

<p align="left">
  <a href="https://www.python.org/" target="_blank">
    <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white&style=for-the-badge" alt="Python"/>
  </a>
  <a href="https://fastapi.tiangolo.com/" target="_blank">
    <img src="https://img.shields.io/badge/FastAPI-async-green?logo=fastapi&logoColor=white&style=for-the-badge" alt="FastAPI"/>
  </a>
  <a href="https://www.sqlalchemy.org/" target="_blank">
    <img src="https://img.shields.io/badge/SQLAlchemy-ORM-764abc?logo=sqlalchemy&logoColor=white&style=for-the-badge" alt="SQLAlchemy"/>
  </a>
  <a href="https://alembic.sqlalchemy.org/" target="_blank">
    <img src="https://img.shields.io/badge/Alembic-migrations-44aadd?logo=alembic&logoColor=white&style=for-the-badge" alt="Alembic"/>
  </a>
  <a href="https://www.postgresql.org/" target="_blank">
    <img src="https://img.shields.io/badge/PostgreSQL-db-336791?logo=postgresql&logoColor=white&style=for-the-badge" alt="PostgreSQL"/>
  </a>
  <a href="https://www.docker.com/" target="_blank">
    <img src="https://img.shields.io/badge/Docker-container-2496ed?logo=docker&logoColor=white&style=for-the-badge" alt="Docker"/>
  </a>
  <a href="https://github.com/aminalaee/sqladmin" target="_blank">
    <img src="https://img.shields.io/badge/SQLAdmin-admin-2d2d2d?logo=python&logoColor=white&style=for-the-badge" alt="SQLAdmin"/>
  </a>
  <a href="https://python-telegram-bot.org/" target="_blank">
    <img src="https://img.shields.io/badge/python—telegram—bot-python%20%2B%20telegram-306998?logo=python&logoColor=white&style=for-the-badge" alt="Python Telegram Bot"/>
  </a>
  <a href="https://jinja.palletsprojects.com/" target="_blank">
    <img src="https://img.shields.io/badge/Jinja2-templates-b41717?logo=jinja&logoColor=white&style=for-the-badge" alt="Jinja2"/>
  </a>
  <a href="https://www.python-httpx.org/" target="_blank">
    <img src="https://img.shields.io/badge/httpx-async-ef3b2d?logo=python&logoColor=white&style=for-the-badge" alt="httpx"/>
  </a>
  <a href="https://docs.pydantic.dev/" target="_blank">
    <img src="https://img.shields.io/badge/Pydantic-validation-008489?logo=pydantic&logoColor=white&style=for-the-badge" alt="Pydantic"/>
  </a>
  <a href="https://docs.astral.sh/ruff/" target="_blank">
    <img src="https://img.shields.io/badge/Ruff-linter-333333?logo=ruff&logoColor=white&style=for-the-badge" alt="Ruff"/>
  </a>
  <a href="https://pre-commit.com/" target="_blank">
    <img src="https://img.shields.io/badge/pre--commit-hooks-FAB040?logo=pre-commit&logoColor=white&style=for-the-badge" alt="pre-commit"/>
  </a>
  <a href="https://github.com/features/actions" target="_blank">
    <img src="https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-2088FF?logo=githubactions&logoColor=white&style=for-the-badge" alt="GitHub Actions"/>
  </a>
  </a>
  <a href="https://github.com/bbd03/check-swear" target="_blank">
    <img src="https://img.shields.io/badge/check--swear-powered--by--bbd03-2088FF?logo=github&logoColor=white&style=for-the-badge" alt="check-swear"/>
  </a>
</p>

## Описание проекта
**HR Telegram Bot для завода готовой еды Яндекс Лавки** — это корпоративное решение для автоматизации HR-коммуникаций и работы с запросами сотрудников через удобный Telegram-бот.
В проект входит:
- Асинхронный сервер на FastAPI (backend + OpenAPI + API)
- Веб-админка (на базе SQLAdmin/Jinja2) для управления пользователями, контентом, HR-запросами
- Телеграм-бот для сотрудников завода с авторизацией, интерактивными меню, заявками HR
- Единая интеграция: все части разворачиваются и обновляются в рамках одного монорепозитория

---

## Основные возможности
- Единая административная панель для управления сотрудниками, деревом контента, картинками, заявками HR
- Импорт пользователей из Excel-файлов через админку
- Интеграция с Telegram-ботом
- Гибкое дерево информации (узлы, кнопки, изображения) с быстрым обновлением контента
- Открытое API с документацией OpenAPI/Swagger
- Полная докеризация: быстрый запуск, обновление и деплой на сервер через Docker Compose
- Автоматический деплой через GitHub Actions: тесты, сборка, публикация Docker-образов и автозагрузка на сервер

---

### [Telegram-бот](https://t.me/lavka_hr_4_bot)
- Авторизация сотрудников по Telegram ID
- Быстрые заявки HR, просмотр и отслеживание их статусов
- Навигация по информационному дереву (разделы, инструкции, документы)
- Интерактивные меню, кастомные кнопки

**Типовой сценарий**
- Сотрудник запускает бота и проходит авторизацию.
- Получает меню с возможными действиями.
- Может создать и отслеживать свой HR-запрос (вопрос, отпуск, пропуск и пр.).
- Получает ответы HR прямо в Telegram.

---

### [Административная панель](https://lavka4.rsateam.ru/admin)
- Управление всеми пользователями (роли, Telegram ID, статус, доступ)
- Импорт сотрудников из Excel (шаблон в интерфейсе)
- Редактирование дерева информации (узлы, кнопки, вложенность, изображения)
- Просмотр и обработка HR-заявок (отправка ответов в Telegram)

---

## API и документация

**[OpenAPI/Swagger](https://lavka4.rsateam.ru/docs)**

**Основные эндпоинты:**
- /api/v1/login/ — логин (JWT)
- /api/v1/logout/ — логаут
- /api/v1/auth/telegram — Telegram-авторизация
- /api/v1/nodes/root — корневой узел
- /api/v1/nodes/{id} — конкретный узел
- /api/v1/hr-request — создать HR-запрос
- /api/v1/hr-requests — HR-запросы пользователя
- /api/v1/import-users/upload — импорт пользователей

---

## Архитектура и структура репозитория

```
infra/                # Dockerfile, docker-compose, .env
  backend/            # Dockerfile backend
  bot/                # Dockerfile Telegram-бота
  data/               # fixtures и тестовые данные
src/
  app/                # FastAPI-приложение (backend + админка)
    admin/            # SQLAdmin-панель
    api/              # API endpoints (включая OpenAPI-спеку)
      endpoints/      # Конкретные реализации эндпоинтов
    core/             # Конфиги, инициализация, база
    models/           # SQLAlchemy-модели
    schemas/          # Pydantic-схемы
    services/         # Бизнес-логика
    static/           # css/js/images для админки
    scripts/          # Скрипты для загрузки данных
    main.py           # Точка входа backend
  bot/                # Исходники Telegram-бота
    handlers.py       # Обработчики команд и сообщений
    keyboards.py      # Кастомные клавиатуры
    callbacks.py      # Обработчик колбэков
    backend_client.py # Взаимодействие с backend API
    config.py         # Конфигурация бота
    constants.py      # Константы для бота
    main.py           # Точка входа бота
    services.py       # Вспомогательные сервисы бота
    render.py         # Обработка и отображение узлов
  alembic/            # Миграции базы данных
    versions/         # Файлы миграций
  node_images/        # Изображения для информационных узлов
templates/            # Jinja2-шаблоны для админки (SQLAdmin)
requirements-admin.txt    # Зависимости для админки/бэкенда
requirements-bot.txt      # Зависимости для бота
requirements-dev.txt      # Dev-зависимости
requirements_style.txt    # Стиль/линтеры
ruff.toml                 # Конфиг линтера ruff
README.md                 # Документация
```

---

## Быстрый старт (локально через Docker)

### 1. Клонируйте репозиторий и создайте файл .env в папке infra (пример — ниже).

### 2. Запустите инфраструктуру:
```bash
git clone git@github.com:Studio-Yandex-Practicum/zge_lavka_team4.git
cd zge_lavka_team4/infra
cp .env.example .env  # или создайте свой .env по примеру ниже
docker-compose up -d
```

### 3. Проверьте, что сервисы работают:
- Backend: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Админка: http://localhost:8000/admin

---

## Развертывание на сервере (production)

### Предварительные требования
- Сервер с Linux (Ubuntu 22.04+ рекомендуется)
- Docker и Docker Compose установлены - [инструкция](https://docs.docker.com/engine/install/)
- Выделенный домен с SSL (рекомендуется настроить через nginx/reverse-proxy)
- Созданы секреты и переменные окружения для деплоя

## Подготовка и деплой

### 1. Копируйте docker-compose.production.yml и .env:
```bash
mkdir -p /opt/lavka
cd /opt/lavka
# Скопируйте docker-compose.production.yml в /opt/lavka/docker-compose.yml
# Добавьте .env (пример ниже)
```

### 2. Настройте переменные в .env (см. пример ниже).

### 3. Откройте порт 8000 (или настройте reverse-proxy/nginx для SSL-домена).

### 4. Первый запуск:
```bash
docker compose pull
docker compose up -d
docker compose exec backend alembic -c src/alembic.ini upgrade head
```

### 5. После первого запуска — загрузите данные:
```bash
docker compose exec backend python -m src.app.scripts.load_data
```

### 6. Проверьте доступность:
- Backend: https://ваш_домен/
- Swagger: https://ваш_домен/docs
- Админка: https://ваш_домен/admin

### 7. Остановка проекта
```bash
docker-compose down
```

---

## CI/CD: Автоматический деплой через GitHub Actions

### Проект использует автодеплой при пуше в main:
- Запуск тестов, миграций и сборка Docker-образов на CI
- Публикация образов на Docker Hub
- Копирование и запуск обновлённых контейнеров на сервере по SSH
- Загрузка новых данных при обновлении

### Примерная логика деплоя:
```yml
on:
  push:
    branches: [ main ]

jobs:
  # ... (тесты и сборка)
  deploy:
    steps:
      - copy docker-compose.yml на сервер через ssh
      - docker compose pull && docker compose down && docker compose up -d
      - docker compose exec backend python -m src.app.scripts.load_data
```
### Требования к серверу:
- Доступ по SSH (через ключ), настроенные переменные окружения и Actions.

---


## Пример .env файла
```env
# --- Настройки базы данных ---
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=your_db_name
POSTGRES_SERVER=db
POSTGRES_PORT=5432

# --- Настройки backend ---
SECRET=your_secret_key
first_superuser_login=your_admin_login
first_superuser_password=your_admin_password
first_superuser_full_name=Your Admin Name
root_node_name=StartNode
root_node_text=Welcome to the bot!

# --- Telegram-бот ---
BOT_TOKEN=ваш_токен_бота
BACKEND_URL=http://backend:8000       # URL backend для бота
STACK_LIMIT=20                        # Глубина истории в дереве
STOP_WORDS=["word1","word2","word3"]  # Доп. слова для фильтрации запросов от пользователей

# --- Docker репозиторий для сборки контейнеров ---
DOCKER_REPO=docker_repo_name
```

---

## Возможные проблемы
- Проверьте, что все сервисы docker-compose работают (docker compose ps)
- Убедитесь, что все переменные .env корректны и заданы
- Миграции и начальные данные выполняются только изнутри контейнера backend
- Для импорта пользователей используйте шаблон Excel из админки

---

## Контакты/поддержка
Если нужна помощь по настройке или развитию бота, обратитесь к администрации проекта или откройте issue в репозитории.

---

## Авторы
**Наставник:**
  - [Роман Александров](https://github.com/teamofroman)

**Тимлид проекта:**
- [Максим Буряковский](https://github.com/mbur17)

**Команда Админки:**
- [Иванова Анна](https://github.com/IvalexAnna)
- [Кардава Дмитрий](https://github.com/DmitriyKardava)
- [Столповских Максим](https://github.com/maxstolpovskikh)
- [Серебренников Александр](https://github.com/serebrennikovalexander)

**Команда Бота:**
- [Похлебкина Елизавета](https://github.com/foxxybit)
- [Черепова Кунел](https://github.com/kunelcherepova)
- [Черепов Денис](https://github.com/qwetqwer111)
