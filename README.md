# 🤖 Telega IQ Detector Bot

Телеграм бот, который проверяет использует ли пользователь **Telega от VK**.

## Установка

```bash
pip install python-telegram-bot requests
```

## Запуск

```bash
BOT_TOKEN="твой_токен_от_botfather" python telega_bot.py
```

Или вписать токен прямо в код (строка `BOT_TOKEN = ...`).

## Как получить токен

1. Открой @BotFather в Telegram
2. Напиши `/newbot`
3. Следуй инструкциям, получи токен вида `1234567890:ABCdef...`

## Использование бота

- Отправь числовой ID: `123456789`
- Или перешли сообщение от нужного пользователя
- Узнать ID можно через @userinfobot

## Результаты

| Статус | Ответ |
|--------|-------|
| Использует Telega | 🤡 IQ < 30 |
| Не использует | ✅ IQ > 30 |
| Ошибка API | ⚠️ Попробуй позже |

## Деплой (24/7)

### Railway / Render / VPS

```bash
# .env файл
BOT_TOKEN=твой_токен
```

```bash
python telega_bot.py
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY telega_bot.py .
RUN pip install python-telegram-bot requests
CMD ["python", "telega_bot.py"]
```
