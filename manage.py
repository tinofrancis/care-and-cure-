#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carecure.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Monkeypatch for Python 3.14 compatibility issue in Django 4.2
    # Fixes AttributeError: 'super' object has no attribute 'dicts'
    import django.template.context

    def patched_context_copy(self):
        duplicate = self.__new__(self.__class__)
        duplicate.__dict__ = self.__dict__.copy()
        if hasattr(self, 'dicts'):
            duplicate.dicts = self.dicts[:]
        return duplicate

    django.template.context.Context.__copy__ = patched_context_copy

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
