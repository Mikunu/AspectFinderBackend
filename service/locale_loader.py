import json
from pathlib import Path
from typing import Dict, Optional
from utils.logger import Logger


class LocaleLoader:
    def __init__(self, locales_dir: str = 'resources/locales'):
        self.logger = Logger().logger

        self.locales = {}
        self.locale_info = {}
        self.locales_dir = Path(locales_dir)
        self.load_locales()

    def load_locales(self) -> None:
        """Loads all available locales into memory"""
        self.logger.info("Loading locales...")
        self.locales = {}  # Сброс предыдущих данных
        self.locale_info = {}  # Сброс кэша

        for path in self.locales_dir.glob('*.json'):
            try:
                locale_code = path.stem
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    self.locales[locale_code] = data

                    locale_name = data.get('locale', locale_code)
                    self.locale_info[locale_code] = locale_name

                    self.logger.info(f"Loaded locale {locale_code} ({locale_name}) with {len(data)} entries")
            except Exception as e:
                self.logger.error(f"Failed to load {path}: {str(e)}", exc_info=True)

    def get_locale(self, locale: str) -> Optional[Dict]:
        """Returns the specified locale"""
        return self.locales.get(locale)

    def get_available_locales(self) -> list:
        """Returns a list of available locales"""
        return [
            {
                "locale": code,
                "name": self.locale_info.get(code, code)
            }
            for code in self.locales.keys()
        ]
