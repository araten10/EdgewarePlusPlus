import asyncio
import time
from threading import Thread

from config.settings import Settings
from config.vars import Vars
from buttplug import Client, WebsocketConnector, ProtocolSpec

class Sextoy:
    def __init__(self, settings: Settings | Vars):
        self.connected = False
        self._settings = settings
        self._command_timeout = 2.0

        # 1) Create and start the background asyncio event loop
        self._loop = asyncio.new_event_loop()
        t = Thread(target=self._run_loop, daemon=True)
        t.start()

        # 2) Prepare the buttplug client
        self._client = Client("EdgewarePP", ProtocolSpec.v3)

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
            from buttplug import Client, WebsocketConnector, ProtocolSpec
            
            raw_addr = self._settings.initface_address
            addr = raw_addr.get() if hasattr(raw_addr, "get") else raw_addr
            
            # Создаем клиент Buttplug
            self._client = Client("EdgewarePP", ProtocolSpec.v3)
            connector = WebsocketConnector(addr)
            
            # Подключаемся
            await self._client.connect(connector)
            self.connected = True
            
            # Запускаем сканирование
            await self._client.start_scanning()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def connect(self):
        if self.connected:
            print("🔌 Already connected")
            return None
        # Запускаем корутину подключения/сканирования

        raw_addr = self._settings.initface_address
        addr = raw_addr.get() if hasattr(raw_addr, "get") else raw_addr
        self._connector = WebsocketConnector(addr, logger=self._client.logger)

        return asyncio.run_coroutine_threadsafe(self._connect_and_scan(), self._loop)

    async def _connect_and_scan(self):
        # Perform handshake with Intiface server
        await self._client.connect(self._connector)
        self.connected = True

        # Launch continuous scan loop
        self._loop.create_task(self._scan_loop())

    async def _scan_loop(self, scan_duration: float = 3.0, interval: float = 2.0):
        """Continuously scan for new devices every `interval + scan_duration` seconds."""
        while self.connected:
            try:
                # start scanning
                await self._client.start_scanning()
                await asyncio.sleep(scan_duration)
                await self._client.stop_scanning()
            except Exception as e:
                print(f"⚠️ Scan error: {e}")
            # wait before next scan
            await asyncio.sleep(interval)

    @property
    def devices(self):
        """Возвращает словарь подключенных устройств"""
        return self._client.devices if self._client else {}

    def disconnect(self):
        if not self.connected:
            print("🔌 Not connected")
            return

        async def _do_disconnect():
            await self._client.disconnect()
            self.connected = False  # ← пометили что отключились

        asyncio.run_coroutine_threadsafe(_do_disconnect(), self._loop)

    def vibrate(self, device_index: int, speed: float, duration: float = 0.0):
        """
        Отправляет команду вибрации на устройство
        """
        if not self.connected or not self._client:
            print("⚠️ Not connected to Intiface server")
            return
            
        async def _vibrate_task():
            try:
                # Проверяем доступность устройства
                if device_index not in self._client.devices:
                    print(f"⚠️ Device {device_index} not found")
                    return
                    
                device = self._client.devices[device_index]
                
                # Включаем вибрацию
                start_time = time.time()
                await device.send_vibrate_cmd(speed)
                vibrate_time = time.time() - start_time
                
                # Если указана длительность, ждем и выключаем
                if duration > 0:
                    # Рассчитываем оставшееся время
                    remaining = max(0, duration - vibrate_time)
                    
                    if remaining > 0:
                        await asyncio.sleep(remaining)
                    
                    # Выключаем вибрацию
                    await device.send_vibrate_cmd(0.0)
                    
                    # Логируем общее время
                    total_time = time.time() - start_time
                    if total_time > duration * 1.1:
                        print(f"⚠️ Vibration duration exceeded: {total_time:.2f}s for requested {duration}s")
            except Exception as e:
                print(f"Vibration error for device {device_index}: {str(e)}")

        asyncio.run_coroutine_threadsafe(_vibrate_task(), self._loop)

    def list_devices(self):
        for idx, dev in self._client.devices.items():
            print(f"[{idx}] {dev} — channels: {len(dev.actuators)}")

    def vibrate_all_for(self, speed: float, duration: float = 1.5):
        """
        Vibrate all connected devices at `speed` for `duration` seconds,
        then automatically stop.
        """
        async def _pulse():
            # 1) start vibration on every device
            for dev in self._client.devices.values():
                if dev.actuators:
                    await dev.actuators[0].command(speed)
            # 2) wait the requested duration
            await asyncio.sleep(duration)
            # 3) stop vibration on every device
            for dev in self._client.devices.values():
                for act in dev.actuators:
                    await act.command(0.0)

        # schedule it on the background loop
        asyncio.run_coroutine_threadsafe(_pulse(), self._loop)

    def shutdown(self):
        """
        Correctly disconnects from Intiface and stops the event loop.
        """
        async def _do_shutdown():
            await self._client.disconnect()
            self._loop.stop()
        asyncio.run_coroutine_threadsafe(_do_shutdown(), self._loop)