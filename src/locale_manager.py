import yaml
from pathlib import Path

class LocaleManager:
    def __init__(self, language_code):
        self.code = language_code
        self.data = self._load_locale()

    def _load_locale(self):

        file_path = Path(f"src/locales/{self.code}.yaml")

        if not file_path.exists():
            file_path = Path("src/locales/en.yaml")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}

    def get(self, key_path):
        # Allows nested lookups like "ui.welcome"
        keys = key_path.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, f"[{key_path}]")
            else:
                return f"[{key_path}]"
        return str(value)
