# 🚔 Быстрый старт TheComradeMajor Bot

## 1. Установка зависимостей

```bash
poetry install
```

## 2. Настройка переменных окружения

Скопируйте шаблон и заполните реальными данными:

```bash
cp .env.example .env
```

Отредактируйте файл `.env`:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# GigaChat API Configuration  
GIGACHAT_CLIENT_ID=your_gigachat_client_id
GIGACHAT_CLIENT_SECRET=your_gigachat_client_secret
GIGACHAT_SCOPE=GIGACHAT_API_PERS

# Bot Configuration
BOT_USERNAME=thecomrademajor_bot
LOG_LEVEL=INFO
```

## 3. Получение токенов

### Telegram Bot:
1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Создайте нового бота: `/newbot`
3. Получите токен
4. Настройте для работы в группах: `/setprivacy` → Disable

### GigaChat API:
1. Зарегистрируйтесь на [developers.sber.ru](https://developers.sber.ru/docs/ru/gigachat/api/main)
2. Создайте приложение
3. Получите Client ID и Client Secret

## 4. Запуск

```bash
# Если у вас установлен Task
task run

# Или напрямую через Poetry
poetry run python -m src.main
```

## 5. Использование

1. Добавьте бота в групповой чат
2. Ответьте на любое сообщение
3. В ответе упомяните: `@thecomrademajor_bot`
4. Бот проанализирует исходное сообщение и выдаст "обвинение"

**Готово! Бот запущен и готов к работе!** 🚔
