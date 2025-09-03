# Использование переменных из pipeline_vars.yaml

## Как это работает

1. **Загрузка переменных**: Скрипт `load_pipeline_vars.py` читает переменные из `.github/pipeline_vars.yaml`
2. **Валидация**: Все переменные проверяются на соответствие типу string
3. **Запись в github_output**: Переменные записываются в `github_output` для использования в других джобах
4. **Загрузка в environment**: Переменные загружаются в environment variables текущего джоба

## Структура файла pipeline_vars.yaml

```yaml
---
# Все переменные должны быть строками (в кавычках)
ENV_INVENTORY_INIT: "false"
GENERATE_EFFECTIVE_SET: "false"
ENV_TEMPLATE_TEST: "false"
ENV_TEMPLATE_NAME: ""
SD_DATA: "{}"
SD_VERSION: ""
SD_SOURCE_TYPE: ""
SD_DELTA: "false"
ENV_SPECIFIC_PARAMETERS: "{}"
CRED_ROTATION_PAYLOAD: '{"rotation_items":[]}'
CRED_ROTATION_FORCE: "true"
```

## Использование в других джобах

### 1. Через environment variables (автоматически)

Переменные автоматически доступны в environment variables джоба `show_environment_variables`:

```yaml
- name: Use pipeline variables
  run: |
    echo "ENV_INVENTORY_INIT: $ENV_INVENTORY_INIT"
    echo "GENERATE_EFFECTIVE_SET: $GENERATE_EFFECTIVE_SET"
    
    if [ "$ENV_INVENTORY_INIT" = "true" ]; then
      echo "Initializing inventory..."
    fi
```

### 2. Через outputs джоба

Переменные доступны как outputs джоба `show_environment_variables`:

```yaml
some_other_job:
  needs: show_environment_variables
  runs-on: ubuntu-22.04
  steps:
    - name: Use variables from previous job
      run: |
        echo "ENV_INVENTORY_INIT: ${{ needs.show_environment_variables.outputs.ENV_INVENTORY_INIT }}"
        echo "GENERATE_EFFECTIVE_SET: ${{ needs.show_environment_variables.outputs.GENERATE_EFFECTIVE_SET }}"
```

### 3. В условиях джобов

```yaml
some_conditional_job:
  needs: show_environment_variables
  if: needs.show_environment_variables.outputs.ENV_INVENTORY_INIT == 'true'
  runs-on: ubuntu-22.04
  steps:
    - name: This job runs only if ENV_INVENTORY_INIT is true
      run: echo "Inventory initialization enabled"
```

## Доступные переменные

Все переменные из `pipeline_vars.yaml` автоматически доступны:

- `ENV_INVENTORY_INIT`
- `GENERATE_EFFECTIVE_SET`
- `ENV_TEMPLATE_TEST`
- `ENV_TEMPLATE_NAME`
- `SD_DATA`
- `SD_VERSION`
- `SD_SOURCE_TYPE`
- `SD_DELTA`
- `ENV_SPECIFIC_PARAMETERS`
- `CRED_ROTATION_PAYLOAD`
- `CRED_ROTATION_FORCE`

## Валидация

Скрипт автоматически проверяет, что все переменные являются строками:

```yaml
# ❌ Неправильно (вызовет ошибку):
ENV_INVENTORY_INIT: false
SD_DATA: {}

# ✅ Правильно:
ENV_INVENTORY_INIT: "false"
SD_DATA: "{}"
```

## Примеры использования

### Проверка условий

```bash
if [ "$ENV_INVENTORY_INIT" = "true" ]; then
  echo "Initializing inventory..."
fi

if [ "$GENERATE_EFFECTIVE_SET" = "true" ]; then
  echo "Generating effective set..."
fi
```

### Использование JSON переменных

```bash
# SD_DATA и ENV_SPECIFIC_PARAMETERS содержат JSON
echo "SD_DATA: $SD_DATA"
echo "ENV_SPECIFIC_PARAMETERS: $ENV_SPECIFIC_PARAMETERS"

# Можно парсить JSON в скриптах
sd_data=$(echo "$SD_DATA" | jq '.')
```

### Условное выполнение джобов

```yaml
inventory_job:
  needs: show_environment_variables
  if: needs.show_environment_variables.outputs.ENV_INVENTORY_INIT == 'true'
  runs-on: ubuntu-22.04
  steps:
    - name: Initialize inventory
      run: echo "Initializing inventory..."

effective_set_job:
  needs: show_environment_variables
  if: needs.show_environment_variables.outputs.GENERATE_EFFECTIVE_SET == 'true'
  runs-on: ubuntu-22.04
  steps:
    - name: Generate effective set
      run: echo "Generating effective set..."
```
