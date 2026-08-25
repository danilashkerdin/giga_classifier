"""Конфигурация логирования"""

import logging
import sys
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: str = "logs/classifier.log"):
    """Настройка логирования в консоль и файл."""
    log_path = Path(log_file)
    log_path.parent.mkdir(exist_ok=True)

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    level = getattr(logging, log_level.upper())

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(console)

    file = logging.FileHandler(log_file, encoding="utf-8")
    file.setLevel(logging.DEBUG)
    file.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(file)

    root_logger.info("=" * 60)
    root_logger.info("Логирование настроено")
    root_logger.info(f"Уровень: {log_level}, файл: {log_file}")
    root_logger.info("=" * 60)