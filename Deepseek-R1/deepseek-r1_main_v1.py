import pytest
import requests
from metrics import coverage

BASE_URL = "https://petstore3.swagger.io/api/v3"

@pytest.fixture(scope="session", autouse=True)
def print_coverage_report(request):
    def fin():
        metrics = coverage.calculate_metrics()
        print("\n==================================================")
        print("               API COVERAGE REPORT                ")
        print("==================================================")
        print(f"1. Среднее покрытие эндпоинтов раздела Pet: {metrics['avg_endpoint_coverage']:.1f}%")
        print(f"2. Покрытие статус-кодов раздела Pet: {metrics['pet_status_coverage']:.1f}%")
        print(f"3. Полностью покрытые эндпоинты API: {metrics['full_endpoint_coverage']:.1f}%")
        print(f"4. Общее покрытие статус-кодов API: {metrics['total_api_coverage']:.1f}%")
        print("\nДетали по endpoint'ам:")
        for endpoint, data in coverage.coverage_data.items():
            expected = data['status_codes']
            tested = data['tested']
            expected_count = len(expected)
            tested_count = len(tested)
            coverage_percent = (tested_count / expected_count * 100) if expected_count > 0 else 0.0
            tested_str = f"[{', '.join(f'''{code}''' for code in tested)}]"
            expected_str = f"[{', '.join(f'''{code}''' for code in expected)}]"
            print(f"{endpoint}: {tested_count}/{expected_count} ({coverage_percent:.1f}%) ------> {tested_str} / {expected_str}")
    request.addfinalizer(fin)

def test_create_pet_valid():
    data = {
        "id": 100,
        "name": "ValidPet",
        "category": {"id": 1, "name": "Dogs"},
        "photoUrls": ["http://example.com/image.jpg"],
        "tags": [{"id": 1, "name": "test"}],
        "status": "available"
    }
    response = requests.post(f"{BASE_URL}/pet", json=data)
    assert response.status_code == 200
    coverage.record_test_result("POST /pet", response.status_code)
    requests.delete(f"{BASE_URL}/pet/{data['id']}")

def test_create_pet_invalid():
    data = {"id": "invalid", "name": "InvalidPet", "status": "available"}
    response = requests.post(f"{BASE_URL}/pet", json=data)
    assert response.status_code in [400, 422]
    coverage.record_test_result("POST /pet", response.status_code)

def test_get_pet_valid():
    pet_id = 101
    data = {"id": pet_id, "name": "TestPet", "status": "available"}
    requests.post(f"{BASE_URL}/pet", json=data)
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200
    coverage.record_test_result("GET /pet/{petId}", response.status_code)
    requests.delete(f"{BASE_URL}/pet/{pet_id}")

def test_get_pet_not_found():
    response = requests.get(f"{BASE_URL}/pet/999999")
    assert response.status_code == 404
    coverage.record_test_result("GET /pet/{petId}", response.status_code)

def test_get_pet_invalid_id():
    response = requests.get(f"{BASE_URL}/pet/invalid_id")
    assert response.status_code == 400
    coverage.record_test_result("GET /pet/{petId}", response.status_code)

def test_update_pet_valid():
    pet_id = 102
    data = {"id": pet_id, "name": "UpdateTest", "status": "available"}
    requests.post(f"{BASE_URL}/pet", json=data)
    update_data = {"id": pet_id, "name": "UpdatedName", "status": "sold"}
    response = requests.put(f"{BASE_URL}/pet", json=update_data)
    assert response.status_code == 200
    coverage.record_test_result("PUT /pet", response.status_code)
    requests.delete(f"{BASE_URL}/pet/{pet_id}")

def test_update_pet_not_found():
    data = {"id": 999999, "name": "NonExistentPet", "status": "available"}
    response = requests.put(f"{BASE_URL}/pet", json=data)
    assert response.status_code == 404
    coverage.record_test_result("PUT /pet", response.status_code)

def test_delete_pet_valid():
    pet_id = 103
    data = {"id": pet_id, "name": "DeleteTest", "status": "available"}
    requests.post(f"{BASE_URL}/pet", json=data)
    response = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200
    coverage.record_test_result("DELETE /pet/{petId}", response.status_code)

def test_delete_pet_not_found():
    response = requests.delete(f"{BASE_URL}/pet/999999")
    assert response.status_code == 404
    coverage.record_test_result("DELETE /pet/{petId}", response.status_code)

def test_find_pets_by_status_valid():
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "available"})
    assert response.status_code == 200
    coverage.record_test_result("GET /pet/findByStatus", response.status_code)

def test_find_pets_by_status_invalid():
    response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": "invalid"})
    assert response.status_code == 400
    coverage.record_test_result("GET /pet/findByStatus", response.status_code)

def test_upload_image_valid():
    pet_id = 104
    data = {"id": pet_id, "name": "UploadTest", "status": "available"}
    requests.post(f"{BASE_URL}/pet", json=data)
    files = {"file": ("image.jpg", b"content", "image/jpeg")}
    response = requests.post(f"{BASE_URL}/pet/{pet_id}/uploadImage", files=files)
    assert response.status_code == 200
    coverage.record_test_result("POST /pet/{petId}/uploadImage", response.status_code)
    requests.delete(f"{BASE_URL}/pet/{pet_id}")

def test_upload_image_invalid_pet():
    response = requests.post(f"{BASE_URL}/pet/invalid/uploadImage", files={"file": ("image.jpg", b"content")})
    assert response.status_code == 400
    coverage.record_test_result("POST /pet/{petId}/uploadImage", response.status_code)

def test_upload_image_not_found():
    response = requests.post(f"{BASE_URL}/pet/999999/uploadImage", files={"file": ("image.jpg", b"content")})
    assert response.status_code == 404
    coverage.record_test_result("POST /pet/{petId}/uploadImage", response.status_code)

def test_upload_image_invalid_content_type():
    pet_id = 105
    data = {"id": pet_id, "name": "ContentTypeTest"}
    requests.post(f"{BASE_URL}/pet", json=data)
    files = {"file": ("test.txt", "text data", "text/plain")}
    response = requests.post(f"{BASE_URL}/pet/{pet_id}/uploadImage", files=files)
    assert response.status_code == 415
    coverage.record_test_result("POST /pet/{petId}/uploadImage", response.status_code)
    requests.delete(f"{BASE_URL}/pet/{pet_id}")

def test_pet_crud_flow():
    pet_data = {"id": 106, "name": "CRUDPet", "status": "available"}
    response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    assert response.status_code == 200
    coverage.record_test_result("POST /pet", 200)
    pet_id = pet_data["id"]

    response = requests.put(f"{BASE_URL}/pet", json={"id": pet_id, "name": "Updated", "status": "sold"})
    assert response.status_code == 200
    coverage.record_test_result("PUT /pet", 200)

    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200
    coverage.record_test_result("GET /pet/{petId}", 200)

    response = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 200
    coverage.record_test_result("DELETE /pet/{petId}", 200)

    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    assert response.status_code == 404
    coverage.record_test_result("GET /pet/{petId}", 404)
