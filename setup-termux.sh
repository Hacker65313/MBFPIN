#!/bin/bash
#
# ╔════════════════════════════════════════════════════════════════════╗
# ║     SAMSUNG ANDROID PIN BRUTEFORCE - TERMUX SETUP SCRIPT          ║
# ║     Install dependencies untuk Termux (Android)                   ║
# ╚════════════════════════════════════════════════════════════════════╝
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
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║     SAMSUNG PIN BRUTEFORCE - TERMUX SETUP                         ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
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

# libusb for USB access
echo -e "${GREEN}[+] Installing libusb...${RESET}"
pkg install libusb -y

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

# Install pyusb
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

# Test pyusb
echo -e "${CYAN}[*] Testing pyusb...${RESET}"
python3 -c "import usb; print('pyusb version:', usb.__version__)" 2>/dev/null || {
    echo -e "${RED}[-] pyusb installation failed!${RESET}"
    echo -e "${YELLOW}[!] Try: pip install pyusb --user${RESET}"
}

# Test ADB
echo -e "${CYAN}[*] Testing ADB...${RESET}"
adb version 2>/dev/null || echo -e "${YELLOW}[!] ADB not working properly${RESET}"

# Setup USB permissions for Termux
echo -e "${CYAN}[*] Setting up USB permissions...${RESET}"
# Termux handles USB permissions automatically via termux-usb

echo ""
echo -e "${GREEN}${BOLD}╔════════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${GREEN}${BOLD}║                    ✅ SETUP SELESAI!                              ║${RESET}"
echo -e "${GREEN}${BOLD}╚════════════════════════════════════════════════════════════════════╝${RESET}"
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
echo -e "${CYAN}════════════════════════════════════════════════════════════════════${RESET}"
echo ""
echo -e "${YELLOW}📡 SETUP USB OTG (HP ke HP):${RESET}"
echo -e "  1. HP 1 (Attacker): Install Termux + jalankan tool ini"
echo -e "  2. HP 2 (Target): HP yang lupa PIN"
echo -e "  3. Sambungkan: HP 1 → USB OTG Adapter → USB Cable → HP 2"
echo -e "  4. Jalankan tool di HP 1"
echo ""
echo -e "${RED}⚠️  PERINGATAN: Gunakan HANYA pada device MILIK SENDIRI!${RESET}"
echo ""