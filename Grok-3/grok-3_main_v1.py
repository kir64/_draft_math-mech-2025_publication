import pytest
import requests
import json
from metrics import coverage

BASE_URL = "https://petstore3.swagger.io/api/v3"

@pytest.fixture
def pet_data():
    return {
        "id": 9999,
        "name": "TestPet",
        "category": {"id": 1, "name": "Dogs"},
        "photoUrls": ["string"],
        "tags": [{"id": 1, "name": "tag1"}],
        "status": "available"
    }

def test_post_pet_200(pet_data):
    response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    coverage.record_test_result("POST /pet", response.status_code)
    assert response.status_code == 200
    assert response.json()["name"] == pet_data["name"]

def test_post_pet_400_invalid_body():
    invalid_data = {"id": "invalid", "name": 123}  # Invalid types
    response = requests.post(f"{BASE_URL}/pet", json=invalid_data)
    coverage.record_test_result("POST /pet", response.status_code)
    assert response.status_code == 400

def test_put_pet_200(pet_data):
    pet_data["name"] = "UpdatedPet"
    response = requests.put(f"{BASE_URL}/pet", json=pet_data)
    coverage.record_test_result("PUT /pet", response.status_code)
    assert response.status_code == 200
    assert response.json()["name"] == "UpdatedPet"

def test_put_pet_404_nonexistent():
    invalid_data = pet_data.copy()
    invalid_data["id"] = 999999999  # Non-existent ID
    response = requests.put(f"{BASE_URL}/pet", json=invalid_data)
    coverage.record_test_result("PUT /pet", response.status_code)
    assert response.status_code == 404

def test_get_pet_by_status_200():
    response = requests.get(f"{BASE_URL}/pet/findByStatus?status=available")
    coverage.record_test_result("GET /pet/findByStatus", response.status_code)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_pet_by_status_400_invalid():
    response = requests.get(f"{BASE_URL}/pet/findByStatus?status=invalid")
    coverage.record_test_result("GET /pet/findByStatus", response.status_code)
    assert response.status_code == 400

def test_get_pet_by_tags_200():
    response = requests.get(f"{BASE_URL}/pet/findByTags?tags=tag1")
    coverage.record_test_result("GET /pet/findByTags", response.status_code)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_pet_by_id_200(pet_data):
    # First create pet
    requests.post(f"{BASE_URL}/pet", json=pet_data)
    response = requests.get(f"{BASE_URL}/pet/{pet_data['id']}")
    coverage.record_test_result("GET /pet/{petId}", response.status_code)
    assert response.status_code == 200
    assert response.json()["id"] == pet_data["id"]

def test_get_pet_by_id_404():
    response = requests.get(f"{BASE_URL}/pet/999999999")
    coverage.record_test_result("GET /pet/{petId}", response.status_code)
    assert response.status_code == 404

def test_post_pet_id_400_invalid(pet_data):
    # First create pet
    requests.post(f"{BASE_URL}/pet", json=pet_data)
    invalid_data = {"name": 123}  # Invalid type
    response = requests.post(f"{BASE_URL}/pet/{pet_data['id']}", data=invalid_data)
    coverage.record_test_result("POST /pet/{petId}", response.status_code)
    assert response.status_code == 400

def test_delete_pet_200(pet_data):
    # First create pet
    requests.post(f"{BASE_URL}/pet", json=pet_data)
    response = requests.delete(f"{BASE_URL}/pet/{pet_data['id']}")
    coverage.record_test_result("DELETE /pet/{petId}", response.status_code)
    assert response.status_code == 200

def test_upload_image_415(pet_data):
    # First create pet
    requests.post(f"{BASE_URL}/pet", json=pet_data)
    # Sending invalid content type
    response = requests.post(f"{BASE_URL}/pet/{pet_data['id']}/uploadImage", data="invalid")
    coverage.record_test_result("POST /pet/{petId}/uploadImage", response.status_code)
    assert response.status_code == 415

def test_end_to_end_crud():
    # Create
    pet_data = {
        "id": 9998,
        "name": "CrudPet",
        "category": {"id": 1, "name": "Cats"},
        "photoUrls": ["string"],
        "tags": [{"id": 1, "name": "tag1"}],
        "status": "available"
    }
    create_response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    coverage.record_test_result("POST /pet", create_response.status_code)
    assert create_response.status_code == 200

    # Read
    read_response = requests.get(f"{BASE_URL}/pet/{pet_data['id']}")
    coverage.record_test_result("GET /pet/{petId}", read_response.status_code)
    assert read_response.status_code == 200
    assert read_response.json()["name"] == pet_data["name"]

    # Update
    pet_data["name"] = "UpdatedCrudPet"
    update_response = requests.put(f"{BASE_URL}/pet", json=pet_data)
    coverage.record_test_result("PUT /pet", update_response.status_code)
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "UpdatedCrudPet"

    # Delete
    delete_response = requests.delete(f"{BASE_URL}/pet/{pet_data['id']}")
    coverage.record_test_result("DELETE /pet/{petId}", delete_response.status_code)
    assert delete_response.status_code == 200

def teardown_module():
    metrics = coverage.calculate_metrics()
    print("\n==================================================")
    print("               API COVERAGE REPORT                ")
    print("==================================================\n")
    print(f"1. Среднее покрытие эндпоинтов раздела Pet: {metrics['avg_endpoint_coverage']:.1f}%")
    print(f"2. Покрытие статус-кодов раздела Pet: {metrics['pet_status_coverage']:.1f}%")
    print(f"3. Полностью покрытые эндпоинты API: {metrics['full_endpoint_coverage']:.1f}%")
    print(f"4. Общее покрытие статус-кодов API: {metrics['total_api_coverage']:.1f}%\n")
    print("Детали по endpoint'ам:")
    for endpoint, data in coverage.coverage_data.items():
        tested = data['tested']
        expected = data['status_codes']
        ratio = len(tested) / len(expected) * 100 if expected else 0
        print(f"{endpoint}: {len(tested)}/{len(expected)} ({ratio:.1f}%) ------> {tested} / {expected}")
