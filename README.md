# 🤖 Telega IQ Detector Bot

Телеграм бот, который проверяет использует ли пользователь **Telega от VK**.

## Установка

```bash
pip install python-telegram-bot requests
```

## Запуск


Замени `YOUR_BOT_TOKEN_HERE` на твой токен в этой строке: `BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"`).

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
python telega_bot.py
```
