"""Handlers for /start command and callback queries."""

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from app.database.database import Database
from app.handlers.start_ui import (
    KeyboardFactory,
    back_keyboard,
    commands_keyboard,
    get_text,
    language_settings_keyboard,
    main_keyboard,
)

router = Router()
database = Database()


def _get_language(user_id: int) -> str:
    """Get correct user language."""
    language = database.users.find(user_id)
    return language if language in {'ru', 'en'} else 'ru'


async def _show_page(
    callback: CallbackQuery,
    text_key: str,
    keyboard_factory: KeyboardFactory,
) -> None:
    """Show menu page."""
    if callback.from_user is None or not isinstance(callback.message, Message):
        return

    language = _get_language(callback.from_user.id)
    text = get_text(language, text_key)
    keyboard = keyboard_factory(language)
    await callback.message.edit_text(
        text,
        parse_mode='HTML',
        reply_markup=keyboard,
    )
    await callback.answer()


@router.message(CommandStart())
async def start(message: Message) -> None:
    """Handle /start command."""
    if message.from_user is None:
        return

    language = _get_language(message.from_user.id)
    await message.answer(
        get_text(language, 'welcome'),
        parse_mode='HTML',
        reply_markup=main_keyboard(language),
    )


@router.callback_query(
    lambda callback_data: callback_data.data in {'lang_ru', 'lang_en'},
)
async def language_selected(callback: CallbackQuery) -> None:
    """Handle language selection."""
    if callback.from_user is None or not isinstance(callback.message, Message):
        return

    language = 'ru' if callback.data == 'lang_ru' else 'en'
    database.users.save(callback.from_user.id, language)
    text = get_text(language, 'language_changed')
    keyboard = main_keyboard(language)

    try:
        await callback.message.edit_text(
            text,
            parse_mode='HTML',
            reply_markup=keyboard,
        )
    except TelegramBadRequest:
        await callback.message.answer(
            text,
            parse_mode='HTML',
            reply_markup=keyboard,
        )

    await callback.answer()


@router.callback_query(
    lambda callback_data: callback_data.data in {
        'settings_language',
        'commands',
        'command_mute',
        'command_mutestatus',
        'command_antispam',
        'back_start',
    },
)
async def menu_page(callback: CallbackQuery) -> None:
    """Show selected menu page."""
    pages = {
        'settings_language': ('settings_title', language_settings_keyboard),
        'commands': ('commands_title', commands_keyboard),
        'command_mute': ('mute_desc', back_keyboard),
        'command_mutestatus': ('mutestatus_desc', back_keyboard),
        'command_antispam': ('antispam_desc', back_keyboard),
        'back_start': ('welcome', main_keyboard),
    }
    page = pages.get(callback.data or '')
    if page is None:
        await callback.answer()
        return

    text_key, keyboard_factory = page
    await _show_page(callback, text_key, keyboard_factory)
