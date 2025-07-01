from babel import Locale
from babel.support import Translations
import os
import gettext

_translations = {}
_current_locale = 'en'
SUPPORTED_LOCALES = ['en', 'pt']

def setup_i18n():
    global _translations
    localedir = os.path.join(os.path.dirname(__file__), '..', 'locales')
    
    for locale in SUPPORTED_LOCALES:
        try:
            _translations[locale] = gettext.translation(
                'messages',
                localedir=localedir,
                languages=[locale]
            )
        except FileNotFoundError:
            _translations[locale] = gettext.NullTranslations()

def set_locale(locale: str):
    global _current_locale
    if locale in SUPPORTED_LOCALES:
        _current_locale = locale

def gettext_func(message: str) -> str:
    return _translations.get(_current_locale, gettext.NullTranslations()).gettext(message)
