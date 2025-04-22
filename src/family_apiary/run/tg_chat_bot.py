import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from family_apiary.products.infrastructure.tg_chat_bot import TgChatBotSettings

settings = TgChatBotSettings()

dp = Dispatcher()


# Command handler
@dp.message(Command('start'))
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Hello! I'm a bot created with aiogram.\nChat id: {message.chat.id}"
    )


# Run the bot
async def main() -> None:
    bot = Bot(token=settings.TOKEN)
    await bot.delete_webhook()

    print('Starting tg chat bot...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
