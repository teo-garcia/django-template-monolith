from app.config.settings import _database_from_url


def test_database_from_url_decodes_credentials_and_options() -> None:
    database_url = "postgresql://user:p%40ss%2Fword@db.example.com:5433/app_db?sslmode=require"
    expected_password = "p@ss/word"  # noqa: S105
    config = _database_from_url(database_url)

    assert config["ENGINE"] == "django.db.backends.postgresql"
    assert config["NAME"] == "app_db"
    assert config["USER"] == "user"
    assert config["PASSWORD"] == expected_password
    assert config["HOST"] == "db.example.com"
    assert config["PORT"] == "5433"
    assert config["OPTIONS"] == {"sslmode": "require"}
