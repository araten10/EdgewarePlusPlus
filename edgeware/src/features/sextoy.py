import asyncio
import time
from threading import Thread
import logging
import random

from typing import TypedDict
from config.settings import Settings
from config.vars import Vars
from buttplug import Client, WebsocketConnector, ProtocolSpec
from buttplug.client import Actuator

class StoredActuator(TypedDict):
    speed: float
    clockwise: bool|None

class Sextoy:
    def __init__(self, settings: Settings | Vars):
        self.connected = False
        self._settings = settings
        # Запускаем отдельный asyncio-loop
        self._loop = asyncio.new_event_loop()
        Thread(target=self._run_loop, daemon=True).start()
        self._client = Client("EdgewarePP", ProtocolSpec.v3)
        # Флаги continuous скорости
        self._continuous_forces: dict[int, float] = {}
        self._active_vibrations: dict[int, dict[int, StoredActuator]] = {}
        self._active_rotations:  dict[int, dict[int, StoredActuator]] = {}
        self.vibration_index = 0
        self.rotation_index  = 0

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    @property
    def connection_status(self):
        return "connected" if self.connected else "disconnected"

    async def connect_async(self):
        if self.connected:
            return True
        try:
            raw_addr = self._settings.initface_address
            addr = raw_addr.get() if hasattr(raw_addr, "get") else raw_addr
            self._client = Client("EdgewarePP", ProtocolSpec.v3)
            connector = WebsocketConnector(addr)
            await self._client.connect(connector)
            self.connected = True
            await self._client.start_scanning()
            return True
        except Exception as e:
            logging.error(f"Connection failed: {e}")
            return False

    def connect(self):
        if self.connected:
            logging.info("🔌 Already connected")
            return None
            
        raw_addr = self._settings.initface_address
        addr = raw_addr.get() if hasattr(raw_addr, "get") else raw_addr
        self._connector = WebsocketConnector(addr, logger=self._client.logger)
        
        # Возвращаем Future для отслеживания завершения
        return asyncio.run_coroutine_threadsafe(self._connect_and_scan(), self._loop)

    async def _connect_and_scan(self):
        try:
            await self._client.connect(self._connector)
            self.connected = True
            logging.info("✅ Successfully connected to initface")
            self._loop.create_task(self._scan_loop())
        except Exception as e:
            logging.error(f"Connection error: {e}")
            self.connected = False
            raise  # Пробрасываем исключение для обработки в Future

    async def _scan_loop(self, scan_duration=3.0, interval=2.0):
        while self.connected:
            try:
                await self._client.start_scanning()
                await asyncio.sleep(scan_duration)
                await self._client.stop_scanning()
            except Exception as e:
                logging.warning(f"⚠️ Scan error: {e}")
            await asyncio.sleep(interval)

    @property
    def devices(self):
        return self._client.devices if self._client else {}

    def disconnect(self):
        if not self.connected:
            logging.info("🔌 Not connected")
            return
        async def _do_disconnect():
            await self._client.disconnect()
            self.connected = False
        asyncio.run_coroutine_threadsafe(_do_disconnect(), self._loop)

    async def _run_actuator(
        self,
        act: Actuator,
        speed: float,
        duration: float,
        device_index: int,
        clockwise=None
    ):
        idx = act.index

        # 1) Выбираем store и session_index в зависимости от типа
        if clockwise is None:
            store       = self._active_vibrations
            session_idx = self.vibration_index
        else:
            store       = self._active_rotations
            session_idx = self.rotation_index

        # 2) Инициализация вложенных словарей
        store.setdefault(device_index, {})
        store[device_index].setdefault(session_idx, {})
        store[device_index][session_idx][idx] = {
            "act": act,
            "speed": speed,
            "clockwise": clockwise
        }

        # 3) Стартуем мотор
        cmd = act.command if clockwise is None else (lambda sp: act.command(sp, clockwise))
        t0 = time.monotonic()
        asyncio.run_coroutine_threadsafe(cmd(speed), self._loop)

        # 4) Ждём, пока duration не пройдёт
        remaining = duration - (time.monotonic() - t0)
        if remaining > 0:
            await asyncio.sleep(remaining)

        # 5) Удаляем себя из своего store
        session = store[device_index].get(session_idx, {})
        session.pop(idx, None)
        if not session:
            store[device_index].pop(session_idx, None)
        if not store[device_index]:
            store.pop(device_index, None)

        # 6) Ищем последнюю команду для данного актуатора в других сессиях
        candidate_info = None
        candidate_session_id = None
        sessions = store.get(device_index, {})
        for session_id, session_dict in sessions.items():
            if session_id == session_idx:  # пропускаем текущую сессию
                continue
            if idx in session_dict:
                info = session_dict[idx]
                if candidate_session_id is None or session_id > candidate_session_id:
                    candidate_session_id = session_id
                    candidate_info = info

        if device_index in self._continuous_forces:
            logging.info(f"vibrate_once: continuous active, skipping one-shot for {device_index}")
            return

        if candidate_info is not None:
            # Восстанавливаем команду из candidate_info
            real_act = candidate_info["act"]
            spd = candidate_info["speed"]
            cw  = candidate_info["clockwise"]
            cmd_func = real_act.command if cw is None else (lambda s, cw=cw: real_act.command(s, cw))
            logging.debug(f"Restoring actuator {idx} on device {device_index} from session {candidate_session_id} with speed {spd}")
            asyncio.run_coroutine_threadsafe(cmd_func(spd), self._loop)
        else:
            # Не нашли команд для этого актуатора - останавливаем
            logging.debug(f"Stopping actuator {idx} on device {device_index} (no active sessions)")
            if clockwise is None:
                asyncio.run_coroutine_threadsafe(act.command(0), self._loop)
            else:
                # Для ротатора направление при 0 не важно, но нужно указать
                asyncio.run_coroutine_threadsafe(act.command(0, clockwise), self._loop)


    def get_last_actuator_by_type(
        self,
        device_index: int,
        want_type: type
    ) -> dict[int, StoredActuator] | None:
        """
        Ищем в sessions для device_index в обратном insertion-order
        первую сессию, где есть actuator с типом info["clockwise"] == want_type.
        """
        sessions = self._active_vibrations.get(device_index)
        if not sessions:
            return None

        for vib_idx in reversed(sessions):
            session = sessions[vib_idx]
            filtered = {
                idx: info
                for idx, info in session.items()
                if type(info["clockwise"]) is want_type
            }
            if filtered:
                return filtered
        return None
            
    # -----------------------------------------------------------
    # Одноразовая вибрация (игнорируется при active continuous)
    async def _vibrate_once(self, device_index: int, speed: float, duration: float):
        if device_index in self._continuous_forces:
            logging.info(f"vibrate_once: continuous active, skipping one-shot for {device_index}")
            return
        dev = self._client.devices.get(device_index)
        if not dev:
            logging.warning(f"vibrate_once: device {device_index} not found")
            return
        # START с ACK
        clockwise = bool(random.getrandbits(1))

        if device_index in self._continuous_forces:
            logging.info(f"vibrate_once: continuous active at stop phase, skipping stop for {device_index}")
        else:
            # STOP с ACK
            logging.info("I AM HERE")
            
            if not dev.actuators:
                logging.info(f"No actuators to vibrate on device {device_index}")
            else:
                # START с ACK
                clockwise = bool(random.getrandbits(1))
                self.vibration_index += 1
                logging.info("I AM HERE")
                for act in dev.actuators:
                    asyncio.run_coroutine_threadsafe(
                        self._run_actuator(act, speed, duration, device_index),
                        self._loop
                    )

            # проверяем, есть ли хотя бы один ротатор
            if not dev.rotatory_actuators:
                logging.info(f"No rotatory actuators on device {device_index}")
            else:
                # используем тот же clockwise, что для вибрации (или новый, если нужно)
                self.rotation_index += 1
                for rot in dev.rotatory_actuators:
                    asyncio.run_coroutine_threadsafe(
                        self._run_actuator(rot, speed, duration, device_index, clockwise=clockwise),
                        self._loop
                    )

        logging.debug(f"vibrate_once completed: dev={device_index}, speed={speed}, duration={duration}")(f"vibrate_once completed: dev={device_index}, speed={speed}, duration={duration}")

    def vibrate(self, device_index: int, speed: float, duration: float = 1.0):
        if not self.connected:
            logging.info("vibrate: not connected, skip")
            return
        asyncio.run_coroutine_threadsafe(self._vibrate_once(device_index, speed, duration), self._loop)
                

    # -----------------------------------------------------------
    # Continuous-режим
    async def _send_continuous_start(self, device_index: int, speed: float):
        dev = self._client.devices.get(device_index)
        if not dev:
            return
        clockwise = bool(random.getrandbits(1))
        for idx, act in enumerate(dev.actuators):
            t0 = time.monotonic()
            await act.command(speed)
            logging.info(f"[ack] actuator {idx} continuous start ACK +{time.monotonic()-t0:.3f}s")
        for idx, rot in enumerate(dev.rotatory_actuators):
            t0 = time.monotonic()
            await rot.command(speed, clockwise)
            logging.info(f"[ack] rotatory {idx} continuous start ACK +{time.monotonic()-t0:.3f}s")
        logging.debug(f"Continuous started on {device_index} @ {speed}")

    def start_vibration(self, device_index: int, speed: float):
        if not self.connected:
            logging.warning("start_vibration: not connected")
            return
        if device_index in self._continuous_forces:
            logging.info(f"start_vibration: already active on {device_index}")
            return
        self._continuous_forces[device_index] = speed
        # Планируем корутину и ждём ACK
        asyncio.run_coroutine_threadsafe(
            self._send_continuous_start(device_index, speed), self._loop
        )

    async def _send_continuous_stop(self, device_index: int):
        dev = self._client.devices.get(device_index)
        if not dev:
            return
        for idx, act in enumerate(dev.actuators):
            t0 = time.monotonic()
            await act.command(0)
            logging.info(f"[ack] actuator {idx} continuous stop ACK +{time.monotonic()-t0:.3f}s")
        for idx, rot in enumerate(dev.rotatory_actuators):
            t0 = time.monotonic()
            await rot.command(0, bool(random.getrandbits(1)))
            logging.info(f"[ack] rotatory {idx} continuous stop ACK +{time.monotonic()-t0:.3f}s")
        logging.debug(f"Continuous stopped on device {device_index}")

    def stop_vibration(self, device_index: int):
        if not self.connected:
            return
        if device_index not in self._continuous_forces:
            return
        # Снимаем флаг и отправляем stop
        self._continuous_forces.pop(device_index, None)
        asyncio.run_coroutine_threadsafe(
            self._send_continuous_stop(device_index), self._loop
        )

    # -----------------------------------------------------------
    def list_devices(self):
        for idx, dev in self._client.devices.items():
            print(f"[{idx}] {dev} — channels: {len(dev.actuators)}")
