#!/bin/bash
#
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║     SAMSUNG ANDROID PIN BRUTEFORCE - TERMUX SETUP SCRIPT          ║
# ║     Install dependencies untuk Termux (Android)                   ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
#
# Penggunaan:
#   chmod +x setup-termux.sh
#   ./setup-termux.sh
#
# Setup untuk USB OTG (HP ke HP):
#   HP 1 (Attacker) ──► USB OTG Adapter ──► USB Cable ──► HP 2 (Target)
#

# Colors
GREEN='\033[92m'
YELLOW='\033[93m'
RED='\033[91m'
CYAN='\033[96m'
RESET='\033[0m'
BOLD='\033[1m'

echo -e "${GREEN}${BOLD}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║     SAMSUNG PIN BRUTEFORCE - TERMUX SETUP                         ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${RESET}"

# Check if running in Termux
if [ -z "$PREFIX" ] || [ ! -d "/data/data/com.termux" ]; then
    echo -e "${YELLOW}[!] Warning: Script ini untuk Termux (Android)${RESET}"
    echo -e "${YELLOW}    Untuk Linux, gunakan setup-linux.sh${RESET}"
    echo -e "${YELLOW}    Untuk Windows, gunakan setup-windows.bat${RESET}"
    echo ""
    read -p "Lanjutkan? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update packages
echo -e "${CYAN}[*] Updating packages...${RESET}"
pkg update -y && pkg upgrade -y

# Install required packages
echo -e "${CYAN}[*] Installing required packages...${RESET}"

# Python
echo -e "${GREEN}[+] Installing Python...${RESET}"
pkg install python -y

# libusb for USB access - CRITICAL for PyUSB
echo -e "${GREEN}[+] Installing libusb...${RESET}"
pkg install libusb -y

# termux-api for USB access - CRITICAL for Android USB permissions
echo -e "${GREEN}[+] Installing termux-api...${RESET}"
pkg install termux-api -y

# Android tools (ADB) - optional but recommended
echo -e "${GREEN}[+] Installing Android tools (ADB)...${RESET}"
pkg install android-tools -y

# Git for cloning
echo -e "${GREEN}[+] Installing Git...${RESET}"
pkg install git -y

# Install Python packages
echo -e "${CYAN}[*] Installing Python packages...${RESET}"

# Upgrade pip
pip install --upgrade pip

# Install pyusb - CRITICAL for USB communication
echo -e "${GREEN}[+] Installing pyusb...${RESET}"
pip install pyusb

# Create necessary directories
echo -e "${CYAN}[*] Creating directories...${RESET}"
mkdir -p logs
mkdir -p pins

# Set permissions
echo -e "${CYAN}[*] Setting permissions...${RESET}"
chmod +x src/main.py 2>/dev/null
chmod +x src/*.py 2>/dev/null

# Check if PIN files exist
if [ ! -f "pins/pins-4-digit.txt" ]; then
    echo -e "${YELLOW}[!] PIN files not found, generating...${RESET}"
    python3 src/pin_generator.py --all 2>/dev/null || echo -e "${YELLOW}[!] Could not generate PIN files${RESET}"
fi

# Test Python installation
echo -e "${CYAN}[*] Testing Python installation...${RESET}"
python3 --version

# Test libusb installation
echo -e "${CYAN}[*] Testing libusb installation...${RESET}"
if [ -f "/data/data/com.termux/files/usr/lib/libusb-1.0.so" ]; then
    echo -e "${GREEN}[+] libusb library found at /data/data/com.termux/files/usr/lib/libusb-1.0.so${RESET}"
else
    echo -e "${RED}[-] libusb library NOT found!${RESET}"
    echo -e "${YELLOW}[!] Try: pkg install libusb${RESET}"
fi

# Test pyusb with backend detection
echo -e "${CYAN}[*] Testing pyusb with backend detection...${RESET}"
python3 -c "
import sys
try:
    import usb
    print('pyusb version:', usb.__version__)
    
    import usb.backend
    
    # Try to find backend
    backend = None
    libusb_paths = [
        '/data/data/com.termux/files/usr/lib/libusb-1.0.so',
        '/data/data/com.termux/files/usr/lib/libusb-1.0.so.0',
        'libusb-1.0.so',
    ]
    
    for path in libusb_paths:
        try:
            backend = usb.backend.libusb1.get_backend(find_library=lambda x: path)
            if backend:
                print('${GREEN}[+] USB backend found at:', path, '${RESET}')
                break
        except:
            continue
    
    if not backend:
        # Try default
        backend = usb.backend.libusb1.get_backend()
        if backend:
            print('${GREEN}[+] USB backend found using default discovery${RESET}')
        else:
            print('${RED}[-] No USB backend found!${RESET}')
            print('${YELLOW}[!] Make sure libusb is installed: pkg install libusb${RESET}')
            sys.exit(1)
    
    # Try to list devices
    print('${CYAN}[*] Scanning USB devices...${RESET}')
    devices = list(usb.core.find(find_all=True, backend=backend))
    print('${GREEN}[+] Found', len(devices), 'USB device(s)${RESET}')
    
except ImportError as e:
    print('${RED}[-] pyusb installation failed:', e, '${RESET}')
    print('${YELLOW}[!] Try: pip install pyusb --user${RESET}')
    sys.exit(1)
except Exception as e:
    print('${RED}[-] Error:', e, '${RESET}')
    print('${YELLOW}[!] Make sure libusb is installed: pkg install libusb${RESET}')
    sys.exit(1)
" 2>/dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}[-] PyUSB backend test failed!${RESET}"
    echo ""
    echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${YELLOW}║                    ⚠️  TROUBLESHOOTING                                     ║${RESET}"
    echo -e "${YELLOW}╠══════════════════════════════════════════════════════════════════════════════╣${RESET}"
    echo -e "${YELLOW}║                                                                              ║${RESET}"
    echo -e "${YELLOW}║  1. Pastikan libusb terinstall:                                              ║${RESET}"
    echo -e "${YELLOW}║     pkg install libusb                                                      ║${RESET}"
    echo -e "${YELLOW}║                                                                              ║${RESET}"
    echo -e "${YELLOW}║  2. Pastikan termux-api terinstall:                                         ║${RESET}"
    echo -e "${YELLOW}║     pkg install termux-api                                                  ║${RESET}"
    echo -e "${YELLOW}║                                                                              ║${RESET}"
    echo -e "${YELLOW}║  3. Install Termux:API app dari Play Store                                  ║${RESET}"
    echo -e "${YELLOW}║                                                                              ║${RESET}"
    echo -e "${YELLOW}║  4. Berikan izin USB di pengaturan Android:                                 ║${RESET}"
    echo -e "${YELLOW}║     Settings > Apps > Termux > Permissions                                 ║${RESET}"
    echo -e "${YELLOW}║                                                                              ║${RESET}"
    echo -e "${YELLOW}║  5. Untuk akses USB OTG, jalankan:                                          ║${RESET}"
    echo -e "${YELLOW}║     termux-usb -l                                                            ║${RESET}"
    echo -e "${YELLOW}║                                                                              ║${RESET}"
    echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════════════════════╝${RESET}"
fi

# Test ADB
echo -e "${CYAN}[*] Testing ADB...${RESET}"
adb version 2>/dev/null || echo -e "${YELLOW}[!] ADB not working properly${RESET}"

# Test termux-usb
echo -e "${CYAN}[*] Testing termux-usb...${RESET}"
termux-usb -l 2>/dev/null || echo -e "${YELLOW}[!] termux-usb not working. Install Termux:API app from Play Store${RESET}"

echo ""
echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${GREEN}${BOLD}║                    ✅ SETUP SELESAI!                              ║${RESET}"
echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${CYAN}📋 PERINTAH YANG TERSEDIA:${RESET}"
echo ""
echo -e "  ${YELLOW}# Cek koneksi device${RESET}"
echo -e "  python3 src/main.py --check-connection"
echo ""
echo -e "  ${YELLOW}# Tunggu device terhubung${RESET}"
echo -e "  python3 src/main.py --wait-device"
echo ""
echo -e "  ${YELLOW}# Bruteforce 4-digit PIN (STEALTH MODE)${RESET}"
echo -e "  python3 src/main.py -p 4 --stealth"
echo ""
echo -e "  ${YELLOW}# Bruteforce 6-digit PIN${RESET}"
echo -e "  python3 src/main.py -p 6 --stealth"
echo ""
echo -e "  ${YELLOW}# Tampilkan instruksi lengkap${RESET}"
echo -e "  python3 src/main.py --instructions"
echo ""
echo -e "${CYAN}══════════════════════════════════════════════════════════════════════════${RESET}"
echo ""
echo -e "${YELLOW}📡 SETUP USB OTG (HP ke HP):${RESET}"
echo -e "  1. HP 1 (Attacker): Install Termux + jalankan tool ini"
echo -e "  2. HP 2 (Target): HP yang lupa PIN"
echo -e "  3. Sambungkan: HP 1 → USB OTG Adapter → USB Cable → HP 2"
echo -e "  4. Jalankan tool di HP 1"
echo ""
echo -e "${CYAN}══════════════════════════════════════════════════════════════════════════${RESET}"
echo ""
echo -e "${YELLOW}⚠️  PENTING UNTUK TERMUX:${RESET}"
echo -e "  1. Install app Termux:API dari Play Store"
echo -e "  2. Berikan izin USB di Settings > Apps > Termux > Permissions"
echo -e "  3. Gunakan USB OTG adapter yang kompatibel"
echo -e "  4. Pastikan HP target dalam kondisi lock screen"
echo ""
echo -e "${RED}⚠️  PERINGATAN: Gunakan HANYA pada device MILIK SENDIRI!${RESET}"
echo ""