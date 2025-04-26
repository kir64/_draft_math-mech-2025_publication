import pytest
import requests
import json
from metrics import coverage

BASE_URL = "https://petstore3.swagger.io/api/v3"
PET_ENDPOINTS = [
    "POST /pet",
    "PUT /pet",
    "GET /pet/findByStatus",
    "GET /pet/findByTags",
    "GET /pet/{petId}",
    "POST /pet/{petId}",
    "DELETE /pet/{petId}",
    "POST /pet/{petId}/uploadImage"
]


@pytest.fixture
def setup_pet():
    # Создаем питомца для тестов
    pet_data = {
        "id": 1001,
        "name": "TestDog",
        "category": {"id": 1, "name": "Dogs"},
        "photoUrls": ["string"],
        "tags": [{"id": 0, "name": "string"}],
        "status": "available"
    }
    response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    assert response.status_code == 200
    yield pet_data
    # Удаляем питомца после тестов
    requests.delete(f"{BASE_URL}/pet/{pet_data['id']}")


def test_add_pet(setup_pet):
    """Тест добавления питомца (POST /pet)"""
    pet_data = setup_pet
    response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    coverage.record_test_result("POST /pet", response.status_code)
    assert response.status_code == 200
    assert response.json()["name"] == pet_data["name"]


def test_add_pet_invalid_data():
    """Негативный тест добавления питомца с невалидными данными"""
    invalid_data = {"invalid": "data"}
    response = requests.post(f"{BASE_URL}/pet", json=invalid_data)
    coverage.record_test_result("POST /pet", response.status_code)
    assert response.status_code in [400, 422, 500]


def test_update_pet(setup_pet):
    """Тест обновления питомца (PUT /pet)"""
    pet_data = setup_pet
    pet_data["name"] = "UpdatedDog"
    response = requests.put(f"{BASE_URL}/pet", json=pet_data)
    coverage.record_test_result("PUT /pet", response.status_code)
    assert response.status_code == 200
    assert response.json()["name"] == "UpdatedDog"


def test_update_nonexistent_pet():
    """Негативный тест обновления несуществующего питомца"""
    nonexistent_pet = {
        "id": 999999,
        "name": "Nonexistent",
        "status": "sold"
    }
    response = requests.put(f"{BASE_URL}/pet", json=nonexistent_pet)
    coverage.record_test_result("PUT /pet", response.status_code)
    assert response.status_code in [404, 500]


def test_find_pet_by_status():
    """Тест поиска питомцев по статусу (GET /pet/findByStatus)"""
    for status in ["available", "pending", "sold"]:
        response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": status})
        coverage.record_test_result("GET /pet/findByStatus", response.status_code)
        assert response.status_code == 200
        assert isinstance(response.json(), list)


def test_find_pet_by_status_invalid():
    """Негативный тест поиска питомцев по невалидному статусу"""
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "invalid"})
    coverage.record_test_result("GET /pet/findByStatus", response.status_code)
    assert response.status_code in [400, 500]


def test_find_pet_by_tags():
    """Тест поиска питомцев по тегам (GET /pet/findByTags)"""
    response = requests.get(f"{BASE_URL}/pet/findByTags", params={"tags": "string"})
    coverage.record_test_result("GET /pet/findByTags", response.status_code)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_pet_by_id(setup_pet):
    """Тест получения питомца по ID (GET /pet/{petId})"""
    pet_data = setup_pet
    response = requests.get(f"{BASE_URL}/pet/{pet_data['id']}")
    coverage.record_test_result("GET /pet/{petId}", response.status_code)
    assert response.status_code == 200
    assert response.json()["id"] == pet_data["id"]


def test_get_nonexistent_pet():
    """Негативный тест получения несуществующего питомца"""
    response = requests.get(f"{BASE_URL}/pet/999999")
    coverage.record_test_result("GET /pet/{petId}", response.status_code)
    assert response.status_code == 404


def test_update_pet_with_form_data(setup_pet):
    """Тест обновления питомца через форму (POST /pet/{petId})"""
    pet_data = setup_pet
    form_data = {
        "name": "FormUpdated",
        "status": "pending"
    }
    response = requests.post(
        f"{BASE_URL}/pet/{pet_data['id']}",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    coverage.record_test_result("POST /pet/{petId}", response.status_code)
    assert response.status_code == 200


def test_delete_pet(setup_pet):
    """Тест удаления питомца (DELETE /pet/{petId})"""
    pet_data = setup_pet
    response = requests.delete(f"{BASE_URL}/pet/{pet_data['id']}")
    coverage.record_test_result("DELETE /pet/{petId}", response.status_code)
    assert response.status_code == 200


def test_upload_pet_image(setup_pet):
    """Тест загрузки изображения для питомца (POST /pet/{petId}/uploadImage)"""
    pet_data = setup_pet
    files = {'file': ('image.jpg', b'fake image data', 'image/jpeg')}
    response = requests.post(
        f"{BASE_URL}/pet/{pet_data['id']}/uploadImage",
        files=files
    )
    coverage.record_test_result("POST /pet/{petId}/uploadImage", response.status_code)
    assert response.status_code in [200, 415]


def test_pet_crud_workflow():
    """End-to-end тест CRUD операций для питомца"""
    # Create
    pet_data = {
        "id": 1002,
        "name": "CRUDDog",
        "category": {"id": 1, "name": "Dogs"},
        "photoUrls": ["string"],
        "tags": [{"id": 0, "name": "string"}],
        "status": "available"
    }
    create_response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    coverage.record_test_result("POST /pet", create_response.status_code)
    assert create_response.status_code == 200

    # Read
    read_response = requests.get(f"{BASE_URL}/pet/{pet_data['id']}")
    coverage.record_test_result("GET /pet/{petId}", read_response.status_code)
    assert read_response.status_code == 200
    assert read_response.json()["name"] == "CRUDDog"

    # Update
    pet_data["name"] = "UpdatedCRUDDog"
    update_response = requests.put(f"{BASE_URL}/pet", json=pet_data)
    coverage.record_test_result("PUT /pet", update_response.status_code)
    assert update_response.status_code == 200

    # Verify Update
    verify_response = requests.get(f"{BASE_URL}/pet/{pet_data['id']}")
    coverage.record_test_result("GET /pet/{petId}", verify_response.status_code)
    assert verify_response.status_code == 200
    assert verify_response.json()["name"] == "UpdatedCRUDDog"

    # Delete
    delete_response = requests.delete(f"{BASE_URL}/pet/{pet_data['id']}")
    coverage.record_test_result("DELETE /pet/{petId}", delete_response.status_code)
    assert delete_response.status_code == 200

    # Verify Delete
    verify_delete = requests.get(f"{BASE_URL}/pet/{pet_data['id']}")
    coverage.record_test_result("GET /pet/{petId}", verify_delete.status_code)
    assert verify_delete.status_code == 404


def pytest_sessionfinish(session, exitstatus):
    """Вывод метрик покрытия после выполнения всех тестов"""
    metrics = coverage.calculate_metrics()

    print("\n" + "=" * 50)
    print("               API COVERAGE REPORT                ")
    print("=" * 50 + "\n")

    print(f"1. Среднее покрытие эндпоинтов раздела Pet: {metrics['avg_endpoint_coverage']:.1f}%")
    print(f"2. Покрытие статус-кодов раздела Pet: {metrics['pet_status_coverage']:.1f}%")
    print(f"3. Полностью покрытые эндпоинты API: {metrics['full_endpoint_coverage']:.1f}%")
    print(f"4. Общее покрытие статус-кодов API: {metrics['total_api_coverage']:.1f}%\n")

    print("Детали по endpoint'ам:")
    for endpoint in PET_ENDPOINTS:
        if endpoint in coverage.coverage_data:
            data = coverage.coverage_data[endpoint]
            tested = len(data["tested"])
            expected = len(data["status_codes"])
            ratio = (tested / expected * 100) if expected > 0 else 0
            tested_str = ", ".join(f"'{code}'" for code in data["tested"])
            expected_str = ", ".join(f"'{code}'" for code in data["status_codes"])
            print(f"{endpoint}: {tested}/{expected} ({ratio:.1f}%) ------> [{tested_str}] / [{expected_str}]")

    print("\n" + "=" * 50)
