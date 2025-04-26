# conftest.py
import pytest
from metrics import coverage # Импортируем экземпляр из metrics.py

def pytest_sessionfinish(session):
    """
    Хук, который выполняется после завершения всей тестовой сессии.
    Рассчитывает и выводит отчет о покрытии API.
    """
    print("\n" + "=" * 50)
    print("                API COVERAGE REPORT                 ")
    print("=" * 50 + "\n")

    metrics_results = coverage.calculate_metrics()

    print(f"1. Среднее покрытие эндпоинтов раздела Pet: {metrics_results['avg_endpoint_coverage']:.1f}%")
    print(f"2. Покрытие статус-кодов раздела Pet: {metrics_results['pet_status_coverage']:.1f}%")
    print(f"3. Полностью покрытые эндпоинты API: {metrics_results['full_endpoint_coverage']:.1f}%")
    print(f"4. Общее покрытие статус-кодов API: {metrics_results['total_api_coverage']:.1f}%")
    print("\nДетали по endpoint'ам:")

    # Сортируем эндпоинты для консистентного вывода
    sorted_endpoints = sorted(coverage.coverage_data.keys())

    for endpoint in sorted_endpoints:
        data = coverage.coverage_data[endpoint]
        expected_codes = sorted(data["status_codes"])
        tested_codes = sorted(data["tested"])
        expected_count = len(expected_codes)
        tested_count = len(tested_codes)
        coverage_percent = (tested_count / expected_count * 100) if expected_count > 0 else 0

        print(f"{endpoint}: {tested_count}/{expected_count} ({coverage_percent:.1f}%) ------> {tested_codes} / {expected_codes}")

    print("\n" + "="*25)
    # Pytest сам выведет итоги по passed/failed тестам после этого
