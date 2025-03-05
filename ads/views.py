import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import threading
from functools import lru_cache

# Хранилище рекламных площадок в оперативной памяти
AD_PLACEMENTS = {}
AD_PLACEMENTS_LOCK = threading.Lock()  # Блокировка для потокобезопасности

@csrf_exempt  # Отключаем CSRF для простоты (в production нужно настроить правильно!)
def upload_ads(request):
    """
    Загружает рекламные площадки из JSON файла.
    Полностью перезаписывает существующие данные.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))

            # Проверка входных данных
            if not isinstance(data, list):
                return JsonResponse({'status': 'error', 'message': 'Неверный формат JSON: Ожидался список.'}, status=400)

            for item in data:
                if not isinstance(item, dict):
                    return JsonResponse({'status': 'error', 'message': 'Неверный формат JSON: Каждый элемент должен быть словарем.'}, status=400)
                if 'location' not in item or not isinstance(item['location'], str):
                    return JsonResponse({'status': 'error', 'message': 'Неверный формат JSON: Каждый элемент должен содержать ключ "location" со строковым значением.'}, status=400)

            with AD_PLACEMENTS_LOCK:
                global AD_PLACEMENTS
                AD_PLACEMENTS = {}
                for item in data:
                    location = item['location']
                    if location not in AD_PLACEMENTS:
                        AD_PLACEMENTS[location] = []
                    AD_PLACEMENTS[location].append(item)
            clear_location_cache()  # Очистка кэша после загрузки новых данных
            return JsonResponse({'status': 'success', 'message': 'Рекламные площадки успешно загружены.'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Неверный формат JSON.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Произошла ошибка: {str(e)}'}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Разрешены только POST запросы.'}, status=405)

@lru_cache(maxsize=128)  # Включаем кэширование для поиска по локациям
def get_ads_by_location_cached(location):
    """
    Возвращает рекламные площадки для заданной локации.
    Использует кэширование для ускорения ответа.
    """
    with AD_PLACEMENTS_LOCK:
        if location in AD_PLACEMENTS:
            return AD_PLACEMENTS[location]
        else:
            return []


def get_ads_by_location(request, location):
    """
    Возвращает рекламные площадки для заданной локации.
    """
    if request.method == 'GET':
        try:
            ads = get_ads_by_location_cached(location)
            return JsonResponse({'location': location, 'ads': ads})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Произошла ошибка: {str(e)}'}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Разрешены только GET запросы.'}, status=405)


def clear_location_cache():
    """Очищает кэш для поиска по локациям."""
    get_ads_by_location_cached.cache_clear()
