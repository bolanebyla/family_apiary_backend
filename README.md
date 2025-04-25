# Семейная пасека


## 🛠 Технологии

- **Python 3.13+** - основной язык программирования
- **[FastAPI](https://fastapi.tiangolo.com/)** - современный веб-фреймворк для создания API
- **[Aiogram](https://docs.aiogram.dev/)** - фреймворк для создания Telegram ботов
- **[Dishka](https://github.com/just-work/dishka)** - контейнер внедрения зависимостей
- **[Pydantic](https://docs.pydantic.dev/)** - валидация данных и настройки
- **[Prometheus](https://prometheus.io/)** - мониторинг метрик
- **[Uvicorn](https://www.uvicorn.org/)** - ASGI-сервер
- **[UV](https://github.com/astral-sh/uv)** - современный и быстрый менеджер пакетов Python

## 📁 Структура проекта

```
family_apiary_backend/
├── src/
│   ├── family_apiary/
│   │   ├── module_1/                    # Модуль
│   │   │   ├── domain/                  # Доменный слой
│   │   │   │   ├── entities/            # Бизнес-сущности
│   │   │   │   ├── value_objects/       # Объекты-значения
│   │   │   │   ├── repositories/        # Репозитории для работы с доменными сущностями
│   │   │   │   └── __init__.py
│   │   │   ├── application/             # Прикладной слой
│   │   │   │   ├── services/            # Сервисы прикладного уровня
│   │   │   │   ├── interfaces/          # Интерфейсы для внешних систем
│   │   │   │   ├── dtos/                # Data Transfer Objects
│   │   │   │   ├── use_cases/           # Сценарии использования
│   │   │   │   └── __init__.py
│   │   │   └── infrastructure/          # Инфраструктурный слой
│   │   │       ├── db/                  # Работа с БД и реализации репозиториев
│   │   │       ├── api_controllers/     # API контроллеры
│   │   │       ├── ...
│   │   │       └── __init__.py
│   │   ├── module_2/
│   │   │   └── (...)             
│   │   ├── framework/                   # Общий фреймворк
│   │   │   ├── containers/              # Настройка DI контейнера
│   │   │   ├── api/                     # Общие компоненты API
│   │   │   ├── log/                     # Настройка логирования
│   │   │   └── __init__.py
│   │   └── run/                         # Точка входа
│   │       ├── api.py                   # Запуск API
│   │       ├── ...
│   │       └── __init__.py
│   └── commons/                         # Общие утилиты
```

## 🏗 Архитектура

Проект построен с использованием следующих архитектурных принципов:

- **Чистая архитектура** - разделение на слои (доменный, прикладной, инфраструктурный)
- **Dependency Injection** - использование Dishka для управления зависимостями
- **Domain-Driven Design** - фокус на бизнес-домене и его моделировании
- **REST API** - RESTful архитектура для веб-интерфейса
- **Telegram Bot** - интерфейс для взаимодействия через Telegram

## 🎯 Основные функции

- Отправка уведомлений через Telegram бота о поступлении новых заявок на покупку продукции

## 🚀 Запуск проекта

1. Установите зависимости с помощью uv:
```bash
uv pip install .
```

2. Настройте переменные окружения (создайте файл `.env`):
```
# Пример конфигурации
PRODUCTS_TG_CHAT_BOT_TOKEN=your_bot_token
PRODUCTS_TG_CHAT_BOT_PRODUCT_PURCHASE_REQUEST_NOTIFICATION_CHAT_ID=123456
```

3. Запустите сервер:
```bash
uvicorn src.family_apiary.main:app --reload
```

## 🧪 Тестирование

Для запуска тестов:
```bash
pytest
```

## 📊 Мониторинг

Метрики доступны по адресу `/metrics` (Prometheus)

## 🔍 Линтеры

В проекте используется [Ruff](https://github.com/astral-sh/ruff)

### Настройка линтера

Конфигурация линтера находится в файле `pyproject.toml` в секции `[tool.ruff]`.

### Запуск линтера

Для запуска линтера:
```bash
ruff check .
```

Для автоматического исправления проблем:
```bash
ruff check --fix .
```

## 🔒 Pre-commit

В проекте настроен pre-commit для автоматической проверки кода перед коммитом. Настройки pre-commit находятся в файле `.pre-commit-config.yaml`.

### Установка pre-commit

1. Установите pre-commit:
```bash
pip install pre-commit
```

2. Установите git hooks:
```bash
pre-commit install
```

После этого pre-commit будет автоматически запускаться перед каждым коммитом.

## 📝 Лицензия

