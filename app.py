# -*- coding: utf-8 -*-
"""
Модуль обработки и фильтрации данных информационной системы
Версия на Python (Backend Flask)
ПМ.01 - Разработка модулей программного обеспечения для компьютерных систем
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import csv
import json
import os
from datetime import datetime
from io import StringIO, BytesIO
import pandas as pd

app = Flask(__name__)
CORS(app)

# Хранилище данных сессии
sessions = {}


class DataProcessor:
    """Класс для обработки и фильтрации данных"""
    
    # Обязательные поля
    REQUIRED_FIELDS = ['код', 'наименование', 'категория', 'количество', 'цена']
    
    def __init__(self):
        self.data = []
        self.original_data = []
        self.current_filters = {}
    
    def load_csv(self, content):
        """Загрузка данных из CSV"""
        try:
            reader = csv.DictReader(StringIO(content))
            data = list(reader)
            if not data:
                raise ValueError('CSV файл пуст')
            self._validate_data(data)
            self.data = data
            self.original_data = [row.copy() for row in data]
            return True, f"Загружено {len(data)} записей из CSV"
        except Exception as e:
            return False, f"Ошибка CSV: {str(e)}"
    
    def load_json(self, content):
        """Загрузка данных из JSON"""
        try:
            data = json.loads(content)
            if not isinstance(data, list):
                raise ValueError('JSON должен содержать массив объектов')
            if not data:
                raise ValueError('JSON массив пуст')
            self._validate_data(data)
            self.data = data
            self.original_data = [row.copy() for row in data]
            return True, f"Загружено {len(data)} записей из JSON"
        except json.JSONDecodeError as e:
            return False, f"Некорректный JSON: {str(e)}"
        except Exception as e:
            return False, f"Ошибка JSON: {str(e)}"
    
    def load_txt(self, content):
        """Загрузка данных из TXT (табуляция или двойные пробелы)"""
        try:
            lines = content.strip().split('\n')
            if len(lines) < 2:
                raise ValueError('TXT файл должен содержать заголовок и данные')
            
            # Определяем разделитель (табуляция или двойные пробелы)
            if '\t' in lines[0]:
                sep = '\t'
            else:
                sep = None  # Используем split() с регулярным выражением
            
            if sep:
                headers = [h.strip().lower() for h in lines[0].split(sep)]
                data = []
                for line in lines[1:]:
                    if line.strip():
                        values = [v.strip() for v in line.split(sep)]
                        row = dict(zip(headers, values))
                        data.append(row)
            else:
                # Используем стандартный разделитель
                headers = [h.strip().lower() for h in lines[0].split()]
                data = []
                for line in lines[1:]:
                    if line.strip():
                        values = [v.strip() for v in line.split()]
                        row = dict(zip(headers, values))
                        data.append(row)
            
            if not data:
                raise ValueError('TXT файл не содержит данных')
            
            self._validate_data(data)
            self.data = data
            self.original_data = [row.copy() for row in data]
            return True, f"Загружено {len(data)} записей из TXT"
        except Exception as e:
            return False, f"Ошибка TXT: {str(e)}"
    
    def _validate_data(self, data):
        """Проверка наличия обязательных полей"""
        if not data:
            raise ValueError('Нет данных для проверки')
        
        first_row = data[0]
        row_keys = [k.lower() for k in first_row.keys()]
        
        missing_fields = [f for f in self.REQUIRED_FIELDS if f not in row_keys]
        if missing_fields:
            raise ValueError(f"Отсутствуют обязательные поля: {', '.join(missing_fields)}")
    
    def filter_data(self, field, value, operator='contains'):
        """Фильтрация данных"""
        try:
            self.data = [row.copy() for row in self.original_data]
            
            if not field or not value:
                return False, "Укажите поле и значение для фильтрации"
            
            field_lower = field.lower()
            filtered = []
            
            if operator == 'contains':
                # Текстовый поиск
                filtered = [
                    row for row in self.data 
                    if field_lower in row and value.lower() in str(row[field_lower]).lower()
                ]
            
            elif operator == 'range':
                # Диапазон (для числовых полей)
                try:
                    range_vals = value.split('-')
                    if len(range_vals) != 2:
                        return False, "Укажите диапазон в формате 'от-до' (например: 100-5000)"
                    
                    min_val = float(range_vals[0].strip())
                    max_val = float(range_vals[1].strip())
                    
                    filtered = [
                        row for row in self.data
                        if field_lower in row and min_val <= float(row[field_lower]) <= max_val
                    ]
                except ValueError:
                    return False, "Диапазон должен содержать числовые значения"
            
            elif operator == 'exact':
                # Точное совпадение
                filtered = [
                    row for row in self.data
                    if field_lower in row and str(row[field_lower]).lower() == value.lower()
                ]
            
            self.data = filtered
            self.current_filters = {'field': field, 'value': value, 'operator': operator}
            
            return True, f"Применён фильтр: найдено {len(filtered)} записей"
        
        except Exception as e:
            return False, f"Ошибка фильтрации: {str(e)}"
    
    def sort_data(self, field, order='asc'):
        """Сортировка данных"""
        try:
            if not field:
                return False, "Укажите поле для сортировки"
            
            field_lower = field.lower()
            
            def sort_key(row):
                val = row.get(field_lower, '')
                try:
                    return float(val)
                except:
                    return str(val).lower()
            
            self.data.sort(key=sort_key, reverse=(order == 'desc'))
            return True, f"Данные отсортированы по полю '{field}' {'▼' if order == 'desc' else '▲'}"
        
        except Exception as e:
            return False, f"Ошибка сортировки: {str(e)}"
    
    def calculate_stats(self, field=None):
        """Расчёт статистики"""
        try:
            stats = {}
            
            # Статистика по количеству
            if field is None or field == 'количество':
                qty_values = []
                for row in self.data:
                    try:
                        val = float(row.get('количество', 0))
                        qty_values.append(val)
                    except:
                        pass
                
                if qty_values:
                    stats['количество'] = {
                        'сумма': sum(qty_values),
                        'среднее': sum(qty_values) / len(qty_values),
                        'минимум': min(qty_values),
                        'максимум': max(qty_values),
                        'записей': len(qty_values)
                    }
            
            # Статистика по цене
            if field is None or field == 'цена':
                price_values = []
                for row in self.data:
                    try:
                        val = float(row.get('цена', 0))
                        price_values.append(val)
                    except:
                        pass
                
                if price_values:
                    stats['цена'] = {
                        'сумма': sum(price_values),
                        'среднее': sum(price_values) / len(price_values),
                        'минимум': min(price_values),
                        'максимум': max(price_values),
                        'записей': len(price_values)
                    }
            
            return True, stats
        
        except Exception as e:
            return False, f"Ошибка расчёта: {str(e)}"
    
    def export_csv(self):
        """Экспорт в CSV"""
        try:
            if not self.data:
                return None
            
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=self.data[0].keys())
            writer.writeheader()
            writer.writerows(self.data)
            return output.getvalue()
        except Exception as e:
            raise Exception(f"Ошибка экспорта CSV: {str(e)}")
    
    def export_json(self):
        """Экспорт в JSON"""
        try:
            if not self.data:
                return None
            return json.dumps(self.data, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"Ошибка экспорта JSON: {str(e)}")

    def load_txt(self, content):
        """Загрузка данных из TXT (поддержка ;, табуляции и пробелов)"""
        try:
            lines = content.strip().split('\n')
            if len(lines) < 2:
                raise ValueError('TXT файл должен содержать заголовок и данные')

            header_line = lines[0]

            # Определяем разделитель
            if ';' in header_line:
                sep = ';'
            elif '\t' in header_line:
                sep = '\t'
            else:
                sep = None  # будем резать по пробелам

            data = []

            if sep is not None:
                # Разделитель ; или \t
                headers = [h.strip().lower() for h in header_line.split(sep)]
                for line in lines[1:]:
                    if not line.strip():
                        continue
                    values = [v.strip() for v in line.split(sep)]
                    row = dict(zip(headers, values))
                    data.append(row)
            else:
                # Старый вариант: несколько пробелов / пробелы
                headers = [h.strip().lower() for h in header_line.split()]
                for line in lines[1:]:
                    if not line.strip():
                        continue
                    values = [v.strip() for v in line.split()]
                    row = dict(zip(headers, values))
                    data.append(row)

            if not data:
                raise ValueError('TXT файл не содержит данных')

            self._validate_data(data)
            self.data = data
            self.original_data = [row.copy() for row in data]
            return True, f"Загружено {len(data)} записей из TXT"

        except Exception as e:
            return False, f"Ошибка TXT: {str(e)}"

    def get_data(self):
        """Получить текущие данные"""
        return self.data
    
    def get_original_data(self):
        """Получить оригинальные данные"""
        return self.original_data
    
    def clear(self):
        """Очистить данные"""
        self.data = []
        self.original_data = []
        self.current_filters = {}


# ============ ROUTES ============

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """API для загрузки файла"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'Файл не выбран'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Файл не выбран'}), 400
        
        filename = file.filename.lower()
        content = file.read().decode('utf-8-sig')
        
        processor = DataProcessor()
        
        if filename.endswith('.csv'):
            success, message = processor.load_csv(content)
        elif filename.endswith('.json'):
            success, message = processor.load_json(content)
        elif filename.endswith('.txt'):
            success, message = processor.load_txt(content)
        else:
            return jsonify({'success': False, 'message': 'Неподдерживаемый формат файла'}), 400
        
        if success:
            session_id = datetime.now().strftime('%Y%m%d%H%M%S')
            sessions[session_id] = processor
            return jsonify({
                'success': True,
                'message': message,
                'session_id': session_id,
                'data': processor.get_data()
            })
        else:
            return jsonify({'success': False, 'message': message}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 500


@app.route('/api/filter', methods=['POST'])
def filter_data():
    """API для фильтрации"""
    try:
        data = request.json
        session_id = data.get('session_id')
        field = data.get('field')
        value = data.get('value')
        operator = data.get('operator', 'contains')
        
        if session_id not in sessions:
            return jsonify({'success': False, 'message': 'Сессия не найдена'}), 400
        
        processor = sessions[session_id]
        success, message = processor.filter_data(field, value, operator)
        
        return jsonify({
            'success': success,
            'message': message,
            'data': processor.get_data() if success else []
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 500


@app.route('/api/sort', methods=['POST'])
def sort_data():
    """API для сортировки"""
    try:
        data = request.json
        session_id = data.get('session_id')
        field = data.get('field')
        order = data.get('order', 'asc')
        
        if session_id not in sessions:
            return jsonify({'success': False, 'message': 'Сессия не найдена'}), 400
        
        processor = sessions[session_id]
        success, message = processor.sort_data(field, order)
        
        return jsonify({
            'success': success,
            'message': message,
            'data': processor.get_data() if success else []
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 500


@app.route('/api/stats', methods=['POST'])
def get_stats():
    """API для расчёта статистики"""
    try:
        data = request.json
        session_id = data.get('session_id')
        field = data.get('field')
        
        if session_id not in sessions:
            return jsonify({'success': False, 'message': 'Сессия не найдена'}), 400
        
        processor = sessions[session_id]
        success, stats = processor.calculate_stats(field)
        
        return jsonify({
            'success': success,
            'stats': stats if success else {}
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 500


@app.route('/api/export/<format>', methods=['POST'])
def export_data(format):
    """API для экспорта данных"""
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if session_id not in sessions:
            return jsonify({'success': False, 'message': 'Сессия не найдена'}), 400
        
        processor = sessions[session_id]
        
        if format == 'csv':
            content = processor.export_csv()
            filename = 'data.csv'
            mimetype = 'text/csv'
        elif format == 'json':
            content = processor.export_json()
            filename = 'data.json'
            mimetype = 'application/json'
        elif format == 'txt':
            content = processor.export_txt()
            filename = 'data.txt'
            mimetype = 'text/plain'
        else:
            return jsonify({'success': False, 'message': 'Неподдерживаемый формат'}), 400
        
        if not content:
            return jsonify({'success': False, 'message': 'Нет данных для экспорта'}), 400
        
        output = BytesIO()
        output.write(content.encode('utf-8'))
        output.seek(0)
        
        return send_file(
            output,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 500


@app.route('/api/reset', methods=['POST'])
def reset_data():
    """API для сброса фильтров"""
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if session_id not in sessions:
            return jsonify({'success': False, 'message': 'Сессия не найдена'}), 400
        
        processor = sessions[session_id]
        processor.data = [row.copy() for row in processor.original_data]
        processor.current_filters = {}
        
        return jsonify({
            'success': True,
            'message': 'Фильтры очищены',
            'data': processor.get_data()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 500


@app.route('/api/sample/<format>', methods=['GET'])
def get_sample(format):
    """API для получения примеров данных"""
    try:
        if format == 'csv':
            content = """код,наименование,категория,количество,цена
001,Ноутбук Dell,Электроника,25,85000
002,Клавиатура Mechanical,Электроника,150,3500
003,Монитор LG,Электроника,40,15000
004,Мышка Logitech,Электроника,200,1200
005,Рубашка хлопковая,Одежда,120,2000
006,Джинсы синие,Одежда,80,3500
007,Кроссовки Nike,Обувь,60,8000
008,Носки комплект,Одежда,300,500
009,Шляпа летняя,Одежда,45,1500
010,Сумка кожаная,Аксессуары,30,12000"""
            
            processor = DataProcessor()
            processor.load_csv(content)
            
            session_id = datetime.now().strftime('%Y%m%d%H%M%S') + format
            sessions[session_id] = processor
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'data': processor.get_data(),
                'message': f'Загружен пример CSV ({len(processor.get_data())} записей)'
            })
        
        elif format == 'json':
            content = '''[
  {"код":"001","наименование":"Ноутбук Dell","категория":"Электроника","количество":"25","цена":"85000"},
  {"код":"002","наименование":"Клавиатура Mechanical","категория":"Электроника","количество":"150","цена":"3500"},
  {"код":"003","наименование":"Монитор LG","категория":"Электроника","количество":"40","цена":"15000"},
  {"код":"004","наименование":"Мышка Logitech","категория":"Электроника","количество":"200","цена":"1200"},
  {"код":"005","наименование":"Рубашка хлопковая","категория":"Одежда","количество":"120","цена":"2000"},
  {"код":"006","наименование":"Джинсы синие","категория":"Одежда","количество":"80","цена":"3500"},
  {"код":"007","наименование":"Кроссовки Nike","категория":"Обувь","количество":"60","цена":"8000"},
  {"код":"008","наименование":"Носки комплект","категория":"Одежда","количество":"300","цена":"500"},
  {"код":"009","наименование":"Шляпа летняя","категория":"Одежда","количество":"45","цена":"1500"},
  {"код":"010","наименование":"Сумка кожаная","категория":"Аксессуары","количество":"30","цена":"12000"}
]'''
            
            processor = DataProcessor()
            processor.load_json(content)
            
            session_id = datetime.now().strftime('%Y%m%d%H%M%S') + format
            sessions[session_id] = processor
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'data': processor.get_data(),
                'message': f'Загружен пример JSON ({len(processor.get_data())} записей)'
            })
        
        else:
            return jsonify({'success': False, 'message': 'Неподдерживаемый формат'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 500


# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Не найдено'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Ошибка сервера'}), 500

# ============ API ИНТЕГРАЦИЯ (ТЗ: Интеграция модулей через API) ============

@app.route('/api/v1/data', methods=['GET'])
def api_v1_get_data():
    """3.1.1 Получение данных через API"""
    try:
        # Загружаем данные из файла
        processor = DataProcessor()
        with open('товары.csv', 'r', encoding='utf-8-sig') as f:
            content = f.read()
        success, message = processor.load_csv(content)

        if success:
            return jsonify({
                'status': 'success',
                'count': len(processor.get_data()),
                'data': processor.get_data()
            }), 200
        else:
            return jsonify({'status': 'error', 'message': message}), 400
    except FileNotFoundError:
        return jsonify({'status': 'error', 'message': 'Файл tovary.csv не найден'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/v1/data', methods=['POST'])
def api_v1_post_data():
    """3.1.2 Передача данных через API"""
    try:
        data = request.json

        # Валидация
        if not isinstance(data, list):
            return jsonify({'status': 'error', 'message': 'Данные должны быть массивом объектов'}), 400

        if not data:
            return jsonify({'status': 'error', 'message': 'Массив данных пуст'}), 400

        # Проверка обязательных полей
        required_fields = ['код', 'наименование', 'категория', 'количество', 'цена']
        for item in data:
            missing = [f for f in required_fields if f not in item]
            if missing:
                return jsonify({
                    'status': 'error',
                    'message': f'Отсутствуют поля: {", ".join(missing)}'
                }), 400

        # Сохраняем в CSV
        processor = DataProcessor()
        processor.data = data
        csv_content = processor.export_csv()

        with open('data/api_uploaded.csv', 'w', encoding='utf-8-sig') as f:
            f.write(csv_content)

        return jsonify({
            'status': 'success',
            'message': f'Сохранено {len(data)} записей',
            'saved_to': 'data/api_uploaded.csv'
        }), 201

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/v1/filter', methods=['POST'])
def api_v1_filter():
    """3.1.3 Обработка запросов - фильтрация через API"""
    try:
        params = request.json or {}

        # Загружаем данные
        processor = DataProcessor()
        with open('товары.csv', 'r', encoding='utf-8-sig') as f:
            content = f.read()
        processor.load_csv(content)

        # Применяем фильтры
        filtered_data = processor.get_data()

        # Фильтр по категории
        if 'категория' in params and params['категория']:
            filtered_data = [
                row for row in filtered_data
                if params['категория'].lower() in row.get('категория', '').lower()
            ]

        # Фильтр по минимальной цене
        if 'min_price' in params:
            try:
                min_price = float(params['min_price'])
                filtered_data = [
                    row for row in filtered_data
                    if float(row.get('цена', 0)) >= min_price
                ]
            except ValueError:
                return jsonify({'status': 'error', 'message': 'min_price должна быть числом'}), 400

        # Фильтр по максимальной цене
        if 'max_price' in params:
            try:
                max_price = float(params['max_price'])
                filtered_data = [
                    row for row in filtered_data
                    if float(row.get('цена', 0)) <= max_price
                ]
            except ValueError:
                return jsonify({'status': 'error', 'message': 'max_price должна быть числом'}), 400

        # Фильтр по наименованию
        if 'наименование' in params and params['наименование']:
            filtered_data = [
                row for row in filtered_data
                if params['наименование'].lower() in row.get('наименование', '').lower()
            ]

        return jsonify({
            'status': 'success',
            'count': len(filtered_data),
            'filters': params,
            'data': filtered_data
        }), 200

    except FileNotFoundError:
        return jsonify({'status': 'error', 'message': 'Файл tovary.csv не найден'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/v1/stats', methods=['POST'])
def api_v1_stats():
    """Статистика через API"""
    try:
        params = request.json or {}

        processor = DataProcessor()
        with open('товары.csv', 'r', encoding='utf-8-sig') as f:
            content = f.read()
        processor.load_csv(content)

        # Применяем фильтры если есть
        if 'категория' in params:
            processor.filter_data('категория', params['категория'], 'contains')

        success, stats = processor.calculate_stats()

        return jsonify({
            'status': 'success',
            'stats': stats
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Обработка ошибок API
@app.errorhandler(400)
def bad_request(e):
    return jsonify({'status': 'error', 'message': 'Некорректный запрос'}), 400

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'status': 'error', 'message': 'Метод не поддерживается'}), 405

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
