"""
Touchscreen HID Controller
Mengatur simulasi tap/touch via HID report
Support layout keypad Samsung (4-pin & 6-pin)
Dynamic coordinate calculation berdasarkan device yang terdeteksi
"""

import time
import logging
from device_database import calculate_keypad_coords

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  Default koordinat keypad Samsung (0-10000 normalized)
#  Akan di-override berdasarkan device yang terdeteksi
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_KEYMAP = {
    #  Key : (X,    Y   )
    '1': (1700, 5800),
    '2': (5000, 5800),
    '3': (8300, 5800),
    '4': (1700, 6700),
    '5': (5000, 6700),
    '6': (8300, 6700),
    '7': (1700, 7600),
    '8': (5000, 7600),
    '9': (8300, 7600),
    '0': (5000, 8500),
    'D': (1700, 8500),    # Delete/Backspace
    'OK': (5000, 5500),   # OK popup
    'WAKE': (5000, 5000), # Wake screen
}

# ─────────────────────────────────────────────────────────────────────────────
#  Delay settings
# ─────────────────────────────────────────────────────────────────────────────

# Delay antar ketukan (ms)
DELAY_BETWEEN_KEYS   = 80    # ms
DELAY_AFTER_PIN      = 1200  # ms - tunggu animasi/response
DELAY_COOLDOWN       = 31    # detik - tunggu setelah lockout 5 percobaan
DELAY_WAKE_SCREEN    = 2000  # ms - tunggu layar nyala

# Stealth mode delays (untuk menghindari deteksi sistem)
STEALTH_DELAY_BETWEEN_KEYS = 50   # ms - lebih cepat, seperti ketikan manusia
STEALTH_DELAY_AFTER_PIN    = 800  # ms - lebih cepat dari default


def encode_position(x: int, y: int) -> bytes:
    """
    Encode koordinat X,Y ke HID report bytes (little-endian 16-bit)
    Format report: [type, xLSB, xMSB, yLSB, yMSB]
    type 0x02 = pointer move
    """
    x = max(0, min(10000, x))
    y = max(0, min(10000, y))
    x_lsb = x & 0xFF
    x_msb = (x >> 8) & 0xFF
    y_lsb = y & 0xFF
    y_msb = (y >> 8) & 0xFF
    return bytes([0x02, x_lsb, x_msb, y_lsb, y_msb])


def encode_press() -> bytes:
    """
    Encode touch press event
    0x01 = finger down (tip switch ON)
    0x00 = finger up (tip switch OFF)
    """
    return bytes([0x01, 0, 0, 0, 0])


def encode_release() -> bytes:
    """Encode touch release event"""
    return bytes([0x00, 0, 0, 0, 0])


class Touchscreen:
    """
    Kontroler touchscreen via USB HID
    Support dynamic coordinate mapping berdasarkan device
    """

    def __init__(self, accessory, keymap=None, stealth_mode=False):
        """
        Inisialisasi Touchscreen controller
        
        Args:
            accessory: USBAccessory instance
            keymap: dict koordinat keypad (opsional, akan diambil dari device info)
            stealth_mode: bool - mode tersembunyi tanpa lockout detection
        """
        self.acc = accessory
        self.current_x = 0
        self.current_y = 0
        self.stealth_mode = stealth_mode
        
        # Set keymap berdasarkan device atau gunakan default
        if keymap:
            self.keymap = keymap
        else:
            # Coba ambil dari device yang terdeteksi
            try:
                self.keymap = accessory.get_device_keypad_coords()
                logger.info("[*] Menggunakan koordinat keypad dari device database")
            except Exception:
                self.keymap = DEFAULT_KEYMAP
                logger.info("[*] Menggunakan koordinat keypad default")
        
        # Set delays berdasarkan mode
        if stealth_mode:
            self.delay_between_keys = STEALTH_DELAY_BETWEEN_KEYS
            self.delay_after_pin = STEALTH_DELAY_AFTER_PIN
        else:
            self.delay_between_keys = DELAY_BETWEEN_KEYS
            self.delay_after_pin = DELAY_AFTER_PIN

    def set_position(self, x: int, y: int):
        """Pindahkan pointer ke koordinat X,Y"""
        self.current_x = x
        self.current_y = y
        report = encode_position(x, y)
        self.acc.send_hid_event(report)
        # Kirim dua kali untuk sync (sama seperti original Go code)
        self.acc.send_hid_event(report)

    def press(self):
        """Simulasi satu tap (tekan + lepas)"""
        self.acc.send_hid_event(encode_press())
        time.sleep(0.05)
        self.acc.send_hid_event(encode_release())

    def tap(self, x: int, y: int):
        """Set posisi lalu tap"""
        self.set_position(x, y)
        time.sleep(0.03)
        self.press()

    def double_tap(self, x: int, y: int):
        """Double tap untuk wake/unlock layar"""
        self.tap(x, y)
        time.sleep(0.1)
        self.tap(x, y)

    def tap_key(self, key: str):
        """Tap tombol berdasarkan key map"""
        key = key.upper()
        if key not in self.keymap:
            logger.warning(f"[!] Key '{key}' tidak ada di keymap!")
            return
        x, y = self.keymap[key]
        logger.debug(f"    Tap '{key}' -> ({x}, {y})")
        self.tap(x, y)
        time.sleep(self.delay_between_keys / 1000.0)

    def enter_pin(self, pin: str):
        """
        Ketik PIN digit per digit
        Samsung otomatis submit setelah pin lengkap (4 atau 6 digit)
        """
        for digit in pin:
            self.tap_key(digit)

    def wake_screen(self):
        """Double tap untuk bangunkan layar / tampilkan keypad"""
        x, y = self.keymap['WAKE']
        logger.info("[*] Double tap untuk tampilkan keypad...")
        self.double_tap(x, y)
        time.sleep(DELAY_WAKE_SCREEN / 1000.0)

    def clear_pin(self):
        """Hapus input PIN dengan tap Delete beberapa kali"""
        for _ in range(6):
            self.tap_key('D')
            time.sleep(50 / 1000.0)

    def dismiss_popup(self):
        """Tap OK untuk dismiss popup 'Try again' atau sejenisnya"""
        x, y = self.keymap['OK']
        self.tap(x, y)

    def update_keymap(self, screen_width: int, screen_height: int):
        """
        Update keymap berdasarkan resolusi layar baru
        """
        self.keymap = calculate_keypad_coords(screen_width, screen_height)
        logger.info(f"[*] Keymap diupdate untuk resolusi {screen_width}x{screen_height}")

    def set_stealth_mode(self, enabled: bool):
        """
        Aktifkan/nonaktifkan stealth mode
        Stealth mode menggunakan delay yang lebih natural dan tidak terdeteksi sistem
        """
        self.stealth_mode = enabled
        if enabled:
            self.delay_between_keys = STEALTH_DELAY_BETWEEN_KEYS
            self.delay_after_pin = STEALTH_DELAY_AFTER_PIN
            logger.info("[*] Stealth mode AKTIF - delay lebih cepat dan natural")
        else:
            self.delay_between_keys = DELAY_BETWEEN_KEYS
            self.delay_after_pin = DELAY_AFTER_PIN
            logger.info("[*] Stealth mode NONAKTIF - delay standar")