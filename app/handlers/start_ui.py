"""Start menu texts and keyboards."""

from types import MappingProxyType
from typing import Callable, Final, Mapping

from aiogram.types import CopyTextButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

KeyboardFactory = Callable[[str], InlineKeyboardMarkup]
TextMap = Mapping[str, Mapping[str, str]]

TEXTS: Final[TextMap] = MappingProxyType({
    'en': MappingProxyType({
        'welcome': ''.join((
            '<b>ChatAdminMod</b>\n\n',
            'Useful commands directly in chats with your contacts.\n\n',
            '<b>Connect the bot to your account:</b>\n\n',
            '<blockquote><b>1.</b> Tap «Copy»\n',
            '<b>2.</b> Add the bot to «Chat Automation»\n',
            '<b>3.</b> Tap «Connect»\n',
            '<b>4.</b> Open «Chat Automation»\n',
            '<b>5.</b> Paste the copied username — ',
            '<code>@ChatAdminModbot</code></blockquote>\n\n',
            'If «Chat Automation» is missing, update Telegram to the latest version.',
        )),
        'back': 'Back',
        'language_changed': '<b>Language changed.</b>',
        'settings_title': ''.join((
            '<b>Language</b>\n\n',
            'Choose the interface language.',
        )),
        'commands_title': ''.join((
            '<b>Commands</b>\n\n',
            'Commands available in chats with your contacts.\n\n',
            'Select a command to view its description.',
        )),
        'mute_desc': ''.join((
            '<b>.mute</b>\n\n',
            'Temporarily or permanently mutes a contact.\n\n',
            '<b>Usage:</b>\n\n',
            '<code>.mute</code> — forever\n',
            '<code>.mute 30s</code> — 30 seconds\n',
            '<code>.mute 5m</code> — 5 minutes\n',
            '<code>.mute 2h</code> — 2 hours\n\n',
            '<code>.unmute</code> — remove the mute.\n\n',
            'New messages from the muted contact will be automatically deleted.',
        )),
        'mutestatus_desc': ''.join((
            '<b>.mutestatus</b>\n\n',
            'Shows the current mute status of the chat.\n\n',
            '<b>Usage:</b>\n\n',
            '<code>.mutestatus</code> — check the current mute status.',
        )),
        'antispam_desc': ''.join((
            '<b>.antispam</b>\n\n',
            'Automatically detects rapid message flooding from a contact.\n\n',
            '<b>Current settings:</b>\n\n',
            '10 messages within 5 seconds.\n',
            'The contact is muted for 30 seconds.\n\n',
            '<b>Usage:</b>\n\n',
            '<code>.antispam</code> — enable or disable anti-spam.',
        )),
    }),
    'ru': MappingProxyType({
        'welcome': ''.join((
            '<b>ChatAdminMod</b>\n\n',
            'Полезные команды прямо в чатах с собеседниками.\n\n',
            '<b>Подключи бота к своему аккаунту:</b>\n\n',
            '<blockquote><b>1.</b> Нажми «Скопировать»\n',
            '<b>2.</b> Добавь бота в «Автоматизацию чатов»\n',
            '<b>3.</b> Нажми «Подключить»\n',
            '<b>4.</b> Открой «Автоматизацию чатов»\n',
            '<b>5.</b> Вставь скопированное имя — ',
            '<code>@ChatAdminModbot</code></blockquote>\n\n',
            'Если раздел «Автоматизация чатов» отсутствует, ',
            'обнови Telegram до последней версии.',
        )),
        'back': 'Назад',
        'language_changed': '<b>Язык изменён.</b>',
        'settings_title': ''.join((
            '<b>Язык</b>\n\n',
            'Выбери язык интерфейса ChatAdminMod.',
        )),
        'commands_title': ''.join((
            '<b>Команды</b>\n\n',
            'Команды, доступные в чатах с собеседниками.\n\n',
            'Выбери команду, чтобы посмотреть её описание.',
        )),
        'mute_desc': ''.join((
            '<b>.mute</b>\n\n',
            'Позволяет временно или навсегда замьютить собеседника.\n\n',
            '<b>Использование:</b>\n\n',
            '<code>.mute</code> — навсегда\n',
            '<code>.mute 30s</code> — 30 секунд\n',
            '<code>.mute 5m</code> — 5 минут\n',
            '<code>.mute 2h</code> — 2 часа\n\n',
            '<code>.unmute</code> — снять мут досрочно.\n\n',
            'Новые сообщения собеседника будут автоматически удаляться.',
        )),
        'mutestatus_desc': ''.join((
            '<b>.mutestatus</b>\n\n',
            'Показывает текущий статус мута собеседника.\n\n',
            '<b>Использование:</b>\n\n',
            '<code>.mutestatus</code> — проверить текущий статус.',
        )),
        'antispam_desc': ''.join((
            '<b>.antispam</b>\n\n',
            'Автоматически обнаруживает слишком быструю отправку ',
            'сообщений собеседником.\n\n',
            '<b>Текущие настройки:</b>\n\n',
            '10 сообщений за 5 секунд.\n',
            'Собеседник получает мут на 30 секунд.\n\n',
            '<b>Использование:</b>\n\n',
            '<code>.antispam</code> — включить или выключить антиспам.',
        )),
    }),
})


def get_text(language: str, key: str) -> str:
    """Get localized text."""
    lang = 'en' if language == 'en' else 'ru'
    return TEXTS[lang].get(key, '')


def language_keyboard() -> InlineKeyboardMarkup:
    """Build language selection keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text='Русский', callback_data='lang_ru')
    builder.button(text='English', callback_data='lang_en')
    builder.adjust(2)
    return InlineKeyboardMarkup(inline_keyboard=builder.export())


def main_keyboard(language: str) -> InlineKeyboardMarkup:
    """Build main menu keyboard."""
    builder = InlineKeyboardBuilder()
    labels = (
        ('Copy', 'Connect', 'Commands', 'Language')
        if language == 'en'
        else ('Скопировать', 'Подключить', 'Команды', 'Язык')
    )
    builder.button(
        text=labels[0],
        copy_text=CopyTextButton(text='@ChatAdminModbot'),
    )
    builder.button(text=labels[1], url='tg://settings/edit')
    builder.button(text=labels[2], callback_data='commands')
    builder.button(text=labels[3], callback_data='settings_language')
    builder.adjust(2, 2)
    return InlineKeyboardMarkup(inline_keyboard=builder.export())


def commands_keyboard(language: str) -> InlineKeyboardMarkup:
    """Build commands list keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text='.mute', callback_data='command_mute')
    builder.button(text='.mutestatus', callback_data='command_mutestatus')
    builder.button(text='.antispam', callback_data='command_antispam')
    builder.button(
        text='Back' if language == 'en' else 'Назад',
        callback_data='back_start',
    )
    builder.adjust(3, 1)
    return InlineKeyboardMarkup(inline_keyboard=builder.export())


def back_keyboard(language: str) -> InlineKeyboardMarkup:
    """Build back keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Back' if language == 'en' else 'Назад',
        callback_data='commands',
    )
    return InlineKeyboardMarkup(inline_keyboard=builder.export())


def language_settings_keyboard(language: str) -> InlineKeyboardMarkup:
    """Build language settings keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text='Русский', callback_data='lang_ru')
    builder.button(text='English', callback_data='lang_en')
    builder.button(
        text='Back' if language == 'en' else 'Назад',
        callback_data='back_start',
    )
    builder.adjust(2, 1)
    return InlineKeyboardMarkup(inline_keyboard=builder.export())
