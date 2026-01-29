#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Клиентская часть для тестирования API
ПМ.01 - Интеграция модулей через API
"""

import requests
import json

# Базовый URL API
API_BASE = 'http://localhost:5000/api/v1'

def print_response(title, response):
    """Красивый вывод ответа"""
    print(f"\n{'='*60}")
    print(f"🔹 {title}")
    print(f"{'='*60}")
    print(f"Статус: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except:
        print(response.text)
    print()


def test_get_data():
    """3.2.1 Тест: Получение данных"""
    print("\n📥 ТЕСТ 1: Получение всех данных (GET /api/v1/data)")
    try:
        response = requests.get(f'{API_BASE}/data')
        print_response("Получение данных", response)
        return response.json() if response.ok else None
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка: Сервер не запущен! Запусти: python app.py")
        return None


def test_post_data():
    """3.2.2 Тест: Отправка данных"""
    print("\n📤 ТЕСТ 2: Отправка новых данных (POST /api/v1/data)")

    test_data = [
        {
            "код": "101",
            "наименование": "Тестовый товар API",
            "категория": "Тест",
            "количество": "5",
            "цена": "1000"
        },
        {
            "код": "102",
            "наименование": "Второй тестовый",
            "категория": "Тест",
            "количество": "10",
            "цена": "2000"
        }
    ]

    try:
        response = requests.post(
            f'{API_BASE}/data',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        print_response("Отправка данных", response)
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка: Сервер не запущен!")


def test_filter_category():
    """3.2.3 Тест: Фильтрация по категории"""
    print("\n🔍 ТЕСТ 3: Фильтрация по категории (POST /api/v1/filter)")

    filter_params = {
        "категория": "Электроника"
    }

    try:
        response = requests.post(
            f'{API_BASE}/filter',
            json=filter_params,
            headers={'Content-Type': 'application/json'}
        )
        print_response("Фильтр: Электроника", response)
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка: Сервер не запущен!")


def test_filter_price_range():
    """3.2.4 Тест: Фильтрация по диапазону цены"""
    print("\n💰 ТЕСТ 4: Фильтрация по цене (POST /api/v1/filter)")

    filter_params = {
        "min_price": 5000,
        "max_price": 30000
    }

    try:
        response = requests.post(
            f'{API_BASE}/filter',
            json=filter_params,
            headers={'Content-Type': 'application/json'}
        )
        print_response("Фильтр: цена 5000-30000", response)
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка: Сервер не запущен!")


def test_combined_filter():
    """3.2.5 Тест: Комбинированная фильтрация"""
    print("\n🎯 ТЕСТ 5: Комбинированная фильтрация")

    filter_params = {
        "категория": "Периферия",
        "max_price": 5000
    }

    try:
        response = requests.post(
            f'{API_BASE}/filter',
            json=filter_params,
            headers={'Content-Type': 'application/json'}
        )
        print_response("Фильтр: Периферия до 5000р", response)
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка: Сервер не запущен!")


def test_stats():
    """3.2.6 Тест: Статистика"""
    print("\n📊 ТЕСТ 6: Статистика (POST /api/v1/stats)")

    try:
        response = requests.post(
            f'{API_BASE}/stats',
            json={},
            headers={'Content-Type': 'application/json'}
        )
        print_response("Статистика", response)
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка: Сервер не запущен!")


def test_error_handling():
    """3.3 Тест: Обработка ошибок"""
    print("\n⚠️ ТЕСТ 7: Обработка ошибочных запросов")

    # Неверный формат данных
    print("\n7.1 Отправка строки вместо массива:")
    try:
        response = requests.post(
            f'{API_BASE}/data',
            json="неверный формат",
            headers={'Content-Type': 'application/json'}
        )
        print_response("Ошибка формата", response)
    except:
        pass

    # Отсутствующие поля
    print("\n7.2 Отправка данных без обязательных полей:")
    try:
        response = requests.post(
            f'{API_BASE}/data',
            json=[{"код": "999"}],  # нет остальных полей
            headers={'Content-Type': 'application/json'}
        )
        print_response("Ошибка валидации", response)
    except:
        pass


def main():
    """Главная функция - запуск всех тестов"""
    print("\n" + "="*60)
    print("🚀 ТЕСТИРОВАНИЕ API МОДУЛЯ ИНТЕГРАЦИИ")
    print("="*60)
    print("\n⚠️  Убедись, что сервер запущен: python app.py")
    print("    API доступен на: http://localhost:5000/api/v1")

    input("\n▶️  Нажми Enter для начала тестирования...")

    # Запуск тестов
    test_get_data()
    test_post_data()
    test_filter_category()
    test_filter_price_range()
    test_combined_filter()
    test_stats()
    test_error_handling()

    print("\n" + "="*60)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*60)
    print("\n📝 Результаты тестов можно использовать в отчёте!")


if __name__ == '__main__':
    main()
