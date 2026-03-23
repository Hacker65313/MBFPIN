#!/usr/bin/env python3
"""
USB Device Detector - Cross Platform
Mendeteksi device Android yang terhubung via USB
Support: Termux (Android OTG), Linux, Windows CMD

Fitur:
- Auto-detect USB device connection
- ADB connection check
- Device info display
- Cross-platform support
"""

import os
import sys
import subprocess
import platform
import time
import re
from typing import Optional, Dict, Tuple, List

# ANSI Color Codes
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
RED     = "\033[91m"
CYAN    = "\033[96m"
WHITE   = "\033[97m"
MAGENTA = "\033[95m"
RESET   = "\033[0m"
BOLD    = "\033[1m"
BLINK   = "\033[5m"

# Platform detection
IS_TERMUX = "com.termux" in os.environ.get("PREFIX", "")
IS_LINUX = sys.platform.startswith("linux")
IS_WINDOWS = sys.platform.startswith("win")
PLATFORM_NAME = "Termux" if IS_TERMUX else ("Windows" if IS_WINDOWS else "Linux")


def print_banner():
    """Tampilkan banner tool"""
    banner = f"""{GREEN}{BOLD}
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║    ██████╗ ███████╗███████╗████████╗ ██████╗ ██████╗ ███████╗     ║
║    ██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔═══██╗██╔════╝     ║
║    ██║  ██║█████╗  █████╗     ██║   ██║     ██║   ██║███████╗     ║
║    ██║  ██║██╔══╝  ██╔══╝     ██║   ██║     ██║   ██║╚════██║     ║
║    ██████╔╝███████╗███████╗   ██║   ╚██████╗╚██████╔╝███████║     ║
║    ╚═════╝ ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═════╝ ╚══════╝     ║
║                                                                    ║
║         USB Device Detector - Cross Platform                      ║
║         Platform: {PLATFORM_NAME:<43} ║
║                                                                    ║
║  🔌 Detect USB Device | 📱 Check ADB Connection | ℹ️ Show Info    ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
{RESET}{CYAN}
  Author  : MasJawa
  IG      : fendipendol65
{RESET}"""
    print(banner)


def run_command(cmd: List[str], timeout: int = 10) -> Tuple[int, str, str]:
    """
    Jalankan command dan return (returncode, stdout, stderr)
    Cross-platform support
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Command timeout"
    except FileNotFoundError:
        return -2, "", "Command not found"
    except Exception as e:
        return -3, "", str(e)


def check_adb_installed() -> Tuple[bool, str]:
    """
    Cek apakah ADB terinstall
    Return: (is_installed, version)
    """
    returncode, stdout, stderr = run_command(["adb", "version"])
    if returncode == 0 and stdout:
        # Parse version
        match = re.search(r"Android Debug Bridge version ([\d.]+)", stdout)
        if match:
            return True, match.group(1)
        return True, "unknown"
    return False, ""


def check_adb_devices() -> List[Dict[str, str]]:
    """
    Cek device yang terhubung via ADB
    Return: list of device info
    """
    devices = []
    returncode, stdout, stderr = run_command(["adb", "devices", "-l"])
    
    if returncode != 0:
        return devices
    
    lines = stdout.split("\n")
    for line in lines[1:]:  # Skip header
        if not line.strip():
            continue
        
        parts = line.split()
        if len(parts) >= 2:
            device = {
                "serial": parts[0],
                "status": parts[1],
            }
            
            # Parse additional info
            for part in parts[2:]:
                if ":" in part:
                    key, val = part.split(":", 1)
                    device[key] = val
            
            devices.append(device)
    
    return devices


def get_device_prop(serial: str, prop: str) -> str:
    """
    Ambil device property via ADB
    """
    returncode, stdout, stderr = run_command(
        ["adb", "-s", serial, "shell", "getprop", prop]
    )
    return stdout.strip() if returncode == 0 else ""


def get_device_info_adb(serial: str) -> Dict[str, str]:
    """
    Ambil informasi lengkap device via ADB
    """
    info = {
        "serial": serial,
        "model": get_device_prop(serial, "ro.product.model"),
        "manufacturer": get_device_prop(serial, "ro.product.manufacturer"),
        "brand": get_device_prop(serial, "ro.product.brand"),
        "device": get_device_prop(serial, "ro.product.device"),
        "android_version": get_device_prop(serial, "ro.build.version.release"),
        "sdk_version": get_device_prop(serial, "ro.build.version.sdk"),
        "build_id": get_device_prop(serial, "ro.build.id"),
        "fingerprint": get_device_prop(serial, "ro.build.fingerprint"),
        "battery": "",
    }
    
    # Get battery level
    returncode, stdout, stderr = run_command(
        ["adb", "-s", serial, "shell", "dumpsys battery | grep level"]
    )
    if returncode == 0 and stdout:
        match = re.search(r"level:\s*(\d+)", stdout)
        if match:
            info["battery"] = match.group(1) + "%"
    
    return info


def check_usb_devices_linux() -> List[Dict[str, str]]:
    """
    Cek USB devices di Linux/Termux menggunakan lsusb
    """
    devices = []
    
    # Try lsusb
    returncode, stdout, stderr = run_command(["lsusb"])
    
    if returncode == 0 and stdout:
        for line in stdout.split("\n"):
            if not line.strip():
                continue
            
            # Parse: Bus 002 Device 003: ID 04e8:6860 Samsung Electronics Co., Ltd
            match = re.match(
                r"Bus\s+(\d+)\s+Device\s+(\d+):\s+ID\s+([0-9a-f]+):([0-9a-f]+)\s+(.*)",
                line,
                re.IGNORECASE
            )
            if match:
                devices.append({
                    "bus": match.group(1),
                    "device": match.group(2),
                    "vid": match.group(3).upper(),
                    "pid": match.group(4).upper(),
                    "description": match.group(5).strip(),
                })
    
    return devices


def check_usb_devices_termux() -> List[Dict[str, str]]:
    """
    Cek USB devices di Termux menggunakan termux-usb
    """
    devices = []
    
    # Try termux-usb-list (if available)
    returncode, stdout, stderr = run_command(["termux-usb-list"])
    
    if returncode == 0 and stdout:
        for line in stdout.split("\n"):
            if line.strip():
                devices.append({
                    "path": line.strip(),
                    "type": "termux-usb"
                })
    
    # Also check lsusb if available
    lsusb_devices = check_usb_devices_linux()
    devices.extend(lsusb_devices)
    
    return devices


def check_usb_devices_windows() -> List[Dict[str, str]]:
    """
    Cek USB devices di Windows menggunakan PowerShell/CMD
    """
    devices = []
    
    # Try PowerShell Get-PnpDevice
    ps_cmd = [
        "powershell", "-Command",
        "Get-PnpDevice -PresentOnly | Where-Object {$_.Class -eq 'USB' -or $_.FriendlyName -like '*Android*' -or $_.FriendlyName -like '*Samsung*'} | Select-Object Status, Class, FriendlyName, InstanceId"
    ]
    
    returncode, stdout, stderr = run_command(ps_cmd, timeout=30)
    
    if returncode == 0 and stdout:
        for line in stdout.split("\n"):
            if line.strip() and "USB" in line.upper() or "SAMSUNG" in line.upper() or "ANDROID" in line.upper():
                devices.append({
                    "raw": line.strip(),
                    "type": "windows-pnp"
                })
    
    # Also try WMIC
    wmic_cmd = ["wmic", "path", "Win32_USBHub", "get", "DeviceID,Description"]
    returncode, stdout, stderr = run_command(wmic_cmd, timeout=30)
    
    if returncode == 0 and stdout:
        for line in stdout.split("\n"):
            if line.strip() and "USB" in line.upper():
                devices.append({
                    "raw": line.strip(),
                    "type": "wmic"
                })
    
    return devices


def check_usb_devices() -> List[Dict[str, str]]:
    """
    Cek USB devices - Cross platform
    """
    if IS_TERMUX:
        return check_usb_devices_termux()
    elif IS_WINDOWS:
        return check_usb_devices_windows()
    else:  # Linux
        return check_usb_devices_linux()


def is_android_device(device: Dict[str, str]) -> bool:
    """
    Cek apakah device adalah Android
    """
    # Check by USB VID
    android_vids = [
        "04E8",  # Samsung
        "18D1",  # Google
        "2717",  # Xiaomi
        "12D1",  # Huawei
        "0BB4",  # HTC
        "054C",  # Sony
        "22D9",  # OPPO/OnePlus
        "19D2",  # ZTE
        "1BBB",  # Motorola
        "2A47",  # Realme
        "29A9",  # Vivo
    ]
    
    vid = device.get("vid", "").upper()
    if vid in android_vids:
        return True
    
    # Check by description
    desc = device.get("description", "").lower()
    if any(kw in desc for kw in ["samsung", "android", "galaxy", "pixel", "xiaomi", "huawei", "oneplus", "oppo"]):
        return True
    
    return False


def print_device_box(device_info: Dict[str, str], adb_info: Dict[str, str] = None):
    """
    Tampilkan info device dalam box yang keren
    """
    print(f"""
{GREEN}{BOLD}╔════════════════════════════════════════════════════════════════════╗
║                    📱 DEVICE DETECTED                              ║
╠════════════════════════════════════════════════════════════════════╣
║  Vendor         : {device_info.get('description', 'Unknown'):<43} ║
║  USB ID         : VID:{device_info.get('vid', '????')}:PID:{device_info.get('pid', '????'):<28} ║
║  Bus/Device     : {device_info.get('bus', '?')}/{device_info.get('device', '?'):<48} ║
╚════════════════════════════════════════════════════════════════════╝{RESET}""")
    
    if adb_info:
        print(f"""
{CYAN}{BOLD}╔════════════════════════════════════════════════════════════════════╗
║                    📱 ADB DEVICE INFO                              ║
╠════════════════════════════════════════════════════════════════════╣
║  Model          : {adb_info.get('model', 'N/A'):<43} ║
║  Manufacturer   : {adb_info.get('manufacturer', 'N/A'):<43} ║
║  Brand          : {adb_info.get('brand', 'N/A'):<43} ║
║  Device         : {adb_info.get('device', 'N/A'):<43} ║
║  ─────────────────────────────────────────────────────────────────  ║
║  Android        : {adb_info.get('android_version', 'N/A'):<43} ║
║  SDK Version    : {adb_info.get('sdk_version', 'N/A'):<43} ║
║  Build ID       : {adb_info.get('build_id', 'N/A'):<43} ║
║  ─────────────────────────────────────────────────────────────────  ║
║  Battery        : {adb_info.get('battery', 'N/A'):<43} ║
║  Serial         : {adb_info.get('serial', 'N/A'):<43} ║
╚════════════════════════════════════════════════════════════════════╝{RESET}""")


def print_instructions():
    """
    Tampilkan instruksi penggunaan
    """
    print(f"""
{YELLOW}{BOLD}╔════════════════════════════════════════════════════════════════════╗
║                    📋 INSTRUKSI PENGGUNAAN                         ║
╚════════════════════════════════════════════════════════════════════╝{RESET}

{CYAN}{'─'*70}{RESET}

{GREEN}{BOLD}🔧 SETUP USB OTG (Termux → Android Target):{RESET}
  
  1. Siapkan 2 HP:
     • HP 1 (Attacker): Install Termux, jalankan tool ini
     • HP 2 (Target): HP yang lupa PIN
  
  2. Sambungkan dengan kabel USB OTG:
     • HP 1 (Attacker) → USB OTG Adapter → Kabel USB → HP 2 (Target)
     • Pastikan HP 1 mendeteksi HP 2 sebagai USB device
  
  3. Di HP Target:
     • Pastikan dalam kondisi LOCK SCREEN (terkunci)
     • USB Debugging TIDAK perlu aktif
     • Jika muncul prompt "Allow USB Debugging", pilih ALLOW
  
  4. Di HP 1 (Termux):
     • Jalankan: {YELLOW}python3 src/main.py -p 4 --stealth{RESET}
     • Tool akan auto-detect device yang terhubung

{CYAN}{'─'*70}{RESET}

{GREEN}{BOLD}🔧 SETUP USB (Linux/Windows PC → Android Target):{RESET}
  
  1. Sambungkan Android ke PC via kabel USB
  
  2. Di Android:
     • Pastikan USB Debugging AKTIF (Developer Options)
     • Jika muncul prompt, pilih ALLOW
  
  3. Di PC:
     • Jalankan: {YELLOW}sudo python3 src/main.py -p 4 --stealth{RESET}
     • Atau di Windows: {YELLOW}python src\\main.py -p 4 --stealth{RESET}

{CYAN}{'─'*70}{RESET}

{GREEN}{BOLD}📋 PERINTAH TERMINAL YANG TERSEDIA:{RESET}

  {YELLOW}# Cek koneksi device{RESET}
  python3 src/main.py --test-connection
  
  {YELLOW}# Bruteforce 4-digit PIN (STEALTH MODE - rekomendasi){RESET}
  python3 src/main.py -p 4 --stealth
  
  {YELLOW}# Bruteforce 6-digit PIN{RESET}
  python3 src/main.py -p 6 --stealth
  
  {YELLOW}# Tampilkan daftar device yang didukung{RESET}
  python3 src/main.py --list-devices
  
  {YELLOW}# Reset progress (mulai dari awal){RESET}
  python3 src/main.py -p 4 --reset --stealth
  
  {YELLOW}# Test dengan PIN tertentu{RESET}
  python3 src/main.py --single-pin 1234
  
  {YELLOW}# Dry-run (simulasi tanpa device){RESET}
  python3 src/main.py -p 4 --dry-run --limit 20

{CYAN}{'─'*70}{RESET}

{GREEN}{BOLD}📋 PERINTAH ADB (jika USB Debugging aktif):{RESET}

  {YELLOW}# Cek device terkoneksi via ADB{RESET}
  adb devices
  
  {YELLOW}# Restart ADB server{RESET}
  adb kill-server && adb start-server
  
  {YELLOW}# Masuk ke shell Android{RESET}
  adb shell
  
  {YELLOW}# Ambil info device{RESET}
  adb shell getprop ro.product.model

{CYAN}{'─'*70}{RESET}

{RED}{BOLD}⚠️  PERINGATAN:{RESET}
  • Gunakan HANYA pada device MILIK SENDIRI
  • Penggunaan pada device orang lain adalah ILEGAL
  • Tool ini untuk tujuan EDUKASI dan RECOVERY

{CYAN}{'─'*70}{RESET}
""")


class DeviceDetector:
    """
    Class untuk mendeteksi dan mengelola koneksi device
    """
    
    def __init__(self):
        self.adb_installed = False
        self.adb_version = ""
        self.connected_devices = []
        self.adb_devices = []
        self.target_device = None
        
    def check_prerequisites(self) -> bool:
        """
        Cek prerequisites sebelum deteksi
        """
        print(f"\n{CYAN}[*] Memeriksa prerequisites...{RESET}")
        
        # Check ADB
        self.adb_installed, self.adb_version = check_adb_installed()
        
        if self.adb_installed:
            print(f"{GREEN}[+] ADB terinstall: version {self.adb_version}{RESET}")
        else:
            print(f"{YELLOW}[!] ADB tidak terinstall (opsional untuk beberapa fitur){RESET}")
            print(f"{YELLOW}    Install dengan: {PLATFORM_NAME} install android-tools{RESET}")
        
        # Check platform-specific requirements
        if IS_TERMUX:
            print(f"{GREEN}[+] Platform: Termux (Android OTG Mode){RESET}")
            self._check_termux_packages()
        elif IS_LINUX:
            print(f"{GREEN}[+] Platform: Linux{RESET}")
            self._check_linux_packages()
        elif IS_WINDOWS:
            print(f"{GREEN}[+] Platform: Windows{RESET}")
            self._check_windows_drivers()
        
        return True
    
    def _check_termux_packages(self):
        """Cek packages yang diperlukan di Termux"""
        packages = ["python", "libusb", "android-tools"]
        for pkg in packages:
            returncode, _, _ = run_command(["pkg", "list-installed", pkg])
            if returncode == 0:
                print(f"{GREEN}[+] Package {pkg} terinstall{RESET}")
            else:
                print(f"{YELLOW}[!] Package {pkg} belum terinstall{RESET}")
                print(f"{YELLOW}    Install dengan: pkg install {pkg}{RESET}")
    
    def _check_linux_packages(self):
        """Cek packages yang diperlukan di Linux"""
        packages = ["python3", "libusb-1.0-0", "adb"]
        for pkg in packages:
            returncode, _, _ = run_command(["which", pkg.split("-")[0]])
            if returncode == 0:
                print(f"{GREEN}[+] {pkg} tersedia{RESET}")
            else:
                print(f"{YELLOW}[!] {pkg} mungkin belum terinstall{RESET}")
                print(f"{YELLOW}    Install dengan: sudo apt install {pkg}{RESET}")
    
    def _check_windows_drivers(self):
        """Cek driver di Windows"""
        print(f"{CYAN}[*] Pastikan USB drivers untuk Android sudah terinstall{RESET}")
        print(f"{CYAN}    Download dari website manufacturer device Anda{RESET}")
    
    def scan_usb_devices(self) -> List[Dict[str, str]]:
        """
        Scan USB devices yang terhubung
        """
        print(f"\n{CYAN}[*] Scanning USB devices...{RESET}")
        
        self.connected_devices = check_usb_devices()
        
        if not self.connected_devices:
            print(f"{YELLOW}[!] Tidak ada USB device terdeteksi{RESET}")
            return []
        
        print(f"{GREEN}[+] Ditemukan {len(self.connected_devices)} USB device(s){RESET}\n")
        
        for i, device in enumerate(self.connected_devices, 1):
            vid = device.get("vid", "????")
            pid = device.get("pid", "????")
            desc = device.get("description", "Unknown")
            is_android = is_android_device(device)
            
            status = f"{GREEN}[ANDROID]{RESET}" if is_android else ""
            print(f"    [{i}] VID:{vid} PID:{pid} - {desc} {status}")
        
        return self.connected_devices
    
    def scan_adb_devices(self) -> List[Dict[str, str]]:
        """
        Scan device via ADB
        """
        if not self.adb_installed:
            print(f"{YELLOW}[!] ADB tidak terinstall, skip ADB scan{RESET}")
            return []
        
        print(f"\n{CYAN}[*] Scanning ADB devices...{RESET}")
        
        self.adb_devices = check_adb_devices()
        
        if not self.adb_devices:
            print(f"{YELLOW}[!] Tidak ada ADB device terdeteksi{RESET}")
            print(f"{YELLOW}    Pastikan USB Debugging aktif dan device authorized{RESET}")
            return []
        
        print(f"{GREEN}[+] Ditemukan {len(self.adb_devices)} ADB device(s){RESET}\n")
        
        for i, device in enumerate(self.adb_devices, 1):
            serial = device.get("serial", "unknown")
            status = device.get("status", "unknown")
            
            status_color = GREEN if status == "device" else YELLOW
            print(f"    [{i}] Serial: {serial} - Status: {status_color}{status}{RESET}")
            
            # Get detailed info if authorized
            if status == "device":
                info = get_device_info_adb(serial)
                print(f"        Model: {info.get('model', 'N/A')}")
                print(f"        Android: {info.get('android_version', 'N/A')}")
                print(f"        Battery: {info.get('battery', 'N/A')}")
        
        return self.adb_devices
    
    def select_target(self) -> Optional[Dict[str, str]]:
        """
        Pilih target device untuk bruteforce
        """
        print(f"\n{CYAN}[*] Memilih target device...{RESET}")
        
        # Priority: ADB device (authorized) > USB Android device
        
        # Check ADB devices first
        for device in self.adb_devices:
            if device.get("status") == "device":
                serial = device.get("serial")
                info = get_device_info_adb(serial)
                self.target_device = {
                    "type": "adb",
                    "serial": serial,
                    "info": info,
                }
                print(f"{GREEN}[+] Target dipilih: {info.get('model', serial)} (ADB){RESET}")
                return self.target_device
        
        # Check USB Android devices
        for device in self.connected_devices:
            if is_android_device(device):
                self.target_device = {
                    "type": "usb",
                    "vid": device.get("vid"),
                    "pid": device.get("pid"),
                    "info": device,
                }
                print(f"{GREEN}[+] Target dipilih: {device.get('description', 'Unknown')} (USB){RESET}")
                return self.target_device
        
        print(f"{RED}[-] Tidak ada Android device yang bisa dijadikan target{RESET}")
        return None
    
    def wait_for_device(self, timeout: int = 60) -> bool:
        """
        Tunggu sampai device terdeteksi
        """
        print(f"\n{CYAN}[*] Menunggu device terhubung...{RESET}")
        print(f"{YELLOW}    Timeout: {timeout} detik{RESET}")
        print(f"{YELLOW}    Hubungkan device via USB sekarang...{RESET}\n")
        
        start_time = time.time()
        check_interval = 2
        
        while time.time() - start_time < timeout:
            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed
            
            # Show countdown
            sys.stdout.write(f"\r{CYAN}[*] Menunggu... {remaining} detik tersisa  {RESET}")
            sys.stdout.flush()
            
            # Check for devices
            devices = check_usb_devices()
            android_devices = [d for d in devices if is_android_device(d)]
            
            if android_devices:
                print(f"\n\n{GREEN}[+] Android device terdeteksi!{RESET}")
                return True
            
            # Also check ADB
            if self.adb_installed:
                adb_devs = check_adb_devices()
                authorized = [d for d in adb_devs if d.get("status") == "device"]
                if authorized:
                    print(f"\n\n{GREEN}[+] ADB device terdeteksi!{RESET}")
                    return True
            
            time.sleep(check_interval)
        
        print(f"\n\n{RED}[-] Timeout! Tidak ada device terdeteksi dalam {timeout} detik{RESET}")
        return False
    
    def show_device_info(self):
        """
        Tampilkan info device yang terdeteksi
        """
        if not self.target_device:
            print(f"{RED}[-] Tidak ada target device{RESET}")
            return
        
        if self.target_device["type"] == "adb":
            adb_info = self.target_device.get("info", {})
            usb_info = {
                "vid": "N/A",
                "pid": "N/A",
                "bus": "N/A",
                "device": "N/A",
                "description": adb_info.get("manufacturer", "Unknown") + " " + adb_info.get("model", ""),
            }
            print_device_box(usb_info, adb_info)
        else:
            print_device_box(self.target_device.get("info", {}))


def main():
    """Main entry point untuk device detector"""
    print_banner()
    
    detector = DeviceDetector()
    
    # Check prerequisites
    detector.check_prerequisites()
    
    # Scan USB devices
    usb_devices = detector.scan_usb_devices()
    
    # Scan ADB devices
    adb_devices = detector.scan_adb_devices()
    
    # Select target
    target = detector.select_target()
    
    # Show device info
    if target:
        detector.show_device_info()
    else:
        print(f"\n{YELLOW}[!] Tidak ada Android device terdeteksi{RESET}")
        print(f"{YELLOW}    Pastikan device terhubung via USB{RESET}")
        
        # Offer to wait for device
        print(f"\n{CYAN}[*] Tekan ENTER untuk menunggu device, atau Ctrl+C untuk keluar...{RESET}")
        try:
            input()
            if detector.wait_for_device(timeout=60):
                detector.scan_usb_devices()
                detector.scan_adb_devices()
                detector.select_target()
                if detector.target_device:
                    detector.show_device_info()
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}[*] Dibatalkan oleh user{RESET}")
    
    # Show instructions
    print_instructions()


if __name__ == "__main__":
    main()