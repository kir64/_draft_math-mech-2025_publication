import pytest
import requests
from metrics import coverage
import os

# Базовый URL API
BASE_URL = "https://petstore3.swagger.io/api/v3"

# Вспомогательные функции
def create_pet(pet_data):
    """Создает питомца через POST /pet."""
    response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    return response

def update_pet(pet_data):
    """Обновляет питомца через PUT /pet."""
    response = requests.put(f"{BASE_URL}/pet", json=pet_data)
    return response

def find_pet_by_status(status):
    """Находит питомцев по статусу через GET /pet/findByStatus."""
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": status})
    return response

def get_pet_by_id(pet_id):
    """Получает питомца по ID через GET /pet/{petId}."""
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    return response

def delete_pet(pet_id):
    """Удаляет питомца через DELETE /pet/{petId}."""
    headers = {"api_key": "special-key"}
    response = requests.delete(f"{BASE_URL}/pet/{pet_id}", headers=headers)
    return response

def upload_pet_image(pet_id, file_path="test_image.jpg"):
    """Загружает изображение для питомца через POST /pet/{petId}/uploadImage."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден. Пожалуйста, создайте файл перед выполнением теста.")
    files = {"file": open(file_path, "rb")}
    response = requests.post(f"{BASE_URL}/pet/{pet_id}/uploadImage", files=files)
    return response

# Тесты для эндпоинтов раздела Pet
@pytest.mark.positive
def test_create_pet():
    """Тест создания питомца."""
    pet_data = {
        "id": 999,
        "name": "TestPet",
        "category": {"id": 1, "name": "Dogs"},
        "photoUrls": ["http://example.com/photo"],
        "tags": [{"id": 1, "name": "tag1"}],
        "status": "available"
    }
    response = create_pet(pet_data)
    assert response.status_code == 200
    coverage.record_test_result("POST /pet", response.status_code)

@pytest.mark.positive
def test_update_pet():
    """Тест обновления питомца."""
    # Сначала создаем питомца
    pet_data = {
        "id": 999,
        "name": "TestPet",
        "category": {"id": 1, "name": "Dogs"},
        "photoUrls": ["http://example.com/photo"],
        "tags": [{"id": 1, "name": "tag1"}],
        "status": "available"
    }
    create_response = create_pet(pet_data)
    assert create_response.status_code == 200

    # Затем обновляем его
    pet_data["name"] = "UpdatedPet"
    response = update_pet(pet_data)
    assert response.status_code == 200
    coverage.record_test_result("PUT /pet", response.status_code)

@pytest.mark.positive
def test_find_pets_by_status():
    """Тест поиска питомцев по статусу."""
    response = find_pet_by_status("available")
    assert response.status_code == 200
    coverage.record_test_result("GET /pet/findByStatus", response.status_code)

@pytest.mark.positive
def test_get_pet_by_id():
    """Тест получения питомца по ID."""
    # Создаем питомца
    pet_data = {
        "id": 999,
        "name": "TestPet",
        "category": {"id": 1, "name": "Dogs"},
        "photoUrls": ["http://example.com/photo"],
        "tags": [{"id": 1, "name": "tag1"}],
        "status": "available"
    }
    create_response = create_pet(pet_data)
    assert create_response.status_code == 200

    # Получаем питомца
    pet_id = pet_data["id"]
    response = get_pet_by_id(pet_id)
    assert response.status_code == 200
    coverage.record_test_result("GET /pet/{petId}", response.status_code)

@pytest.mark.positive
def test_delete_pet():
    """Тест удаления питомца."""
    # Создаем питомца
    pet_data = {
        "id": 999,
        "name": "TestPet",
        "category": {"id": 1, "name": "Dogs"},
        "photoUrls": ["http://example.com/photo"],
        "tags": [{"id": 1, "name": "tag1"}],
        "status": "available"
    }
    create_response = create_pet(pet_data)
    assert create_response.status_code == 200

    # Удаляем питомца
    pet_id = pet_data["id"]
    response = delete_pet(pet_id)
    assert response.status_code == 200
    coverage.record_test_result("DELETE /pet/{petId}", response.status_code)

@pytest.mark.negative
def test_invalid_pet_creation():
    """Тест создания питомца с невалидными данными."""
    invalid_pet_data = {
        "id": "invalid_id",
        "name": "",
        "category": {"id": -1, "name": ""},
        "photoUrls": [],
        "tags": [],
        "status": "invalid_status"
    }
    response = create_pet(invalid_pet_data)
    assert response.status_code in [400, 422]
    coverage.record_test_result("POST /pet", response.status_code)

@pytest.mark.negative
def test_get_nonexistent_pet():
    """Тест получения несуществующего питомца."""
    non_existent_pet_id = 999999
    response = get_pet_by_id(non_existent_pet_id)
    assert response.status_code == 404
    coverage.record_test_result("GET /pet/{petId}", response.status_code)

@pytest.mark.negative
def test_delete_nonexistent_pet():
    """Тест удаления несуществующего питомца."""
    non_existent_pet_id = 999999
    response = delete_pet(non_existent_pet_id)
    assert response.status_code in [200, 404]  # Ожидаем 200 или 404 в зависимости от реализации API
    coverage.record_test_result("DELETE /pet/{petId}", response.status_code)

@pytest.mark.positive
def test_upload_pet_image():
    """Тест загрузки изображения для питомца."""
    # Создаем питомца
    pet_data = {
        "id": 999,
        "name": "TestPet",
        "category": {"id": 1, "name": "Dogs"},
        "photoUrls": ["http://example.com/photo"],
        "tags": [{"id": 1, "name": "tag1"}],
        "status": "available"
    }
    create_response = create_pet(pet_data)
    assert create_response.status_code == 200

    # Загружаем изображение
    pet_id = pet_data["id"]
    file_path = "test_image.jpg"
    with open(file_path, "wb") as f:
        f.write(b"fake image data")  # Создаем файл с фиктивными данными
    response = upload_pet_image(pet_id, file_path)
    os.remove(file_path)  # Удаляем временный файл после теста
    assert response.status_code == 200
    coverage.record_test_result("POST /pet/{petId}/uploadImage", response.status_code)

# End-to-end тест (CRUD операции)
@pytest.mark.e2e
def test_crud_operations():
    """End-to-end тест CRUD операций."""
    # Создание питомца
    pet_data = {
        "id": 1000,
        "name": "E2EPet",
        "category": {"id": 1, "name": "Dogs"},
        "photoUrls": ["http://example.com/photo"],
        "tags": [{"id": 1, "name": "tag1"}],
        "status": "available"
    }
    create_response = create_pet(pet_data)
    assert create_response.status_code == 200
    coverage.record_test_result("POST /pet", create_response.status_code)

    # Получение питомца
    pet_id = pet_data["id"]
    get_response = get_pet_by_id(pet_id)
    assert get_response.status_code == 200
    coverage.record_test_result("GET /pet/{petId}", get_response.status_code)

    # Обновление питомца
    pet_data["name"] = "UpdatedE2EPet"
    update_response = update_pet(pet_data)
    assert update_response.status_code == 200
    coverage.record_test_result("PUT /pet", update_response.status_code)

    # Удаление питомца
    delete_response = delete_pet(pet_id)
    assert delete_response.status_code == 200
    coverage.record_test_result("DELETE /pet/{petId}", delete_response.status_code)

# Финальный вывод метрик
def pytest_sessionfinish(session, exitstatus):
    """Вывод метрик покрытия после выполнения тестов."""
    metrics = coverage.calculate_metrics()
    print("\n==================================================")
    print("               API COVERAGE REPORT                ")
    print("==================================================")
    print(f"1. Среднее покрытие эндпоинтов раздела Pet: {metrics['avg_endpoint_coverage']:.1f}%")
    print(f"2. Покрытие статус-кодов раздела Pet: {metrics['pet_status_coverage']:.1f}%")
    print(f"3. Полностью покрытые эндпоинты API: {metrics['full_endpoint_coverage']:.1f}%")
    print(f"4. Общее покрытие статус-кодов API: {metrics['total_api_coverage']:.1f}%\n")

    print("Детали по endpoint'ам:")
    for endpoint, data in coverage.coverage_data.items():
        expected = data["status_codes"]
        tested = data["tested"]
        ratio = len(tested) / len(expected) * 100 if expected else 0
        print(f"{endpoint}: {len(tested)}/{len(expected)} ({ratio:.1f}%) ------> {tested} / {expected}")
