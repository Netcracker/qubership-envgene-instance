# Интеграция Unified Variable Exporter в Pipeline

## ✅ Выполненные задачи

### 1. Создан единый Python скрипт
- **Файл**: `.github/scripts/unified_variable_exporter.py`
- **Функции**: Экспорт всех переменных из всех источников
- **Поддержка**: Все указанные шаги pipeline

### 2. Протестировано решение
- ✅ Базовое использование
- ✅ JSON переменные
- ✅ API input переменные
- ✅ pipeline_vars.yaml переменные
- ✅ Генерация shell скриптов
- ✅ Step-specific переменные

### 3. Интегрировано в pipeline.yml
Заменили все дублирующиеся экспорты в шагах:
- **Generate inventory** ✅
- **Credential Rotation** ✅
- **Build Env** ✅
- **Generate Effective Set** ✅
- **Git Commit** ✅

## 🔄 Что изменилось

### Было (дублирующиеся экспорты):
```bash
export CLUSTER_NAME=$(echo "${{ matrix.environment }}" | cut -d'/' -f1)
export ENVIRONMENT_NAME=$(echo "${{ matrix.environment }}" | cut -d'/' -f2 | xargs)
# ... много других экспортов в каждом шаге
```

### Стало (единый скрипт в том же шаге):
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

**ВАЖНО**: Переменные экспортируются в том же шаге, где используются, и загружаются через GITHUB_ENV!

## 📊 Результаты

### Устранено дублирование:
- **Generate inventory**: 4 экспорта → 1 скрипт
- **Credential Rotation**: 8 экспортов → 1 скрипт  
- **Build Env**: 20+ экспортов → 1 скрипт
- **Generate Effective Set**: 20+ экспортов → 1 скрипт
- **Git Commit**: 15+ экспортов → 1 скрипт

### Добавлена поддержка всех источников переменных:
1. **pipeline_vars.yaml** - переменные по умолчанию
2. **GitHub workflow inputs** - входные параметры
3. **API input** - переменные из `GITHUB_PIPELINE_API_INPUT`
4. **Системные переменные** - CI/CD переменные
5. **Job-specific переменные** - переменные для конкретного шага

## 🚀 Как использовать

### Добавление новой переменной:
1. Добавь в `.github/pipeline_vars.yaml`:
```yaml
MY_NEW_VAR: "my_value"
```

2. Переменная автоматически экспортируется во все шаги!

### Переопределение через API:
```json
{
  "MY_NEW_VAR": "api_override_value"
}
```

### Переопределение через workflow input:
Добавь в workflow inputs и передай значение при запуске.

## 📁 Созданные файлы

1. **`.github/scripts/unified_variable_exporter.py`** - основной скрипт
2. **`.github/pipeline_vars.yaml`** - конфигурация переменных
3. **`UNIFIED_VARIABLE_EXPORTER.md`** - полная документация
4. **`.github/scripts/test_unified_exporter.py`** - тесты
5. **`.github/scripts/demo_unified_exporter.py`** - демонстрация
6. **`.github/workflows/pipeline_with_unified_exporter.yml`** - пример интеграции

## 🎯 Преимущества

- ✅ **Единообразие** - все шаги используют одинаковый механизм
- ✅ **Централизация** - все переменные в одном месте
- ✅ **Гибкость** - легко добавлять новые источники
- ✅ **Отладка** - простое логирование переменных
- ✅ **Тестирование** - возможность локального тестирования
- ✅ **DRY принцип** - устранено дублирование кода

## 🔧 Команды для тестирования

```bash
# Базовое тестирование
python3 .github/scripts/unified_variable_exporter.py \
  --step generate_inventory \
  --matrix-env test-cluster/e01 \
  --list-vars

# С JSON переменными
python3 .github/scripts/unified_variable_exporter.py \
  --step env_build \
  --matrix-env test-cluster/e01 \
  --variables-json '{"MY_VAR": "my_value"}' \
  --list-vars

# Демонстрация
python3 .github/scripts/demo_unified_exporter.py

# Тесты
python3 .github/scripts/test_unified_exporter.py
```

## ✨ Готово к использованию!

Pipeline теперь использует единую систему управления переменными. Все дублирующиеся экспорты заменены на вызовы `unified_variable_exporter.py`, что делает код более чистым, поддерживаемым и расширяемым.
