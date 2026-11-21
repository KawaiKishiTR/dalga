from functools import lru_cache
import yaml

from app.common.file_paths import CONFIG_DIR

class ConfigModelMixin:
    @classmethod
    def _get_config_file(cls):
        return (CONFIG_DIR / cls.__name__.lower()).with_suffix(".yml")

    @classmethod
    @lru_cache(maxsize=1)
    def get_config(cls):
        user_data = {}
        if cls._get_config_file().exists():
            with cls._get_config_file().open("r", encoding="utf-8") as f:
                user_data = yaml.safe_load(f) or {}
        return cls.model_validate(user_data)

    def set_config(self) -> None:
        with self._get_config_file().open("w", encoding="utf-8") as f:
            yaml.safe_dump(self.model_dump(), f, sort_keys=False, allow_unicode=True)
        type(self).get_config.cache_clear()


