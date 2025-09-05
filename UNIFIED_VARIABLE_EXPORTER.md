# Unified Variable Exporter Documentation

## Обзор

`unified_variable_exporter.py` - это единый Python скрипт для экспорта всех переменных окружения, необходимых для шагов pipeline:

- **Generate inventory**
- **Credential Rotation**  
- **Build Env**
- **Generate Effective Set**
- **Git Commit**

## Источники переменных

Скрипт обрабатывает переменные из следующих источников (в порядке приоритета):

1. **Переменные окружения** (наивысший приоритет)
2. **API input** (`GITHUB_PIPELINE_API_INPUT`)
3. **GitHub workflow inputs**
4. **pipeline_vars.yaml** (по умолчанию)

## Использование

### Базовое использование

```bash
# Экспорт всех переменных для конкретного шага
python .github/scripts/unified_variable_exporter.py --step generate_inventory --matrix-env test-cluster/e01

# Экспорт с дополнительными переменными из JSON
python .github/scripts/unified_variable_exporter.py --step env_build --matrix-env test-cluster/e01 --variables-json '{"MY_VAR": "my_value"}'

# Генерация shell скрипта с экспортами
python .github/scripts/unified_variable_exporter.py --step git_commit --matrix-env test-cluster/e01 --generate-script export_vars.sh

# Показать все экспортированные переменные
python .github/scripts/unified_variable_exporter.py --step credential_rotation --matrix-env test-cluster/e01 --list-vars
```

### Интеграция в pipeline

**ВАЖНО**: Переменные должны экспортироваться в том же шаге, где они используются!

Замените существующие блоки экспорта в шагах pipeline на:

```yaml
- name: Generate inventory
  run: |
    # Export all variables using unified exporter
    python .github/scripts/unified_variable_exporter.py \
      --step generate_inventory \
      --matrix-env ${{ matrix.environment }} \
      --variables-json '${{ needs.show_environment_variables.outputs.variables_json }}'
    
    # Load variables from GITHUB_ENV
    if [ -f "$GITHUB_ENV" ]; then
      set -a
      source "$GITHUB_ENV"
      set +a
    fi
    
    # All variables are now available from the unified exporter
    python3 /build_env/scripts/build_env/env_inventory_generation.py
```

**НЕ ДЕЛАЙТЕ ТАК** (переменные не передаются между шагами):
```yaml
- name: Export Environment Variables
  run: |
    python .github/scripts/unified_variable_exporter.py ...
- name: Generate inventory
  run: |
    # Переменные здесь НЕ БУДУТ доступны!
```

## Конфигурация переменных

### 1. pipeline_vars.yaml

Создайте файл `.github/pipeline_vars.yaml` с переменными по умолчанию:

```yaml
# Все значения должны быть строками
MY_VAR: "my_value"
ANOTHER_VAR: "another_value"
JSON_VAR: '{"key": "value"}'
BOOLEAN_VAR: "true"
NUMBER_VAR: "123"
```

### 2. GitHub Workflow Inputs

Переменные из workflow inputs автоматически экспортируются:

```yaml
workflow_dispatch:
  inputs:
    ENV_NAMES:
      required: true
      type: string
    MY_CUSTOM_VAR:
      required: false
      type: string
      default: ""
```

### 3. API Input

Передайте переменные через `GITHUB_PIPELINE_API_INPUT`:

```json
{
  "MY_VAR": "api_value",
  "ANOTHER_VAR": "another_api_value"
}
```

Или в формате key=value:

```
MY_VAR=api_value
ANOTHER_VAR=another_api_value
```

## Экспортируемые переменные

### Системные переменные

- `CI_PROJECT_DIR`
- `SECRET_KEY`
- `GITHUB_ACTIONS`
- `GITHUB_REPOSITORY`
- `GITHUB_REF_NAME`
- `GITHUB_USER_EMAIL`
- `GITHUB_USER_NAME`
- `GITHUB_TOKEN`
- `ENVGENE_AGE_PUBLIC_KEY`
- `ENVGENE_AGE_PRIVATE_KEY`
- `DOCKER_IMAGE_*`

### Job-specific переменные

- `FULL_ENV` - полное имя окружения
- `ENV_NAMES` - имена окружений
- `CLUSTER_NAME` - имя кластера
- `ENVIRONMENT_NAME` - имя окружения
- `ENV_NAME` - имя окружения
- `ENV_NAME_SHORT` - короткое имя окружения
- `SANITIZED_NAME` - санитизированное имя
- `PROJECT_DIR` - директория проекта

### Step-specific переменные

Для всех шагов:
- `INSTANCES_DIR` - директория инстансов
- `module_ansible_dir` - директория Ansible
- `module_inventory` - файл инвентаря
- `module_ansible_cfg` - конфиг Ansible
- `module_config_default` - конфиг по умолчанию
- `envgen_args` - аргументы envgen
- `envgen_debug` - режим отладки
- `GIT_STRATEGY` - стратегия Git
- `COMMIT_ENV` - коммит окружения

Для Credential Rotation:
- `CRED_ROTATION_FORCE`
- `CRED_ROTATION_PAYLOAD`
- `PUBLIC_AGE_KEYS`

## Примеры использования

### Пример 1: Добавление новой переменной через pipeline_vars.yaml

1. Добавьте в `.github/pipeline_vars.yaml`:
```yaml
MY_NEW_VAR: "default_value"
```

2. Переменная будет автоматически экспортирована во все шаги

### Пример 2: Переопределение через API

1. Вызовите workflow с API input:
```json
{
  "MY_NEW_VAR": "api_override_value"
}
```

2. Переменная будет иметь значение `api_override_value` во всех шагах

### Пример 3: Переопределение через workflow input

1. Добавьте в workflow inputs:
```yaml
MY_NEW_VAR:
  required: false
  type: string
  default: ""
```

2. Передайте значение при запуске workflow

## Тестирование

### Локальное тестирование

```bash
# Тест экспорта переменных
python .github/scripts/unified_variable_exporter.py \
  --step generate_inventory \
  --matrix-env test-cluster/e01 \
  --variables-json '{"TEST_VAR": "test_value"}' \
  --list-vars

# Тест генерации скрипта
python .github/scripts/unified_variable_exporter.py \
  --step env_build \
  --matrix-env test-cluster/e01 \
  --generate-script test_export.sh
```

### Тест с pipeline_vars.yaml

```bash
# Создайте тестовый файл
echo "TEST_VAR: test_value" > .github/pipeline_vars.yaml

# Запустите экспорт
python .github/scripts/unified_variable_exporter.py \
  --step generate_inventory \
  --matrix-env test-cluster/e01 \
  --list-vars
```

## Миграция существующего кода

### Замена существующих экспортов

**Было:**
```bash
export CLUSTER_NAME=$(echo "${{ matrix.environment }}" | cut -d'/' -f1)
export ENVIRONMENT_NAME=$(echo "${{ matrix.environment }}" | cut -d'/' -f2 | xargs)
# ... много других экспортов
```

**Стало:**
```bash
python .github/scripts/unified_variable_exporter.py \
  --step generate_inventory \
  --matrix-env ${{ matrix.environment }} \
  --variables-json '${{ needs.show_environment_variables.outputs.variables_json }}'
```

### Преимущества

1. **Единообразие** - все шаги используют одинаковый механизм экспорта
2. **Централизация** - все переменные управляются в одном месте
3. **Гибкость** - легко добавлять новые источники переменных
4. **Отладка** - простое логирование и отображение переменных
5. **Тестирование** - возможность локального тестирования

## Troubleshooting

### Проблема: Переменная не экспортируется

1. Проверьте приоритет источников
2. Убедитесь, что значение не пустое
3. Проверьте логи скрипта

### Проблема: Неправильное значение переменной

1. Проверьте, откуда берется значение (источник с наивысшим приоритетом)
2. Убедитесь в правильности формата в pipeline_vars.yaml
3. Проверьте JSON формат для API input

### Проблема: Переменная перезаписывается

1. Это ожидаемое поведение - переменные с более высоким приоритетом перезаписывают переменные с низким приоритетом
2. Используйте уникальные имена переменных для избежания конфликтов
