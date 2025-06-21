import asyncio
import time
from threading import Thread
import logging
import random

from config.settings import Settings
from config.vars import Vars
from buttplug import Client, WebsocketConnector, ProtocolSpec

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
        self._active_vibrations: dict[int, list[float]] = {}
        self.vibration_index = 0

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
            return
        raw_addr = self._settings.initface_address
        addr = raw_addr.get() if hasattr(raw_addr, "get") else raw_addr
        self._connector = WebsocketConnector(addr, logger=self._client.logger)
        asyncio.run_coroutine_threadsafe(self._connect_and_scan(), self._loop)

    async def _connect_and_scan(self):
        await self._client.connect(self._connector)
        self.connected = True
        self._loop.create_task(self._scan_loop())

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

        t_start = time.monotonic()

        for idx, act in enumerate(dev.actuators):
            t0 = time.monotonic()
            await act.command(speed)
            logging.info(f"[ack] actuator {idx} start ACK +{time.monotonic() - t0:.3f}s")

        for idx, rot in enumerate(dev.rotatory_actuators):
            t0 = time.monotonic()
            await rot.command(speed, clockwise)
            logging.info(f"[ack] rotatory {idx} start ACK +{time.monotonic() - t0:.3f}s")

        elapsed_ack_time = time.monotonic() - t_start
        adjusted_duration = max(0, duration - elapsed_ack_time)

        if adjusted_duration > 0:
            await asyncio.sleep(adjusted_duration)
            if device_index in self._continuous_forces:
                logging.info(f"vibrate_once: continuous active at stop phase, skipping stop for {device_index}")
            else:
                # STOP с ACK
                for idx, act in enumerate(dev.actuators):
                    t0 = time.monotonic()
                    task = asyncio.create_task(act.command(0))
                    while not task.done():
                        await asyncio.sleep(0.01)
                    logging.info(f"[ack] actuator {idx} stop ACK +{time.monotonic()-t0:.3f}s")
                for idx, rot in enumerate(dev.rotatory_actuators):
                    t0 = time.monotonic()
                    task = asyncio.create_task(rot.command(0, clockwise))
                    while not task.done():
                        await asyncio.sleep(0.01)
                    logging.info(f"[ack] rotatory {idx} stop ACK +{time.monotonic()-t0:.3f}s")
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
        future = asyncio.run_coroutine_threadsafe(
            self._send_continuous_start(device_index, speed), self._loop
        )
        future.result()

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
        future = asyncio.run_coroutine_threadsafe(
            self._send_continuous_stop(device_index), self._loop
        )
        future.result()

    # -----------------------------------------------------------
    def list_devices(self):
        for idx, dev in self._client.devices.items():
            print(f"[{idx}] {dev} — channels: {len(dev.actuators)}")
