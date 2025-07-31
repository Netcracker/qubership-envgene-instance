# Conventional Commits

Этот проект использует [Conventional Commits](https://www.conventionalcommits.org/) для стандартизации сообщений коммитов.

## Установка

Pre-commit hooks уже настроены в проекте. Для установки:

```bash
# Установка pre-commit
pip3 install pre-commit

# Установка commitizen
pip3 install commitizen

# Установка hooks в репозиторий
pre-commit install --hook-type commit-msg
pre-commit install
```

## Формат сообщений коммитов

Сообщения коммитов должны следовать формату:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Типы коммитов

- **feat**: новая функциональность
- **fix**: исправление бага
- **docs**: изменения в документации
- **style**: изменения, не влияющие на смысл кода (пробелы, форматирование, отсутствующие точки с запятой и т.д.)
- **refactor**: рефакторинг кода
- **perf**: изменения, улучшающие производительность
- **test**: добавление или исправление тестов
- **chore**: изменения в процессе сборки или вспомогательных инструментах
- **ci**: изменения в CI/CD конфигурации
- **build**: изменения в системе сборки или внешних зависимостях

### Примеры

```bash
# Валидные коммиты
git commit -m "feat: add user authentication"
git commit -m "fix: resolve login issue"
git commit -m "docs: update README"
git commit -m "style: format code with black"
git commit -m "refactor: improve error handling"
git commit -m "test: add unit tests for auth"
git commit -m "chore: update dependencies"
git commit -m "perf: optimize database queries"
git commit -m "ci: update GitHub Actions"
git commit -m "build: update build configuration"

# С областью (scope)
git commit -m "feat(auth): add OAuth2 support"
git commit -m "fix(api): resolve rate limiting issue"

# С телом сообщения
git commit -m "feat: add user authentication

This commit adds JWT-based authentication system
with refresh token support."

# С footer
git commit -m "fix: resolve login issue

Closes #123"
```

### Невалидные коммиты

Следующие коммиты будут отклонены:

```bash
git commit -m "test commit"
git commit -m "update code"
git commit -m "fix bug"
git commit -m "add feature"
```

## Pre-commit Hooks

Проект настроен с следующими pre-commit hooks:

- **trailing-whitespace**: удаляет лишние пробелы в конце строк
- **end-of-file-fixer**: добавляет перевод строки в конец файлов
- **check-yaml**: проверяет синтаксис YAML файлов
- **check-json**: проверяет синтаксис JSON файлов
- **black**: форматирует Python код
- **isort**: сортирует импорты Python
- **commitizen**: проверяет формат сообщений коммитов

## Использование commitizen

Для создания коммита с интерактивным интерфейсом:

```bash
cz commit
```

Для проверки сообщения коммита:

```bash
echo "feat: add new feature" | cz check
```

## Настройка

Конфигурация находится в файлах:
- `.pre-commit-config.yaml` - настройки pre-commit hooks
- `pyproject.toml` - настройки commitizen

## Troubleshooting

Если коммит отклоняется, проверьте:
1. Соответствует ли сообщение формату conventional commits
2. Нет ли ошибок в коде (flake8, black, isort)
3. Правильно ли настроены hooks

Для пропуска проверок (не рекомендуется):
```bash
git commit -m "feat: add feature" --no-verify
```
