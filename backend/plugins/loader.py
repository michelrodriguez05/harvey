import importlib
import pkgutil
from pathlib import Path

from backend.core.config import settings
from backend.tools.registry import registry


def load_plugins() -> list[str]:
    """Discover and load plugins from backend/plugins/. Each plugin module must expose register(registry)."""
    loaded: list[str] = []
    plugins_path = Path(settings.plugins_dir)
    if not plugins_path.exists():
        return loaded

    for module_info in pkgutil.iter_modules([str(plugins_path)]):
        if module_info.name.startswith("_"):
            continue
        module = importlib.import_module(f"backend.plugins.{module_info.name}")
        register = getattr(module, "register", None)
        if callable(register):
            register(registry)
            loaded.append(module_info.name)
    return loaded
