# 🚀 Инструкция по запуску проекта

## Шаг 1: Установка зависимостей

```bash
pip install -r requirements.txt
```

Или установи вручную:
```bash
pip install Flask flask-cors pandas requests
```

---

## Шаг 2: Структура проекта

```
project/
├── app.py                      # Основной сервер Flask
├── api_client.py               # Клиент для тестирования API
├── requirements.txt            # Зависимости
├── API_DOCUMENTATION.md        # Документация API
├── templates/
│   └── index.html             # Веб-интерфейс
├── data/                      # Папка для загруженных данных
├── товары.csv                 # Данные товаров
├── товары.json
└── товары.txt
```

---

## Шаг 3: Добавление API в app.py

Открой `app.py` и **добавь код из `api_routes_addon.py`** перед строкой:
```python
if __name__ == '__main__':
```

Скопируй весь блок с маркером `# ============ API ИНТЕГРАЦИЯ`.

---

## Шаг 4: Создание папки data

```bash
mkdir data
```

Или в Windows:
```cmd
md data
```

---

## Шаг 5: Запуск сервера

```bash
python app.py
```

Сервер запустится на: **http://localhost:5000**

Проверь в браузере:
- Веб-интерфейс: http://localhost:5000
- API: http://localhost:5000/api/v1/data

---

## Шаг 6: Тестирование API

Открой **новый терминал** (не закрывая сервер!) и запусти:

```bash
python api_client.py
```

Клиент выполнит 7 автоматических тестов и выведет результаты.

---

## Шаг 7: Ручное тестирование с curl

### Получить данные:
```bash
curl http://localhost:5000/api/v1/data
```

### Отправить данные:
```bash
curl -X POST http://localhost:5000/api/v1/data \
  -H "Content-Type: application/json" \
  -d '[{"код":"999","наименование":"Тест","категория":"API","количество":"10","цена":"5000"}]'
```

### Фильтрация:
```bash
curl -X POST http://localhost:5000/api/v1/filter \
  -H "Content-Type: application/json" \
  -d '{"категория":"Электроника"}'
```

---

## Решение проблем

### Ошибка: "ModuleNotFoundError: No module named 'flask'"
```bash
pip install Flask
```

### Ошибка: "Address already in use"
Порт 5000 занят. Измени в app.py:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Ошибка: "Connection refused" в api_client.py
Убедись, что `app.py` запущен в другом терминале.

### Файл товары.csv не найден
Скопируй `товары.csv` в ту же папку, где находится `app.py`.

---

