# Исправление проблемы с CRED_ROTATION_PAYLOAD

## Проблема

Ошибка при парсинге JSON в `creds_rotation_handler.py`:

```
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
```

## Причина

Проблема возникала из-за неправильного формата `CRED_ROTATION_PAYLOAD` в файле `.github/pipeline_vars.yaml`.

### Неправильный формат (до исправления):
```yaml
CRED_ROTATION_PAYLOAD: |
  {"rotation_items":[...]}
```

### Правильный формат (после исправления):
```yaml
CRED_ROTATION_PAYLOAD: '{"rotation_items":[{"namespace":"e02-bss","application":"postgres","context":"deployment","parameter_key":"POSTGRES_DBA_USER","parameter_value":"new_postgres_user"}]}'
```

## Объяснение

1. **YAML Block Scalar (|)** - YAML интерпретировал JSON как многострочную строку, что приводило к проблемам при передаче в Python
2. **Потеря кавычек** - В процессе обработки JSON терял кавычки вокруг ключей
3. **Переменные окружения** - При передаче через GitHub Actions формат мог искажаться

## Решение

Изменили формат на простую строку в одинарных кавычках и оптимизировали JSON форматирование:

```yaml
# Было (неправильно):
CRED_ROTATION_PAYLOAD: |
  {"rotation_items":[{"namespace":"e02-bss",...}]}

# Стало (правильно):
CRED_ROTATION_PAYLOAD: '{"rotation_items":[{"namespace":"e02-bss","application":"postgres","context":"deployment","parameter_key":"POSTGRES_DBA_USER","parameter_value":"new_postgres_user"}]}'
```

## Проверка

Формат протестирован и работает корректно:
- ✅ YAML парсинг
- ✅ JSON валидация в `load_env_variables.py`
- ✅ JSON парсинг в `creds_rotation_handler.py`

## Альтернативные форматы

Если возникнут проблемы, можно использовать:

```yaml
# Вариант 1: Двойные кавычки с экранированием
CRED_ROTATION_PAYLOAD: "{\"rotation_items\":[...]}"

# Вариант 2: YAML block scalar с правильным отступом
CRED_ROTATION_PAYLOAD: |
  {
    "rotation_items": [...]
  }

# Вариант 3: Простая строка в одинарных кавычках (рекомендуемый)
CRED_ROTATION_PAYLOAD: '{"rotation_items":[...]}'
```

## Рекомендации

1. **Используйте простую строку в одинарных кавычках** для JSON данных
2. **Избегайте YAML block scalar** для JSON - они могут терять кавычки
3. **Оптимизируйте JSON форматирование** в `load_env_variables.py`
4. **Тестируйте формат** перед использованием в production
