import pytest
import requests
from metrics import coverage
import json

BASE_URL = "https://petstore3.swagger.io/api/v3"

def load_openapi_spec():
    """Загружает OpenAPI спецификацию."""
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке спецификации: {e}")
        return None

openapi_spec = load_openapi_spec()

def get_expected_status_codes(method: str, path: str):
    """Извлекает ожидаемые статус-коды из спецификации для заданного метода и пути."""
    if openapi_spec and "paths" in openapi_spec and path in openapi_spec["paths"]:
        path_data = openapi_spec["paths"][path]
        method_lower = method.lower()
        if method_lower in path_data and "responses" in path_data[method_lower]:
            return [code for code in path_data[method_lower]["responses"].keys()]
    return []

# Вспомогательные функции для работы с API
def create_pet(payload):
    return requests.post(f"{BASE_URL}/pet", json=payload)

def get_pet(pet_id):
    return requests.get(f"{BASE_URL}/pet/{pet_id}")

def update_pet(payload):
    return requests.put(f"{BASE_URL}/pet", json=payload)

def delete_pet(pet_id):
    return requests.delete(f"{BASE_URL}/pet/{pet_id}")

def find_pets_by_status(status):
    return requests.get(f"{BASE_URL}/pet/findByStatus?status={status}")

def find_pets_by_tags(tags):
    return requests.get(f"{BASE_URL}/pet/findByTags?tags={','.join(tags)}")

def upload_pet_image(pet_id, file_path):
    with open(file_path, 'rb') as img:
        files = {'file': ('image.jpg', img, 'image/jpeg')}
        return requests.post(f"{BASE_URL}/pet/{pet_id}/uploadImage", files=files, headers={'Content-Type': 'multipart/form-data'})

# --- Тесты ---

# Пример позитивного теста
def test_add_new_pet():
    payload = {
        "id": 9223372036854775000,
        "category": {"id": 0, "name": "string"},
        "name": "doggie",
        "photoUrls": ["string"],
        "tags": [{"id": 0, "name": "string"}],
        "status": "available"
    }
    response = create_pet(payload)
    assert response.status_code == 200
    coverage.record_test_result("POST /pet", response.status_code)

# Пример теста для валидации статус-кодов
def test_get_pet_by_id_success():
    pet_id = 1
    response = get_pet(pet_id)
    assert response.status_code == 200
    coverage.record_test_result("GET /pet/{petId}", response.status_code)
    expected_statuses = get_expected_status_codes("GET", "/pet/{petId}")
    assert str(response.status_code) in expected_statuses

# Здесь будут добавлены остальные тесты

def test_pet_crud_workflow():
    # 1. Создание питомца
    create_payload = {
        "category": {"name": "test_category"},
        "name": "test_pet",
        "photoUrls": ["url1"],
        "tags": [{"name": "test_tag"}],
        "status": "available"
    }
    create_response = create_pet(create_payload)
    assert create_response.status_code == 200
    coverage.record_test_result("POST /pet", create_response.status_code)
    pet_data = create_response.json()
    pet_id = pet_data["id"]
    assert pet_id is not None

    # 2. Получение питомца
    get_response = get_pet(pet_id)
    assert get_response.status_code == 200
    coverage.record_test_result("GET /pet/{petId}", get_response.status_code)
    assert get_response.json()["name"] == "test_pet"

    # 3. Обновление питомца
    update_payload = {
        "id": pet_id,
        "name": "updated_pet",
        "status": "sold"
    }
    update_response = update_pet(update_payload)
    assert update_response.status_code == 200
    coverage.record_test_result("PUT /pet", update_response.status_code)
    assert update_response.json()["name"] == "updated_pet"

    # 4. Получение обновленного питомца
    get_updated_response = get_pet(pet_id)
    assert get_updated_response.status_code == 200
    assert get_updated_response.json()["name"] == "updated_pet"
    assert get_updated_response.json()["status"] == "sold"

    # 5. Удаление питомца
    delete_response = delete_pet(pet_id)
    assert delete_response.status_code == 200
    coverage.record_test_result("DELETE /pet/{petId}", delete_response.status_code)

    # 6. Проверка, что питомец удален
    get_deleted_response = get_pet(pet_id)
    assert get_deleted_response.status_code == 404
    coverage.record_test_result("GET /pet/{petId}", get_deleted_response.status_code)

def test_find_pets_by_status_available():
    response = find_pets_by_status("available")
    assert response.status_code == 200
    coverage.record_test_result("GET /pet/findByStatus", response.status_code)

def test_find_pets_by_tags_single():
    response = find_pets_by_tags(["test_tag"])
    assert response.status_code == 200
    coverage.record_test_result("GET /pet/findByTags", response.status_code)

def test_update_pet_with_invalid_id():
    payload = {
        "id": "invalid",
        "name": "updated_pet",
        "status": "sold"
    }
    response = update_pet(payload)
    assert response.status_code == 400 or response.status_code == 404 or response.status_code == 500 # Зависит от реализации API
    coverage.record_test_result("PUT /pet", response.status_code)

def test_get_pet_by_invalid_id():
    pet_id = "invalid"
    response = get_pet(pet_id)
    assert response.status_code == 400 or response.status_code == 404
    coverage.record_test_result("GET /pet/{petId}", response.status_code)

def test_delete_pet_by_invalid_id():
    pet_id = "invalid"
    response = delete_pet(pet_id)
    assert response.status_code == 400 or response.status_code == 404
    coverage.record_test_result("DELETE /pet/{petId}", response.status_code)

def test_add_pet_with_missing_required_field():
    payload = {
        "category": {"id": 0, "name": "string"},
        "photoUrls": ["string"],
        "tags": [{"id": 0, "name": "string"}],
        "status": "available"
    }
    response = create_pet(payload)
    assert response.status_code == 400 or response.status_code == 422 or response.status_code == 500 # Зависит от реализации API
    coverage.record_test_result("POST /pet", response.status_code)

def test_upload_image_for_nonexistent_pet():
    pet_id = 999999
    file_path = "test_image.jpg" # Создайте пустой файл test_image.jpg для теста
    try:
        with open(file_path, 'w') as f:
            f.write("test content")
        response = upload_pet_image(pet_id, file_path)
        assert response.status_code == 404
        coverage.record_test_result("POST /pet/{petId}/uploadImage", response.status_code)
    finally:
        import os
        if os.path.exists(file_path):
            os.remove(file_path)

@pytest.fixture(scope="session", autouse=True)
def final_report():
    yield
    metrics = coverage.calculate_metrics()
    print("\n==================================================")
    print("\t\t\tAPI COVERAGE REPORT\t\t\t")
    print("==================================================")
    print(f"1. Среднее покрытие эндпоинтов раздела Pet: {metrics['avg_endpoint_coverage']:.1f}%")
    print(f"2. Покрытие статус-кодов раздела Pet: {metrics['pet_status_coverage']:.1f}%")
    print(f"3. Полностью покрытые эндпоинты API: {metrics['full_endpoint_coverage']:.1f}%")
    print(f"4. Общее покрытие статус-кодов API: {metrics['total_api_coverage']:.1f}%")
    print("\nДетали по endpoint'ам:")
    for endpoint, data in coverage.coverage_data.items():
        expected_count = len(data["status_codes"])
        tested_count = len(data["tested"])
        coverage_percent = (tested_count / expected_count * 100) if expected_count > 0 else 0.0
        print(f"{endpoint}: {tested_count}/{expected_count} ({coverage_percent:.1f}%) ------> {sorted(data['tested'])} / {sorted(data['status_codes'])}")
    print("\n=========================")
