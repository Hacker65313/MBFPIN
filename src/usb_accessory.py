"""
USB AOA (Android Open Accessory) Handler
Menangani koneksi USB ke Android device via libusb/pyusb
Support: Samsung, Sony, dan device Android lainnya
Auto-detect device dengan informasi lengkap
"""

import usb.core
import usb.util
import time
import logging
from hid_descriptor import (
    AOA_GET_PROTOCOL, AOA_SEND_IDENT, AOA_START_ACCESSORY,
    AOA_REGISTER_HID, AOA_UNREGISTER_HID, AOA_SET_HID_REPORT_DESC,
    AOA_SEND_HID_EVENT,
    MANUFACTURER, MODEL, DESCRIPTION, VERSION, URI, SERIAL,
    TOUCHSCREEN_REPORT_DESC
)
from device_database import (
    SAMSUNG_DEVICES, SAMSUNG_USB_IDS, ANDROID_VENDOR_IDS,
    get_device_info, get_device_by_usb_id, get_vendor_name,
    calculate_keypad_coords, format_device_info
)

logger = logging.getLogger(__name__)

# Android USB Vendor ID (Google)
GOOGLE_VID = 0x18D1
# AOA mode Product IDs
AOA_PID_LIST = [0x2D00, 0x2D01, 0x2D02, 0x2D03, 0x2D04, 0x2D05]

# Samsung Vendor ID
SAMSUNG_VID = 0x04E8

HID_ID = 1  # ID HID instance


class DetectedDevice:
    """Class untuk menyimpan informasi device yang terdeteksi"""
    
    def __init__(self):
        self.vid = 0
        self.pid = 0
        self.vendor_name = ""
        self.model_code = None
        self.device_info = None
        self.product_name = ""
        self.manufacturer = ""
        self.serial = ""
        self.is_aoa_mode = False
    
    def __str__(self):
        if self.model_code and self.device_info:
            return format_device_info(self.model_code, self.device_info)
        else:
            return f"""
╔══════════════════════════════════════════════════════════════╗
║                    📱 DEVICE DETECTED                        ║
╠══════════════════════════════════════════════════════════════╣
║  Vendor         : {self.vendor_name:<38} ║
║  USB ID         : {f'0x{self.vid:04X}:0x{self.pid:04X}':<38} ║
║  Product        : {self.product_name[:38] if self.product_name else 'N/A':<38} ║
║  Manufacturer   : {self.manufacturer[:38] if self.manufacturer else 'N/A':<38} ║
║  Mode           : {'AOA Mode' if self.is_aoa_mode else 'Normal Mode':<38} ║
╚══════════════════════════════════════════════════════════════╝
""".strip()


class USBAccessory:
    """
    Kelas untuk mengelola koneksi USB AOA ke Android device
    Dengan auto-detect dan device info display
    """

    def __init__(self):
        self.device = None
        self.endpoint_out = None
        self.interface = None
        self._hid_registered = False
        self.detected_device = DetectedDevice()

    def _read_device_string(self, dev, idx):
        """Baca string descriptor dari device"""
        if idx is None:
            return ""
        try:
            return usb.util.get_string(dev, idx)
        except Exception:
            return ""

    def _identify_device(self, dev, is_aoa=False):
        """
        Identifikasi device dan ambil informasi lengkap
        """
        self.detected_device.vid = dev.idVendor
        self.detected_device.pid = dev.idProduct
        self.detected_device.vendor_name = get_vendor_name(dev.idVendor)
        self.detected_device.is_aoa_mode = is_aoa
        
        # Coba baca string descriptors
        try:
            self.detected_device.product_name = self._read_device_string(dev, dev.iProduct)
            self.detected_device.manufacturer = self._read_device_string(dev, dev.iManufacturer)
            self.detected_device.serial = self._read_device_string(dev, dev.iSerialNumber)
        except Exception:
            pass
        
        # Identifikasi berdasarkan USB ID
        model_code, device_info = get_device_by_usb_id(dev.idVendor, dev.idProduct)
        
        if model_code and device_info:
            self.detected_device.model_code = model_code
            self.detected_device.device_info = device_info
            logger.info(f"[+] Device teridentifikasi: {device_info['name']}")
        else:
            # Coba identifikasi dari string product
            product = self.detected_device.product_name.lower()
            manufacturer = self.detected_device.manufacturer.lower()
            
            # Check untuk Samsung A55
            if 'a55' in product or 'sm-a556' in product:
                self.detected_device.model_code = 'SM-A556B'
                self.detected_device.device_info = SAMSUNG_DEVICES.get('SM-A556B')
            elif 'samsung' in manufacturer or 'samsung' in product:
                # Generic Samsung device
                self.detected_device.model_code = 'Unknown Samsung'
                logger.info(f"[+] Samsung device terdeteksi: {self.detected_device.product_name}")
            else:
                logger.info(f"[+] Device terdeteksi: {self.detected_device.vendor_name}")

    def find_android_device(self):
        """
        Cari Android device yang terhubung via USB
        Return: (device, mode)
          mode = 'normal' | 'aoa'
        """
        # Cek apakah sudah mode AOA
        for pid in AOA_PID_LIST:
            dev = usb.core.find(idVendor=GOOGLE_VID, idProduct=pid)
            if dev is not None:
                self._identify_device(dev, is_aoa=True)
                logger.info(f"[+] Device sudah dalam mode AOA (PID: 0x{pid:04X})")
                return dev, 'aoa'

        # Cari berdasarkan known VIDs
        for vid, vendor_data in ANDROID_VENDOR_IDS.items():
            dev = usb.core.find(idVendor=vid)
            if dev is not None:
                self._identify_device(dev, is_aoa=False)
                logger.info(f"[+] Ditemukan {self.detected_device.vendor_name} device (VID: 0x{vid:04X})")
                return dev, 'normal'

        # Fallback: scan semua device, cari yang punya string "Android" atau manufacturer known
        for dev in usb.core.find(find_all=True):
            try:
                manufacturer = self._read_device_string(dev, dev.iManufacturer)
                product = self._read_device_string(dev, dev.iProduct)
                
                if manufacturer and ('android' in manufacturer.lower() or 
                                     'samsung' in manufacturer.lower()):
                    self._identify_device(dev, is_aoa=False)
                    logger.info(f"[+] Ditemukan via string: {manufacturer}")
                    return dev, 'normal'
                    
                if product and ('android' in product.lower() or 
                                'samsung' in product.lower() or
                                'galaxy' in product.lower()):
                    self._identify_device(dev, is_aoa=False)
                    logger.info(f"[+] Ditemukan via product: {product}")
                    return dev, 'normal'
            except Exception:
                pass

        return None, None

    def switch_to_aoa_mode(self, device):
        """
        Switch Android device ke AOA (Accessory) mode
        Sesuai protokol AOA 2.0
        """
        logger.info("[*] Cek protokol AOA...")

        try:
            # Step 1: Get protocol version
            result = device.ctrl_transfer(
                0xC0,           # bmRequestType: device-to-host, vendor, device
                AOA_GET_PROTOCOL,
                0, 0, 2
            )
            protocol = result[0] | (result[1] << 8)
            logger.info(f"[+] AOA Protocol version: {protocol}")

            if protocol < 1:
                logger.error("[-] Device tidak support AOA!")
                return False

            # Step 2: Kirim identification strings
            strings = [
                (0, MANUFACTURER),
                (1, MODEL),
                (2, DESCRIPTION),
                (3, VERSION),
                (4, URI),
                (5, SERIAL),
            ]
            for idx, string in strings:
                data = (string + '\0').encode('utf-8')
                device.ctrl_transfer(
                    0x40,           # host-to-device, vendor, device
                    AOA_SEND_IDENT,
                    0, idx, data
                )
                logger.debug(f"    Sent ident[{idx}]: {string}")

            time.sleep(0.1)

            # Step 3: Start accessory mode
            device.ctrl_transfer(0x40, AOA_START_ACCESSORY, 0, 0, None)
            logger.info("[*] Switching ke AOA mode, tunggu device reconnect...")
            time.sleep(3)
            return True

        except usb.core.USBError as e:
            logger.error(f"[-] USBError saat switch AOA: {e}")
            return False

    def connect(self, max_retries=5):
        """
        Connect ke Android device, switch ke AOA jika perlu
        """
        for attempt in range(1, max_retries + 1):
            logger.info(f"[*] Mencari device... (attempt {attempt}/{max_retries})")
            device, mode = self.find_android_device()

            if device is None:
                logger.warning("[-] Tidak ada device ditemukan, coba lagi dalam 3 detik...")
                time.sleep(3)
                continue

            # Tampilkan info device yang terdeteksi
            print("\n" + str(self.detected_device) + "\n")

            if mode == 'normal':
                logger.info("[*] Device dalam mode normal, switching ke AOA...")
                if self.switch_to_aoa_mode(device):
                    time.sleep(2)
                    continue  # Cari ulang setelah switch
                else:
                    logger.error("[-] Gagal switch ke AOA mode!")
                    return False

            elif mode == 'aoa':
                # Detach kernel driver jika perlu
                if device.is_kernel_driver_active(0):
                    try:
                        device.detach_kernel_driver(0)
                        logger.info("[*] Kernel driver di-detach")
                    except usb.core.USBError as e:
                        logger.warning(f"[!] Gagal detach kernel driver: {e}")

                device.set_configuration()

                # Cari endpoint
                cfg = device.get_active_configuration()
                intf = cfg[(0, 0)]

                ep_out = usb.util.find_descriptor(
                    intf,
                    custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress)
                        == usb.util.ENDPOINT_OUT
                )

                if ep_out is None:
                    logger.error("[-] Tidak menemukan endpoint OUT!")
                    return False

                self.device = device
                self.endpoint_out = ep_out
                self.interface = intf
                logger.info("[+] Berhasil connect ke AOA device!")
                return True

        logger.error(f"[-] Gagal connect setelah {max_retries} percobaan")
        return False

    def register_hid(self):
        """
        Register HID device dan kirim report descriptor
        """
        if self.device is None:
            raise RuntimeError("Device belum terkoneksi!")

        desc = TOUCHSCREEN_REPORT_DESC
        desc_len = len(desc)

        logger.info(f"[*] Register HID (ID={HID_ID}, desc_len={desc_len})...")

        try:
            # Register HID
            self.device.ctrl_transfer(
                0x40, AOA_REGISTER_HID,
                HID_ID, desc_len, None
            )
            time.sleep(0.05)

            # Kirim report descriptor (bisa dibagi beberapa paket)
            chunk_size = 16
            offset = 0
            while offset < desc_len:
                chunk = desc[offset:offset + chunk_size]
                self.device.ctrl_transfer(
                    0x40, AOA_SET_HID_REPORT_DESC,
                    HID_ID, offset, bytes(chunk)
                )
                offset += chunk_size

            self._hid_registered = True
            logger.info("[+] HID berhasil di-register!")
            time.sleep(0.1)
            return True

        except usb.core.USBError as e:
            logger.error(f"[-] Gagal register HID: {e}")
            return False

    def send_hid_event(self, report: bytes):
        """
        Kirim HID event ke device
        report: bytes payload
        """
        if self.device is None:
            raise RuntimeError("Device belum terkoneksi!")
        try:
            self.device.ctrl_transfer(
                0x40, AOA_SEND_HID_EVENT,
                HID_ID, 0, report
            )
        except usb.core.USBError as e:
            logger.error(f"[-] Gagal kirim HID event: {e}")
            raise

    def unregister_hid(self):
        """Unregister HID device"""
        if self.device and self._hid_registered:
            try:
                self.device.ctrl_transfer(
                    0x40, AOA_UNREGISTER_HID,
                    HID_ID, 0, None
                )
                logger.info("[*] HID di-unregister")
            except Exception:
                pass

    def close(self):
        """Tutup koneksi USB"""
        self.unregister_hid()
        if self.device:
            try:
                usb.util.dispose_resources(self.device)
            except Exception:
                pass
            self.device = None
        logger.info("[*] Koneksi USB ditutup")

    def get_device_keypad_coords(self):
        """
        Ambil koordinat keypad yang sesuai untuk device yang terdeteksi
        Return: dict dengan koordinat (X, Y) untuk setiap tombol
        """
        if self.detected_device.device_info:
            screen_width = self.detected_device.device_info.get('screen_width', 1080)
            screen_height = self.detected_device.device_info.get('screen_height', 2340)
            return calculate_keypad_coords(screen_width, screen_height)
        else:
            # Default coords untuk device tidak dikenal
            return calculate_keypad_coords(1080, 2340)