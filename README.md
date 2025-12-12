# 📋 Task Manager API

Современный REST API для управления задачами с поддержкой команд, ролей и асинхронной обработки событий через Apache Kafka.

## ✨ Возможности

- 🔐 **Аутентификация и авторизация** - JWT токены с поддержкой refresh tokens
- 👥 **Система команд** - создание команд, управление участниками и ролями
- ✅ **Управление задачами** - CRUD операции, назначение исполнителей, статусы
- 🎭 **Ролевая модель** - Owner, Manager, User с различными правами доступа
- 📡 **Webhooks** - отправка уведомлений о событиях во внешние системы
- 🚀 **Асинхронная обработка** - Apache Kafka для событийно-ориентированной архитектуры
- 📊 **Панель администратора** - управление пользователями и командами
- 🐳 **Docker Ready** - полная контейнеризация приложения

## 🛠 Технологический стек

- **Framework**: FastAPI 0.124.2
- **Database**: PostgreSQL 15 + SQLAlchemy 2.0
- **Message Broker**: Apache Kafka + Zookeeper
- **Authentication**: JWT (python-jose)
- **Password Hashing**: Argon2 + Bcrypt + Passlib
- **Migration**: Alembic
- **Async HTTP**: aiohttp + aiokafka
- **Validation**: Pydantic 2.12

## 📁 Структура проекта

```
task_manager/
├── app/
│   ├── api/                    # API endpoints
│   │   ├── auth.py            # Аутентификация
│   │   ├── tasks.py           # Управление задачами
│   │   ├── teams.py           # Управление командами
│   │   ├── webhooks.py        # Webhooks
│   │   └── admin.py           # Админ панель
│   ├── core/                   # Ядро приложения
│   │   ├── config.py          # Конфигурация
│   │   └── security.py        # Безопасность, хеширование
│   ├── db/                     # База данных
│   │   └── session.py         # Сессии SQLAlchemy
│   ├── models/                 # ORM модели
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── team.py
│   │   └── webhook.py
│   ├── services/               # Бизнес-логика
│   │   ├── task_service.py
│   │   └── async_kafka_producer.py
│   ├── integrations/           # Внешние интеграции
│   │   └── kafka/
│   │       └── consumers/
│   └── main.py                # Точка входа
├── alembic/                   # Миграции БД
├── docker-compose.yml         # Docker конфигурация
├── Dockerfile                 # Docker образ
└── pyproject.toml            # Зависимости

```

### Основные эндпоинты

#### Аутентификация
```
POST   /auth/register          # Регистрация пользователя
POST   /auth/login             # Вход (получение токенов)
POST   /auth/refresh           # Обновление access token
GET    /auth/me                # Получение текущего пользователя
```

#### Задачи
```
GET    /tasks                  # Список задач команды
POST   /tasks                  # Создание задачи
GET    /tasks/{id}             # Получение задачи
PUT    /tasks/{id}             # Обновление задачи
DELETE /tasks/{id}             # Удаление задачи
PATCH  /tasks/{id}/assign      # Назначение исполнителя
PATCH  /tasks/{id}/status      # Изменение статуса
```

#### Команды
```
GET    /teams                  # Список всех команд
GET    /teams/my               # Мои команды
POST   /teams                  # Создание команды
GET    /teams/{id}/members     # Участники команды
POST   /teams/{id}/join        # Вступить в команду
DELETE /teams/{id}/leave       # Покинуть команду
PUT    /teams/{id}/members/{user_id}  # Изменить роль участника
DELETE /teams/{id}/members/{user_id}  # Удалить участника
```

#### Webhooks
```
GET    /webhooks               # Список webhooks команды
POST   /webhooks               # Создание webhook
DELETE /webhooks/{id}          # Удаление webhook
GET    /webhooks/{id}/logs     # История отправок
```

#### Администрирование
```
GET    /admin/users            # Список всех пользователей
PUT    /admin/users/{id}       # Обновление пользователя
DELETE /admin/users/{id}       # Удаление пользователя
GET    /admin/teams            # Список всех команд
```

## 🎭 Система ролей

### В команде

| Роль | Описание | Права |
|------|----------|-------|
| **Owner** | Создатель команды | Полный доступ: управление участниками, удаление команды, все права Manager |
| **Manager** | Менеджер | Управление задачами и рядовыми участниками (не может управлять admin'ами) |
| **User** | Участник | Просмотр задач команды, выполнение назначенных задач |

### Администратор системы

- Управление всеми пользователями
- Просмотр и управление всеми командами
- Доступ к панели администратора

## 🔐 Безопасность

- **Хеширование паролей**: Argon2 (основной) + Bcrypt (fallback)
- **JWT токены**: Access (30 мин) + Refresh (7 дней)
- **CORS**: Настраиваемые allowed origins
- **SQL Injection**: Защита через SQLAlchemy ORM
- **Валидация**: Pydantic schemas для всех входных данных

## 📄 Лицензия

MIT License

## 👨‍💻 Автор

Стас Басов
