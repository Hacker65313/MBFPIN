"""
USB AOA (Android Open Accessory) Handler - FIXED VERSION
Menangani koneksi USB ke Android device via libusb/pyusb
Support: Samsung, Sony, dan device Android lainnya

FIX: Support untuk Termux dengan backend detection yang benar
"""

import os
import sys
import time
import logging
import subprocess

# Try to import usb, handle if not available
try:
    import usb.core
    import usb.util
    import usb.backend
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False
    print("[!] PyUSB tidak terinstall. Install dengan: pip install pyusb")

# Platform detection
IS_TERMUX = "com.termux" in os.environ.get("PREFIX", "")
IS_LINUX = sys.platform.startswith("linux")
IS_WINDOWS = sys.platform.startswith("win")

logger = logging.getLogger(__name__)

# Android USB Vendor ID (Google)
GOOGLE_VID = 0x18D1
# AOA mode Product IDs
AOA_PID_LIST = [0x2D00, 0x2D01, 0x2D02, 0x2D03, 0x2D04, 0x2D05]

# Samsung Vendor ID
SAMSUNG_VID = 0x04E8

HID_ID = 1  # ID HID instance


def find_libusb_backend():
    """
    Find and return appropriate libusb backend for PyUSB
    CRITICAL: This fixes the "No backend available" error
    """
    if not USB_AVAILABLE:
        return None
    
    backend = None
    
    # Try different backend locations based on platform
    if IS_TERMUX:
        libusb_paths = [
            '/data/data/com.termux/files/usr/lib/libusb-1.0.so',
            '/data/data/com.termux/files/usr/lib/libusb-1.0.so.0',
            '/system/lib64/libusb-1.0.so',
            '/system/lib/libusb-1.0.so',
            'libusb-1.0.so',
        ]
    elif IS_LINUX:
        libusb_paths = [
            '/usr/lib/x86_64-linux-gnu/libusb-1.0.so',
            '/usr/lib/aarch64-linux-gnu/libusb-1.0.so',
            '/usr/lib/arm-linux-gnueabihf/libusb-1.0.so',
            '/usr/lib/libusb-1.0.so',
            '/usr/local/lib/libusb-1.0.so',
            'libusb-1.0.so.0',
            'libusb-1.0.so',
        ]
    elif IS_WINDOWS:
        libusb_paths = [
            'libusb-1.0.dll',
            'libusb0.dll',
            r'C:\Windows\System32\libusb-1.0.dll',
        ]
    else:
        libusb_paths = ['libusb-1.0.so', 'libusb-1.0.dll']
    
    # Try each path
    for path in libusb_paths:
        try:
            backend = usb.backend.libusb1.get_backend(find_library=lambda x: path)
            if backend:
                print(f"[+] USB backend found: {path}")
                return backend
        except Exception:
            continue
    
    # Try default discovery
    try:
        backend = usb.backend.libusb1.get_backend()
        if backend:
            print("[+] USB backend found (default)")
            return backend
    except Exception:
        pass
    
    # Try libusb0 as fallback
    try:
        backend = usb.backend.libusb0.get_backend()
        if backend:
            print("[+] USB backend found (libusb0)")
            return backend
    except Exception:
        pass
    
    print("[-] No USB backend found!")
    return None


class USBAccessory:
    """
    Kelas untuk mengelola koneksi USB AOA ke Android device
    """

    def __init__(self):
        self.device = None
        self.endpoint_out = None
        self.interface = None
        self._hid_registered = False
        self.backend = None
        
        # Setup backend saat init
        if USB_AVAILABLE:
            self.backend = find_libusb_backend()
            if self.backend is None:
                print("=" * 60)
                print("ERROR: libusb backend tidak ditemukan!")
                print("=" * 60)
                if IS_TERMUX:
                    print("Jalankan perintah berikut di Termux:")
                    print("  pkg install libusb")
                    print("  pkg install termux-api")
                    print("  pip install pyusb")
                elif IS_LINUX:
                    print("Jalankan perintah berikut:")
                    print("  sudo apt install libusb-1.0-0")
                    print("  pip install pyusb")
                print("=" * 60)

    def find_android_device(self):
        """
        Cari Android device yang terhubung via USB
        """
        if not USB_AVAILABLE:
            print("[-] PyUSB tidak tersedia!")
            return None, None
        
        if self.backend is None:
            print("[-] USB backend tidak tersedia!")
            return None, None
        
        print("[*] Mencari Android device...")
        
        # Cek apakah sudah mode AOA - PAKAI BACKEND!
        for pid in AOA_PID_LIST:
            try:
                dev = usb.core.find(idVendor=GOOGLE_VID, idProduct=pid, backend=self.backend)
                if dev is not None:
                    print(f"[+] Device sudah dalam mode AOA (PID: 0x{pid:04X})")
                    return dev, 'aoa'
            except Exception as e:
                continue

        # Cari Samsung device - PAKAI BACKEND!
        try:
            dev = usb.core.find(idVendor=SAMSUNG_VID, backend=self.backend)
            if dev is not None:
                print(f"[+] Samsung device ditemukan!")
                return dev, 'normal'
        except Exception:
            pass

        # Cari semua device dan filter - PAKAI BACKEND!
        try:
            for dev in usb.core.find(find_all=True, backend=self.backend):
                try:
                    # Check if Android device by VID
                    vid = dev.idVendor
                    # Common Android VIDs
                    android_vids = [0x04E8, 0x18D1, 0x2717, 0x12D1, 0x0BB4, 0x054C, 0x22D9, 0x19D2, 0x1BBB, 0x2A47, 0x29A9]
                    if vid in android_vids:
                        print(f"[+] Android device ditemukan (VID: 0x{vid:04X})")
                        return dev, 'normal'
                except Exception:
                    continue
        except Exception as e:
            print(f"[-] Error scanning devices: {e}")

        return None, None

    def switch_to_aoa_mode(self, device):
        """Switch Android device ke AOA mode"""
        from hid_descriptor import (
            AOA_GET_PROTOCOL, AOA_SEND_IDENT, AOA_START_ACCESSORY,
            MANUFACTURER, MODEL, DESCRIPTION, VERSION, URI, SERIAL
        )
        
        print("[*] Switching ke AOA mode...")
        
        try:
            # Get protocol version
            result = device.ctrl_transfer(0xC0, AOA_GET_PROTOCOL, 0, 0, 2)
            protocol = result[0] | (result[1] << 8)
            print(f"[+] AOA Protocol version: {protocol}")

            if protocol < 1:
                print("[-] Device tidak support AOA!")
                return False

            # Send identification strings
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
                device.ctrl_transfer(0x40, AOA_SEND_IDENT, 0, idx, data)

            time.sleep(0.1)

            # Start accessory mode
            device.ctrl_transfer(0x40, AOA_START_ACCESSORY, 0, 0, None)
            print("[*] Switching ke AOA mode, tunggu device reconnect...")
            time.sleep(3)
            return True

        except Exception as e:
            print(f"[-] Error saat switch AOA: {e}")
            return False

    def connect(self, max_retries=5):
        """Connect ke Android device"""
        if not USB_AVAILABLE:
            print("[-] PyUSB tidak terinstall!")
            print("    Install dengan: pip install pyusb")
            return False
        
        if self.backend is None:
            self.backend = find_libusb_backend()
            if self.backend is None:
                print("\n" + "=" * 60)
                print("ERROR: Tidak bisa menemukan libusb backend!")
                print("=" * 60)
                if IS_TERMUX:
                    print("\nSolusi untuk Termux:")
                    print("  1. pkg install libusb")
                    print("  2. pkg install termux-api")
                    print("  3. pip install pyusb")
                    print("  4. Install app Termux:API dari Play Store")
                elif IS_LINUX:
                    print("\nSolusi untuk Linux:")
                    print("  1. sudo apt install libusb-1.0-0")
                    print("  2. pip install pyusb")
                    print("  3. Jalankan dengan sudo")
                print("=" * 60 + "\n")
                return False
        
        for attempt in range(1, max_retries + 1):
            print(f"[*] Mencari device... (attempt {attempt}/{max_retries})")
            
            device, mode = self.find_android_device()

            if device is None:
                print("[-] Tidak ada device ditemukan, coba lagi dalam 3 detik...")
                time.sleep(3)
                continue

            if mode == 'normal':
                print("[*] Device dalam mode normal, switching ke AOA...")
                if self.switch_to_aoa_mode(device):
                    time.sleep(2)
                    continue
                else:
                    print("[-] Gagal switch ke AOA mode!")
                    return False

            elif mode == 'aoa':
                # Detach kernel driver jika perlu
                try:
                    if device.is_kernel_driver_active(0):
                        device.detach_kernel_driver(0)
                        print("[*] Kernel driver di-detach")
                except Exception:
                    pass

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
                    print("[-] Tidak menemukan endpoint OUT!")
                    return False

                self.device = device
                self.endpoint_out = ep_out
                self.interface = intf
                print("[+] Berhasil connect ke AOA device!")
                return True

        print(f"[-] Gagal connect setelah {max_retries} percobaan")
        return False

    def register_hid(self):
        """Register HID device"""
        if self.device is None:
            raise RuntimeError("Device belum terkoneksi!")
        
        from hid_descriptor import (
            AOA_REGISTER_HID, AOA_SET_HID_REPORT_DESC,
            TOUCHSCREEN_REPORT_DESC
        )

        desc = TOUCHSCREEN_REPORT_DESC
        desc_len = len(desc)

        print(f"[*] Register HID (ID={HID_ID}, desc_len={desc_len})...")

        try:
            self.device.ctrl_transfer(0x40, AOA_REGISTER_HID, HID_ID, desc_len, None)
            time.sleep(0.05)

            chunk_size = 16
            offset = 0
            while offset < desc_len:
                chunk = desc[offset:offset + chunk_size]
                self.device.ctrl_transfer(0x40, AOA_SET_HID_REPORT_DESC, HID_ID, offset, bytes(chunk))
                offset += chunk_size

            self._hid_registered = True
            print("[+] HID berhasil di-register!")
            return True

        except Exception as e:
            print(f"[-] Gagal register HID: {e}")
            return False

    def send_hid_event(self, report: bytes):
        """Kirim HID event"""
        if self.device is None:
            raise RuntimeError("Device belum terkoneksi!")
        
        from hid_descriptor import AOA_SEND_HID_EVENT
        
        try:
            self.device.ctrl_transfer(0x40, AOA_SEND_HID_EVENT, HID_ID, 0, report)
        except Exception as e:
            print(f"[-] Gagal kirim HID event: {e}")
            raise

    def unregister_hid(self):
        """Unregister HID device"""
        if self.device and self._hid_registered:
            try:
                from hid_descriptor import AOA_UNREGISTER_HID
                self.device.ctrl_transfer(0x40, AOA_UNREGISTER_HID, HID_ID, 0, None)
                print("[*] HID di-unregister")
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
        print("[*] Koneksi USB ditutup")


# ============================================
# TEST FUNCTION - Jalankan untuk test
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print("  USB BACKEND TEST")
    print("=" * 60)
    
    if not USB_AVAILABLE:
        print("[-] PyUSB tidak terinstall!")
        print("    Install dengan: pip install pyusb")
        sys.exit(1)
    
    print(f"[*] Platform: {'Termux' if IS_TERMUX else 'Linux' if IS_LINUX else 'Windows'}")
    print("[*] Mencari USB backend...")
    
    backend = find_libusb_backend()
    
    if backend is None:
        print("\n[-] FAILED: Tidak bisa menemukan libusb backend!")
        print("\nSolusi:")
        if IS_TERMUX:
            print("  pkg install libusb")
            print("  pkg install termux-api")
            print("  pip install pyusb")
        elif IS_LINUX:
            print("  sudo apt install libusb-1.0-0")
            print("  pip install pyusb")
        sys.exit(1)
    
    print("\n[+] SUCCESS: USB backend ditemukan!")
    
    # Test device scan
    print("\n[*] Scanning USB devices...")
    try:
        devices = list(usb.core.find(find_all=True, backend=backend))
        print(f"[+] Ditemukan {len(devices)} USB device(s)")
        
        for dev in devices:
            try:
                vid = dev.idVendor
                pid = dev.idProduct
                print(f"    - VID:0x{vid:04X} PID:0x{pid:04X}")
            except Exception:
                pass
    except Exception as e:
        print(f"[-] Error scanning: {e}")
    
    print("\n" + "=" * 60)
    print("  TEST SELESAI")
    print("=" * 60)