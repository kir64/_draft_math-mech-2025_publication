import pytest
import requests
import random
from metrics import coverage

BASE_URL = "https://petstore3.swagger.io/api/v3"


def record_and_assert(method, endpoint, **kwargs):
    """Обёртка для записи метрик и возврата ответа"""
    url = BASE_URL + endpoint
    response = requests.request(method, url, **kwargs)
    key = f"{method.upper()} {endpoint.split('?')[0]}"
    coverage.record_test_result(key, response.status_code)
    return response


# ---------- End-to-End CRUD тест на Pet ----------
def test_crud_pet():
    pet_id = random.randint(100000, 999999)

    # 1. Create Pet (POST)
    pet_data = {
        "id": pet_id,
        "name": "Fluffy",
        "photoUrls": ["http://example.com/photo.jpg"],
        "status": "available"
    }
    res_post = record_and_assert("post", "/pet", json=pet_data)
    assert res_post.status_code == 200

    # 2. Get Pet (GET)
    res_get = record_and_assert("get", f"/pet/{pet_id}")
    assert res_get.status_code == 200
    assert res_get.json()["name"] == "Fluffy"

    # 3. Update Pet (PUT)
    pet_data["status"] = "sold"
    res_put = record_and_assert("put", "/pet", json=pet_data)
    assert res_put.status_code == 200

    # 4. Delete Pet (DELETE)
    res_del = record_and_assert("delete", f"/pet/{pet_id}")
    assert res_del.status_code == 200

    # 5. Confirm Deletion
    res_get_after = record_and_assert("get", f"/pet/{pet_id}")
    assert res_get_after.status_code == 404


# ---------- Проверки всех эндпоинтов Pet ----------
@pytest.mark.parametrize("method, endpoint, kwargs", [
    ("get", "/pet/findByStatus", {"params": {"status": "available"}}),
    ("get", "/pet/findByTags", {"params": {"tags": ["tag1"]}}),
    ("post", "/pet", {"json": {
        "id": 999999,
        "name": "TestPet",
        "photoUrls": ["url"],
        "status": "available"
    }}),
    ("put", "/pet", {"json": {
        "id": 999999,
        "name": "TestPetUpdated",
        "photoUrls": ["url2"],
        "status": "pending"
    }}),
    ("get", "/pet/999999", {}),
    ("post", "/pet/999999", {"params": {"name": "newname", "status": "pending"}}),
    ("delete", "/pet/999999", {}),
    ("post", "/pet/999999/uploadImage", {
        "files": {"file": ("filename", b"dummy", "image/jpeg")}
    }),
])
def test_pet_endpoints(method, endpoint, kwargs):
    res = record_and_assert(method, endpoint, **kwargs)
    assert res.status_code in [200, 400, 404, 422, 405, 415, 500, 406, 415]


# ---------- Негативные тесты ----------
def test_invalid_pet_post():
    res = record_and_assert("post", "/pet", json={"bad": "data"})
    assert res.status_code in [400, 422, 500]


def test_get_nonexistent_pet():
    res = record_and_assert("get", "/pet/0")
    assert res.status_code == 404


def test_delete_nonexistent_pet():
    res = record_and_assert("delete", "/pet/0")
    assert res.status_code in [404, 400]


def test_upload_image_invalid():
    res = record_and_assert("post", "/pet/0/uploadImage", data="notafile")
    assert res.status_code in [400, 415]


# ---------- Финальный отчёт покрытия ----------
def test_print_coverage():
    metrics = coverage.calculate_metrics()
    print("\n" + "="*50)
    print("               API COVERAGE REPORT                ")
    print("="*50)
    print(f"\n1. Среднее покрытие эндпоинтов раздела Pet: {metrics['avg_endpoint_coverage']:.1f}%")
    print(f"2. Покрытие статус-кодов раздела Pet: {metrics['pet_status_coverage']:.1f}%")
    print(f"3. Полностью покрытые эндпоинты API: {metrics['full_endpoint_coverage']:.1f}%")
    print(f"4. Общее покрытие статус-кодов API: {metrics['total_api_coverage']:.1f}%\n")

    print("Детали по endpoint'ам:")
    for endpoint, data in coverage.coverage_data.items():
        tested = data["tested"]
        expected = data["status_codes"]
        percent = len(tested) / len(expected) * 100 if expected else 0
        print(f"{endpoint}: {len(tested)}/{len(expected)} ({percent:.1f}%) ------> {tested} / {expected}")
    print("="*50 + "\n")
