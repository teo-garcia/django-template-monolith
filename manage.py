#!/usr/bin/env python
import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.config.settings")
    from django.core.management import execute_from_command_line

    from app.config.env import get_settings
    from app.shared.telemetry import configure_telemetry

    configure_telemetry(get_settings())
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
