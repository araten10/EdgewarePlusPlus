from typing import Dict, Any, Optional, Union
import random
import logging

class VibrationMixin:
    def __init__(self):
        self.active_vibrations = {}

    def trigger_vibration(self, event_type: str, settings: Dict[str, Any], sextoy: Any) -> None:
        """
        Улучшенная версия с дополнительными проверками
        """
        try:
            # Проверка наличия необходимых атрибутов
            if not self._check_sextoy_ready(sextoy):
                return
                
            if not isinstance(settings, dict):
                return

            DEFAULT_CHANCE = 0
            DEFAULT_FORCE = 50
            DEFAULT_DURATION = 0.5
            
            for device_id, device_settings in settings.items():
                try:
                    # Безопасное преобразование ID устройства
                    device_idx = self._safe_get_device_id(device_id)
                    if device_idx is None or device_idx not in sextoy.devices:
                        continue
                        
                    # Формирование ключей с проверкой
                    keys = {
                        'chance': f"sextoy_{event_type}_chance",
                        'force': f"sextoy_{event_type}_vibration_force",
                        'duration': f"sextoy_{event_type}_vibration_length"
                    }
                    
                    # Получение параметров с проверкой типов
                    chance = self._get_valid_value(device_settings, keys['chance'], DEFAULT_CHANCE, (int, float))
                    force_pct = self._get_valid_value(device_settings, keys['force'], DEFAULT_FORCE, (int, float))
                    duration = self._get_valid_value(device_settings, keys['duration'], DEFAULT_DURATION, (int, float))
                    
                    # Проверка шанса
                    if chance <= 0 or random.randint(1, 100) > chance:
                        continue

                    logging.info(f'Device id {device_idx}')
                    logging.info(f'Must vibrate for {duration} seconds')
                        
                    # Нормализация параметров
                    force = self._normalize_force(force_pct, device_settings)

                    duration = max(0.1, min(10.0, float(duration)))
                    
                    # Вызов вибрации
                    sextoy.vibrate(device_idx, force, duration)
                    
                except Exception as e:
                    print(f"Device {device_id} vibration error: {str(e)}")
                    
        except Exception as e:
            print(f"Vibration system error: {str(e)}")

    def start_continuous_vibration(self, event_type: str, settings: Dict[str, Any], sextoy: Any) -> None:
        """
        Запускает постоянную вибрацию для указанного типа события
        """
        try:
            # Проверка наличия необходимых атрибутов
            if not self._check_sextoy_ready(sextoy):
                return
                
            if not isinstance(settings, dict):
                return

            # Инициализируем словарь для этого типа событий
            self.active_vibrations.setdefault(event_type, {})
            
            for device_id, device_settings in settings.items():
                try:
                    # Проверяем, включена ли вибрация для этого события
                    enabled_key = f"sextoy_{event_type}_enabled"
                    force_key = f"sextoy_{event_type}_vibration_force"
                    
                    # Получаем значения с проверкой типа
                    enabled = self._get_valid_value(device_settings, enabled_key, False, (bool, int, str))
                    force_pct = self._get_valid_value(device_settings, force_key, 0, (int, float))
                    
                    # Преобразуем enabled в bool
                    enabled = self._normalize_bool(enabled)
                    
                    # Пропускаем если не включено или сила 0
                    if not enabled or force_pct <= 0:
                        continue
                        
                    # Безопасное преобразование ID устройства
                    device_idx = self._safe_get_device_id(device_id)
                    if device_idx is None or device_idx not in sextoy.devices:
                        continue
                        
                    # Нормализация параметров
                    force = self._normalize_force(force_pct, device_settings)
                    
                    # Запускаем постоянную вибрацию (duration=0)
                    sextoy.start_vibration(device_idx, force)
                    
                    # Сохраняем информацию о активной вибрации
                    self.active_vibrations[event_type][device_idx] = True
                    
                except Exception as e:
                    print(f"Continuous vibration start error for {event_type}, device {device_id}: {str(e)}")
                    
        except Exception as e:
            print(f"Continuous vibration system error for {event_type}: {str(e)}")

    def stop_continuous_vibration(self, event_type: str, sextoy: Any) -> None:
        """
        Останавливает постоянную вибрацию для указанного типа события
        """
        try:
            # Проверяем, есть ли активные вибрации для этого типа события
            if not self.active_vibrations.get(event_type):
                return
                
            # Проверка наличия необходимых атрибутов
            if not self._check_sextoy_ready(sextoy, require_devices=False):
                return
                
            for device_idx in list(self.active_vibrations[event_type]):
                try:
                    sextoy.stop_vibration(device_idx)
                except Exception as e:
                    logging.error(f"Error stopping continuous vib {event_type}/{device_idx}: {e}")
            
            # Удаляем запись о активных вибрациях
            self.active_vibrations.pop(event_type, None)
            
        except Exception as e:
            print(f"Continuous vibration stop system error for {event_type}: {str(e)}")

    def _check_sextoy_ready(self, sextoy: Any, require_devices: bool = True) -> bool:
        """Проверяет готовность секс-игрушки к использованию"""
        if not all(hasattr(sextoy, attr) for attr in ['connected', 'devices', 'vibrate']):
            return False
            
        if not sextoy.connected:
            return False
            
        if require_devices and not sextoy.devices:
            return False
            
        return True

    def _safe_get_device_id(self, device_id: str) -> Optional[int]:
        """Безопасное преобразование ID устройства"""
        try:
            return int(device_id.strip())
        except (ValueError, TypeError, AttributeError):
            return None

    def _get_valid_value(self, settings: Dict[str, Any], key: str, default: Any, valid_types: tuple) -> Any:
        """Получение значения с проверкой типа"""
        try:
            value = settings.get(key, default)
            return value if isinstance(value, valid_types) else default
        except (AttributeError, TypeError):
            return default
        
    def _get_general_limit(self, device_settings: Dict[str, Any]) -> float:
        """Получает общее ограничение мощности из настроек устройства"""
        # Значение по умолчанию 100% (без ограничения)
        default = 100.0
        try:
            # Пытаемся получить значение ограничения
            limit = device_settings.get('sextoy_general_vibration_force', default)
            
            # Приводим к float с проверкой
            return float(limit) if isinstance(limit, (int, float, str)) else default
        except (TypeError, ValueError):
            return default
    
    def _normalize_force(self, force_pct: Union[int, float], settings: Dict[str, Any]) -> float:
        """Нормализует силу вибрации (0-100% → 0.0-1.0)"""
        normalized = max(0.0, min(1.0, float(force_pct) / 100.0))

        normalized_general_limit = max(0.0, min(1.0, float(self._get_general_limit(settings)) / 100.0))

        return round(normalized_general_limit * normalized, 2)
    
    def _normalize_bool(self, value: Any) -> bool:
        """Преобразует значение в bool"""
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'y', 'on']
        if isinstance(value, int):
            return bool(value)
        if isinstance(value, bool):
            return value
        return False