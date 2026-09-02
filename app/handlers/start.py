from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, CopyTextButton, Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.database import Database

router = Router()
database = Database()


def language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Русский", callback_data="lang_ru")
    builder.button(text="English", callback_data="lang_en")
    builder.adjust(2)
    return builder.as_markup()


def main_keyboard(language: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if language == "en":
        builder.button(text="Copy", copy_text=CopyTextButton(text="@ChatAdminModbot"))
        builder.button(text="Connect", url="tg://settings/edit")
        builder.button(text="Commands", callback_data="commands")
        builder.button(text="Language", callback_data="settings_language")
    else:
        builder.button(text="Скопировать", copy_text=CopyTextButton(text="@ChatAdminModbot"))
        builder.button(text="Подключить", url="tg://settings/edit")
        builder.button(text="Команды", callback_data="commands")
        builder.button(text="Язык", callback_data="settings_language")
    builder.adjust(2, 2)
    return builder.as_markup()


def commands_keyboard(language: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if language == "en":
        builder.button(text=".mute", callback_data="command_mute")
        builder.button(text=".mutestatus", callback_data="command_mutestatus")
        builder.button(text=".antispam", callback_data="command_antispam")
        builder.button(text="Back", callback_data="back_start")
    else:
        builder.button(text=".mute", callback_data="command_mute")
        builder.button(text=".mutestatus", callback_data="command_mutestatus")
        builder.button(text=".antispam", callback_data="command_antispam")
        builder.button(text="Назад", callback_data="back_start")
    builder.adjust(3, 1)
    return builder.as_markup()


def back_keyboard(language: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Back" if language == "en" else "Назад", callback_data="commands")
    return builder.as_markup()


def language_settings_keyboard(language: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Русский", callback_data="lang_ru")
    builder.button(text="English", callback_data="lang_en")
    builder.button(text="Back" if language == "en" else "Назад", callback_data="back_start")
    builder.adjust(2, 1)
    return builder.as_markup()


async def send_start(message: Message, language: str) -> None:
    if language == "en":
        text = (
            "<b>ChatAdminMod</b>\n\n"
            "Useful commands directly in chats with your contacts.\n\n"
            "<b>Connect the bot to your account:</b>\n\n"
            "<blockquote>"
            "<b>1.</b> Tap «Copy»\n"
            "<b>2.</b> Add the bot to «Chat Automation»\n"
            "<b>3.</b> Tap «Connect»\n"
            "<b>4.</b> Open «Chat Automation»\n"
            "<b>5.</b> Paste the copied username — <code>@ChatAdminModbot</code>"
            "</blockquote>\n\n"
            "If «Chat Automation» is missing, update Telegram to the latest version."
        )
    else:
        text = (
            "<b>ChatAdminMod</b>\n\n"
            "Полезные команды прямо в чатах с собеседниками.\n\n"
            "<b>Подключи бота к своему аккаунту:</b>\n\n"
            "<blockquote>"
            "<b>1.</b> Нажми «Скопировать»\n"
            "<b>2.</b> Добавь бота в «Автоматизацию чатов»\n"
            "<b>3.</b> Нажми «Подключить»\n"
            "<b>4.</b> Открой «Автоматизацию чатов»\n"
            "<b>5.</b> Вставь скопированное имя — <code>@ChatAdminModbot</code>"
            "</blockquote>\n\n"
            "Если раздел «Автоматизация чатов» отсутствует, обнови Telegram до последней версии."
        )
    await message.answer(text, parse_mode="HTML", reply_markup=main_keyboard(language))


@router.message(CommandStart())
async def start(message: Message) -> None:
    if message.from_user is None:
        return
    user_id = message.from_user.id
    language = database.get_language(user_id)
    if language not in ("ru", "en"):
        language = "ru"
    await send_start(message, language)


@router.callback_query(lambda callback: callback.data in {"lang_ru", "lang_en"})
async def language_selected(callback: CallbackQuery) -> None:
    if callback.from_user is None or not isinstance(callback.message, Message):
        await callback.answer()
        return
    language = "ru" if callback.data == "lang_ru" else "en"
    database.set_language(callback.from_user.id, language)
    text = "<b>Язык изменён.</b>" if language == "ru" else "<b>Language changed.</b>"
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=main_keyboard(language))
    except TelegramBadRequest:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=main_keyboard(language))
    await callback.answer()


@router.callback_query(lambda callback: callback.data == "settings_language")
async def settings_language(callback: CallbackQuery) -> None:
    if callback.from_user is None or not isinstance(callback.message, Message):
        await callback.answer()
        return
    language = database.get_language(callback.from_user.id)
    if language not in ("ru", "en"):
        language = "ru"
    if language == "en":
        text = "<b>Language</b>\n\nChoose the interface language."
    else:
        text = "<b>Язык</b>\n\nВыбери язык интерфейса ChatAdminMod."
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=language_settings_keyboard(language))
    await callback.answer()


@router.callback_query(lambda callback: callback.data == "commands")
async def commands(callback: CallbackQuery) -> None:
    if callback.from_user is None or not isinstance(callback.message, Message):
        await callback.answer()
        return
    language = database.get_language(callback.from_user.id)
    if language not in ("ru", "en"):
        language = "ru"
    if language == "en":
        text = (
            "<b>Commands</b>\n\n"
            "Commands available in chats with your contacts.\n\n"
            "Select a command to view its description."
        )
    else:
        text = (
            "<b>Команды</b>\n\n"
            "Команды, доступные в чатах с собеседниками.\n\n"
            "Выбери команду, чтобы посмотреть её описание."
        )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=commands_keyboard(language))
    await callback.answer()


@router.callback_query(lambda callback: callback.data == "command_mute")
async def command_mute(callback: CallbackQuery) -> None:
    if callback.from_user is None or not isinstance(callback.message, Message):
        await callback.answer()
        return
    language = database.get_language(callback.from_user.id)
    if language not in ("ru", "en"):
        language = "ru"
    if language == "en":
        text = (
            "<b>.mute</b>\n\n"
            "Temporarily or permanently mutes a contact.\n\n"
            "<b>Usage:</b>\n\n"
            "<code>.mute</code> — forever\n"
            "<code>.mute 30s</code> — 30 seconds\n"
            "<code>.mute 5m</code> — 5 minutes\n"
            "<code>.mute 2h</code> — 2 hours\n\n"
            "<code>.unmute</code> — remove the mute.\n\n"
            "New messages from the muted contact will be automatically deleted."
        )
    else:
        text = (
            "<b>.mute</b>\n\n"
            "Позволяет временно или навсегда замьютить собеседника.\n\n"
            "<b>Использование:</b>\n\n"
            "<code>.mute</code> — навсегда\n"
            "<code>.mute 30s</code> — 30 секунд\n"
            "<code>.mute 5m</code> — 5 минут\n"
            "<code>.mute 2h</code> — 2 часа\n\n"
            "<code>.unmute</code> — снять мут досрочно.\n\n"
            "Новые сообщения собеседника будут автоматически удаляться."
        )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=back_keyboard(language))
    await callback.answer()


@router.callback_query(lambda callback: callback.data == "command_mutestatus")
async def command_mutestatus(callback: CallbackQuery) -> None:
    if callback.from_user is None or not isinstance(callback.message, Message):
        await callback.answer()
        return
    language = database.get_language(callback.from_user.id)
    if language not in ("ru", "en"):
        language = "ru"
    if language == "en":
        text = (
            "<b>.mutestatus</b>\n\n"
            "Shows the current mute status of the chat.\n\n"
            "<b>Usage:</b>\n\n"
            "<code>.mutestatus</code> — check the current mute status."
        )
    else:
        text = (
            "<b>.mutestatus</b>\n\n"
            "Показывает текущий статус мута собеседника.\n\n"
            "<b>Использование:</b>\n\n"
            "<code>.mutestatus</code> — проверить текущий статус."
        )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=back_keyboard(language))
    await callback.answer()


@router.callback_query(lambda callback: callback.data == "command_antispam")
async def command_antispam(callback: CallbackQuery) -> None:
    if callback.from_user is None or not isinstance(callback.message, Message):
        await callback.answer()
        return
    language = database.get_language(callback.from_user.id)
    if language not in ("ru", "en"):
        language = "ru"
    if language == "en":
        text = (
            "<b>.antispam</b>\n\n"
            "Automatically detects rapid message flooding from a contact.\n\n"
            "<b>Current settings:</b>\n\n"
            "10 messages within 5 seconds.\n"
            "The contact is muted for 30 seconds.\n\n"
            "<b>Usage:</b>\n\n"
            "<code>.antispam</code> — enable or disable anti-spam."
        )
    else:
        text = (
            "<b>.antispam</b>\n\n"
            "Автоматически обнаруживает слишком быструю отправку сообщений собеседником.\n\n"
            "<b>Текущие настройки:</b>\n\n"
            "10 сообщений за 5 секунд.\n"
            "Собеседник получает мут на 30 секунд.\n\n"
            "<b>Использование:</b>\n\n"
            "<code>.antispam</code> — включить или выключить антиспам."
        )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=back_keyboard(language))
    await callback.answer()


@router.callback_query(lambda callback: callback.data == "back_start")
async def back_start(callback: CallbackQuery) -> None:
    if callback.from_user is None or not isinstance(callback.message, Message):
        await callback.answer()
        return
    language = database.get_language(callback.from_user.id)
    if language not in ("ru", "en"):
        language = "ru"
    if language == "en":
        text = (
            "<b>ChatAdminMod</b>\n\n"
            "Useful commands directly in chats with your contacts.\n\n"
            "<b>Connect the bot to your account:</b>\n\n"
            "<blockquote>"
            "<b>1.</b> Tap «Copy»\n"
            "<b>2.</b> Add the bot to «Chat Automation»\n"
            "<b>3.</b> Tap «Connect»\n"
            "<b>4.</b> Open «Chat Automation»\n"
            "<b>5.</b> Paste the copied username — <code>@ChatAdminModbot</code>"
            "</blockquote>\n\n"
            "If «Chat Automation» is missing, update Telegram to the latest version."
        )
    else:
        text = (
            "<b>ChatAdminMod</b>\n\n"
            "Полезные команды прямо в чатах с собеседниками.\n\n"
            "<b>Подключи бота к своему аккаунту:</b>\n\n"
            "<blockquote>"
            "<b>1.</b> Нажми «Скопировать»\n"
            "<b>2.</b> Добавь бота в «Автоматизацию чатов»\n"
            "<b>3.</b> Нажми «Подключить»\n"
            "<b>4.</b> Открой «Автоматизацию чатов»\n"
            "<b>5.</b> Вставь скопированное имя — <code>@ChatAdminModbot</code>"
            "</blockquote>\n\n"
            "Если раздел «Автоматизация чатов» отсутствует, обнови Telegram до последней версии."
        )
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=main_keyboard(language))
    except TelegramBadRequest:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=main_keyboard(language))
    await callback.answer()