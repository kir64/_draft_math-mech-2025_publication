# main.py
import pytest
import requests
import json
import random
from metrics import coverage # Импортируем глобальный экземпляр

# Базовый URL API
BASE_URL = "https://petstore3.swagger.io/api/v3"

# Глобальная переменная для хранения ID созданного питомца
created_pet_id = None

# --- Вспомогательные функции ---
def generate_pet_data(pet_id=None, name_prefix="Buddy"):
    """Генерирует данные для создания/обновления питомца."""
    if pet_id is None:
        pet_id = random.randint(100000, 999999) # Генерируем случайный ID
    return {
        "id": pet_id,
        "name": f"{name_prefix}_{pet_id}",
        "category": {
            "id": 1,
            "name": "Dogs"
        },
        "photoUrls": [
            "string"
        ],
        "tags": [
            {
                "id": 0,
                "name": "string"
            }
        ],
        "status": "available"
    }

# --- Тесты ---

# --- E2E CRUD Flow ---
def test_e2e_create_pet():
    """Тест создания нового питомца (POST /pet)."""
    global created_pet_id
    endpoint = "POST /pet"
    url = f"{BASE_URL}/pet"
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    pet_data = generate_pet_data()
    created_pet_id = pet_data["id"] # Сохраняем ID для следующих шагов

    response = requests.post(url, headers=headers, data=json.dumps(pet_data))
    coverage.record_test_result(endpoint, response.status_code)

    assert response.status_code == 200
    try:
        response_json = response.json()
        assert response_json["id"] == created_pet_id
        assert response_json["name"] == pet_data["name"]
    except json.JSONDecodeError:
        pytest.fail(f"Response is not valid JSON: {response.text}")
    except KeyError:
        pytest.fail(f"Key 'id' or 'name' not found in response: {response.text}")

def test_e2e_get_pet_by_id():
    """Тест получения созданного питомца по ID (GET /pet/{petId})."""
    global created_pet_id
    assert created_pet_id is not None, "Pet ID not set from create test"
    endpoint = f"GET /pet/{{petId}}" # Используем шаблонный путь для метрик
    url = f"{BASE_URL}/pet/{created_pet_id}"
    headers = {'Accept': 'application/json'}

    response = requests.get(url, headers=headers)
    coverage.record_test_result(endpoint, response.status_code)

    assert response.status_code == 200
    try:
        response_json = response.json()
        assert response_json["id"] == created_pet_id
    except json.JSONDecodeError:
        pytest.fail(f"Response is not valid JSON: {response.text}")
    except KeyError:
         pytest.fail(f"Key 'id' not found in response: {response.text}")

def test_e2e_update_pet_put():
    """Тест обновления питомца (PUT /pet)."""
    global created_pet_id
    assert created_pet_id is not None, "Pet ID not set from create test"
    endpoint = "PUT /pet"
    url = f"{BASE_URL}/pet"
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    updated_pet_data = generate_pet_data(pet_id=created_pet_id, name_prefix="UpdatedBuddy")
    updated_pet_data["status"] = "pending" # Меняем статус

    response = requests.put(url, headers=headers, data=json.dumps(updated_pet_data))
    coverage.record_test_result(endpoint, response.status_code)

    assert response.status_code == 200
    try:
        response_json = response.json()
        assert response_json["id"] == created_pet_id
        assert response_json["name"] == updated_pet_data["name"]
        assert response_json["status"] == "pending"
    except json.JSONDecodeError:
         pytest.fail(f"Response is not valid JSON: {response.text}")
    except KeyError:
        pytest.fail(f"Required key not found in response: {response.text}")

def test_e2e_update_pet_post_form():
    """Тест обновления питомца с использованием данных формы (POST /pet/{petId})."""
    global created_pet_id
    assert created_pet_id is not None, "Pet ID not set from create test"
    endpoint = f"POST /pet/{{petId}}" # Используем шаблонный путь для метрик
    url = f"{BASE_URL}/pet/{created_pet_id}"
    headers = {'Accept': 'application/json'} # Content-Type будет application/x-www-form-urlencoded по умолчанию
    form_data = {
        'name': f'FormUpdatedName_{created_pet_id}',
        'status': 'sold'
    }

    response = requests.post(url, headers=headers, data=form_data)
    # Ожидаем 200 согласно документации openapi.json
    coverage.record_test_result(endpoint, response.status_code)

    assert response.status_code == 200
    # Проверим, что данные действительно обновились, сделав GET запрос
    get_response = requests.get(f"{BASE_URL}/pet/{created_pet_id}", headers={'Accept': 'application/json'})
    assert get_response.status_code == 200
    get_json = get_response.json()
    assert get_json["name"] == form_data['name']
    assert get_json["status"] == form_data['status']


def test_e2e_delete_pet():
    """Тест удаления питомца (DELETE /pet/{petId})."""
    global created_pet_id
    assert created_pet_id is not None, "Pet ID not set from create test"
    endpoint = f"DELETE /pet/{{petId}}" # Используем шаблонный путь для метрик
    url = f"{BASE_URL}/pet/{created_pet_id}"
    headers = {'Accept': 'application/json'}

    response = requests.delete(url, headers=headers)
    coverage.record_test_result(endpoint, response.status_code)

    assert response.status_code == 200

def test_e2e_get_deleted_pet():
    """Тест попытки получения удаленного питомца (GET /pet/{petId} -> 404)."""
    global created_pet_id
    assert created_pet_id is not None, "Pet ID not set from create test"
    endpoint = f"GET /pet/{{petId}}" # Тот же эндпоинт, но другой статус код
    url = f"{BASE_URL}/pet/{created_pet_id}"
    headers = {'Accept': 'application/json'}

    response = requests.get(url, headers=headers)
    coverage.record_test_result(endpoint, response.status_code) # Записываем 404

    assert response.status_code == 404


# --- Другие позитивные тесты ---
def test_get_pets_by_status_available():
    """Тест получения питомцев по статусу 'available' (GET /pet/findByStatus)."""
    endpoint = "GET /pet/findByStatus"
    url = f"{BASE_URL}/pet/findByStatus"
    headers = {'Accept': 'application/json'}
    params = {'status': 'available'}

    response = requests.get(url, headers=headers, params=params)
    coverage.record_test_result(endpoint, response.status_code)

    assert response.status_code == 200
    try:
        response_json = response.json()
        assert isinstance(response_json, list) # Ожидаем список
    except json.JSONDecodeError:
        pytest.fail(f"Response is not valid JSON: {response.text}")

def test_get_pets_by_tags():
    """Тест получения питомцев по тегу (GET /pet/findByTags)."""
    endpoint = "GET /pet/findByTags"
    url = f"{BASE_URL}/pet/findByTags"
    headers = {'Accept': 'application/json'}
    params = {'tags': 'string'} # Используем тег из примера данных

    response = requests.get(url, headers=headers, params=params)
    coverage.record_test_result(endpoint, response.status_code)

    assert response.status_code == 200
    try:
        response_json = response.json()
        assert isinstance(response_json, list)
    except json.JSONDecodeError:
        pytest.fail(f"Response is not valid JSON: {response.text}")


# --- Негативные тесты ---
def test_create_pet_invalid_data():
    """Тест создания питомца с невалидными данными (POST /pet -> 400/422/500)."""
    # OpenAPI спека говорит 'default' -> 500 Internal Server Error
    # или 400/422 для невалидных данных. Попробуем вызвать 500, отправив некорректный JSON
    endpoint = "POST /pet"
    url = f"{BASE_URL}/pet"
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    # Отправляем невалидный JSON
    invalid_json_data = '{"id": 123, "name": "Testy", "category": {"id": 1, "name": "Dogs"}, "photoUrls": ["url1", "url2"], "tags": [{"id": 1, "name": "tag1"}], "status": "available"' # Отсутствует закрывающая скобка

    response = requests.post(url, headers=headers, data=invalid_json_data)
    # Ожидаем код ошибки сервера (500) или Bad Request (400)
    coverage.record_test_result(endpoint, response.status_code)
    # Документация указывает 'default', что часто означает 500.
    # Иногда API возвращают 400 для невалидного JSON. Проверим оба.
    assert response.status_code in [500, 400] # Проверяем, что статус код в списке ожидаемых

def test_get_pet_by_invalid_id_string():
    """Тест получения питомца по невалидному ID (строка) (GET /pet/{petId} -> 400)."""
    endpoint = f"GET /pet/{{petId}}"
    invalid_id = "invalid_id_string"
    url = f"{BASE_URL}/pet/{invalid_id}"
    headers = {'Accept': 'application/json'}

    response = requests.get(url, headers=headers)
    coverage.record_test_result(endpoint, response.status_code) # Записываем 400

    assert response.status_code == 400 # Ожидаем 400 Bad Request из-за нечислового ID

def test_get_pet_by_nonexistent_id():
    """Тест получения питомца по несуществующему ID (GET /pet/{petId} -> 404)."""
    # Этот тест уже частично покрыт в E2E (test_e2e_get_deleted_pet),
    # но добавим отдельный тест с заведомо несуществующим ID (например, 0 или отрицательным)
    endpoint = f"GET /pet/{{petId}}"
    non_existent_id = 0 # ID 0 обычно не используется
    url = f"{BASE_URL}/pet/{non_existent_id}"
    headers = {'Accept': 'application/json'}

    response = requests.get(url, headers=headers)
    coverage.record_test_result(endpoint, response.status_code) # Записываем 404

    assert response.status_code == 404

def test_delete_nonexistent_pet():
    """Тест удаления несуществующего питомца (DELETE /pet/{petId} -> 404 или 400)."""
    # OpenAPI spec указывает 400 Bad Request, но 404 тоже логичен.
    # В реализации Petstore V3, похоже, возвращается 404.
    endpoint = f"DELETE /pet/{{petId}}"
    non_existent_id = 0 # Используем ID, который точно не существует
    url = f"{BASE_URL}/pet/{non_existent_id}"
    headers = {'Accept': 'application/json'}

    response = requests.delete(url, headers=headers)
    coverage.record_test_result(endpoint, response.status_code)

    # В Petstore V3 эндпоинт DELETE /pet/{petId} возвращает 404 для несуществующего ID
    assert response.status_code == 404

def test_update_nonexistent_pet_put():
    """Тест обновления несуществующего питомца (PUT /pet -> 404)."""
    # OpenAPI spec говорит 400/404/422. Попробуем обновить несуществующий ID.
    endpoint = "PUT /pet"
    url = f"{BASE_URL}/pet"
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    non_existent_id = -999
    pet_data = generate_pet_data(pet_id=non_existent_id)

    response = requests.put(url, headers=headers, data=json.dumps(pet_data))
    coverage.record_test_result(endpoint, response.status_code)

    # Реализация Petstore V3 возвращает 404, если ID в теле запроса не найден для PUT
    assert response.status_code == 404

def test_update_pet_form_nonexistent_id():
    """Тест обновления питомца формой с несуществующим ID (POST /pet/{petId} -> 404)."""
    # OpenAPI spec говорит 400 (Invalid ID supplied). Petstore V3 возвращает 404.
    endpoint = f"POST /pet/{{petId}}"
    non_existent_id = 0
    url = f"{BASE_URL}/pet/{non_existent_id}"
    headers = {'Accept': 'application/json'}
    form_data = {'name': 'Ghost', 'status': 'missing'}

    response = requests.post(url, headers=headers, data=form_data)
    coverage.record_test_result(endpoint, response.status_code)

    assert response.status_code == 404 # Ожидаем 404 Not Found

def test_upload_image_invalid_content_type():
    """Тест загрузки изображения с неверным Content-Type (POST /pet/{petId}/uploadImage -> 415)."""
    # Создадим временного питомца для этого теста
    temp_pet_data = generate_pet_data()
    temp_pet_id = temp_pet_data["id"]
    post_resp = requests.post(f"{BASE_URL}/pet", headers={'Content-Type': 'application/json'}, data=json.dumps(temp_pet_data))
    assert post_resp.status_code == 200, "Failed to create temporary pet for upload test"

    endpoint = f"POST /pet/{{petId}}/uploadImage"
    url = f"{BASE_URL}/pet/{temp_pet_id}/uploadImage"
    # Отправляем запрос без multipart/form-data, что должно вызвать ошибку
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    data = {"additionalMetadata": "test"}

    response = requests.post(url, headers=headers, data=json.dumps(data))
    coverage.record_test_result(endpoint, response.status_code)

    # Удаляем временного питомца
    requests.delete(f"{BASE_URL}/pet/{temp_pet_id}")

    # Ожидаем 415 Unsupported Media Type, так как не используем multipart/form-data
    assert response.status_code == 415


def test_get_pets_by_invalid_status():
    """Тест получения питомцев по невалидному статусу (GET /pet/findByStatus -> 400)."""
    endpoint = "GET /pet/findByStatus"
    url = f"{BASE_URL}/pet/findByStatus"
    headers = {'Accept': 'application/json'}
    params = {'status': 'non_existent_status_value_123'} # Невалидный статус

    response = requests.get(url, headers=headers, params=params)
    coverage.record_test_result(endpoint, response.status_code)

    assert response.status_code == 400 # Ожидаем Bad Request согласно спецификации
