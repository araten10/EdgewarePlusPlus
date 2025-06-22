from typing import Dict, Any, Optional, Union
import random
import logging

class VibrationMixin:
    def __init__(self):
        self.active_vibrations = {}

    def trigger_vibration(self, event_type: str, settings: Dict[str, Any], sextoy: Any) -> None:
        """
        Enhanced version with additional checks
        """
        try:
            # Check that necessary attributes are present
            if not self._check_sextoy_ready(sextoy):
                return
                
            if not isinstance(settings, dict):
                return

            DEFAULT_CHANCE = 0
            DEFAULT_FORCE = 50
            DEFAULT_DURATION = 0.5
            
            for device_id, device_settings in settings.items():
                try:
                    # Safely convert device ID
                    device_idx = self._safe_get_device_id(device_id)
                    if device_idx is None or device_idx not in sextoy.devices:
                        continue
                        
                    # Construct keys with validation
                    keys = {
                        'chance': f"sextoy_{event_type}_chance",
                        'force': f"sextoy_{event_type}_vibration_force",
                        'duration': f"sextoy_{event_type}_vibration_length"
                    }
                    
                    # Get parameters with type checking
                    chance = self._get_valid_value(device_settings, keys['chance'], DEFAULT_CHANCE, (int, float))
                    force_pct = self._get_valid_value(device_settings, keys['force'], DEFAULT_FORCE, (int, float))
                    duration = self._get_valid_value(device_settings, keys['duration'], DEFAULT_DURATION, (int, float))
                    
                    # Check chance
                    if chance <= 0 or random.randint(1, 100) > chance:
                        continue

                    logging.info(f'Device id {device_idx}')
                    logging.info(f'Must vibrate for {duration} seconds')
                        
                    # Normalize parameters
                    force = self._normalize_force(force_pct, device_settings)

                    duration = max(0.1, min(10.0, float(duration)))
                    
                    # Trigger vibration
                    sextoy.vibrate(device_idx, force, duration)
                    
                except Exception as e:
                    print(f"Device {device_id} vibration error: {str(e)}")
                    
        except Exception as e:
            print(f"Vibration system error: {str(e)}")

    def start_continuous_vibration(self, event_type: str, settings: Dict[str, Any], sextoy: Any) -> None:
        """
        Starts continuous vibration for the specified event type
        """
        try:
            # Check that necessary attributes are present
            if not self._check_sextoy_ready(sextoy):
                return
                
            if not isinstance(settings, dict):
                return

            # Initialize the dictionary for this event type
            self.active_vibrations.setdefault(event_type, {})
            
            for device_id, device_settings in settings.items():
                try:
                    # Check if vibration is enabled for this event
                    enabled_key = f"sextoy_{event_type}_enabled"
                    force_key = f"sextoy_{event_type}_vibration_force"
                    
                    # Get values with type checking
                    enabled = self._get_valid_value(device_settings, enabled_key, False, (bool, int, str))
                    force_pct = self._get_valid_value(device_settings, force_key, 0, (int, float))
                    
                    # Convert enabled to bool
                    enabled = self._normalize_bool(enabled)
                    
                    # Skip if not enabled or force is zero
                    if not enabled or force_pct <= 0:
                        continue
                        
                    # Safely convert device ID
                    device_idx = self._safe_get_device_id(device_id)
                    if device_idx is None or device_idx not in sextoy.devices:
                        continue
                        
                    # Normalize parameters
                    force = self._normalize_force(force_pct, device_settings)
                    
                    # Start continuous vibration (duration=0)
                    sextoy.start_vibration(device_idx, force)
                    
                    # Record active vibration
                    self.active_vibrations[event_type][device_idx] = True
                    
                except Exception as e:
                    print(f"Continuous vibration start error for {event_type}, device {device_id}: {str(e)}")
                    
        except Exception as e:
            print(f"Continuous vibration system error for {event_type}: {str(e)}")

    def stop_continuous_vibration(self, event_type: str, sextoy: Any) -> None:
        """
        Stops continuous vibration for the specified event type
        """
        try:
            # Check if there are active vibrations for this event type
            if not self.active_vibrations.get(event_type):
                return
                
            # Verify necessary attributes without requiring devices
            if not self._check_sextoy_ready(sextoy, require_devices=False):
                return
                
            for device_idx in list(self.active_vibrations[event_type]):
                try:
                    sextoy.stop_vibration(device_idx)
                except Exception as e:
                    logging.error(f"Error stopping continuous vib {event_type}/{device_idx}: {e}")
            
            # Remove record of active vibrations
            self.active_vibrations.pop(event_type, None)
            
        except Exception as e:
            print(f"Continuous vibration stop system error for {event_type}: {str(e)}")

    def _check_sextoy_ready(self, sextoy: Any, require_devices: bool = True) -> bool:
        """Checks if the sextoy is ready for use"""
        if not all(hasattr(sextoy, attr) for attr in ['connected', 'devices', 'vibrate']):
            return False
            
        if not sextoy.connected:
            return False
            
        if require_devices and not sextoy.devices:
            return False
            
        return True

    def _safe_get_device_id(self, device_id: str) -> Optional[int]:
        """Safely convert device ID to integer"""
        try:
            return int(device_id.strip())
        except (ValueError, TypeError, AttributeError):
            return None

    def _get_valid_value(self, settings: Dict[str, Any], key: str, default: Any, valid_types: tuple) -> Any:
        """Retrieve a setting value with type validation"""
        try:
            value = settings.get(key, default)
            return value if isinstance(value, valid_types) else default
        except (AttributeError, TypeError):
            return default
        
    def _get_general_limit(self, device_settings: Dict[str, Any]) -> float:
        """Get general vibration force limit from device settings"""
        # Default to 100% (no limit)
        default = 100.0
        try:
            # Attempt to retrieve limit value
            limit = device_settings.get('sextoy_general_vibration_force', default)
            
            # Convert to float if valid
            return float(limit) if isinstance(limit, (int, float, str)) else default
        except (TypeError, ValueError):
            return default
    
    def _normalize_force(self, force_pct: Union[int, float], settings: Dict[str, Any]) -> float:
        """Normalize vibration force (0-100% → 0.0-1.0)"""
        normalized = max(0.0, min(1.0, float(force_pct) / 100.0))

        normalized_general_limit = max(0.0, min(1.0, float(self._get_general_limit(settings)) / 100.0))

        return round(normalized_general_limit * normalized, 2)
    
    def _normalize_bool(self, value: Any) -> bool:
        """Convert a value to boolean"""
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'y', 'on']
        if isinstance(value, int):
            return bool(value)
        if isinstance(value, bool):
            return value
        return False