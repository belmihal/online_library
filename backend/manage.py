#!/usr/bin/env python
"""Точка входа для управления Django-проектом «Онлайн-библиотека книг»."""
import os
import sys


def main():
    """Запуск административных команд Django."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_project.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Не удалось импортировать Django. Убедитесь, что пакеты из requirements.txt установлены."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
