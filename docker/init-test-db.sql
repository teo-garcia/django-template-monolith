SELECT 'CREATE DATABASE django_monolith_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'django_monolith_test')\gexec
