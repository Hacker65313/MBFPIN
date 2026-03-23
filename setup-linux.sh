#!/bin/bash
#
# ╔════════════════════════════════════════════════════════════════════╗
# ║     SAMSUNG ANDROID PIN BRUTEFORCE - LINUX SETUP SCRIPT           ║
# ║     Install dependencies untuk Kali Linux / Ubuntu / Debian       ║
# ╚════════════════════════════════════════════════════════════════════╝
#
# Penggunaan:
#   chmod +x setup-linux.sh
#   ./setup-linux.sh
#
# Setup untuk USB (PC ke HP):
#   PC/Laptop ──► USB Cable ──► Android Target
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
echo "║     SAMSUNG PIN BRUTEFORCE - LINUX SETUP                          ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo -e "${RESET}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}[!] Script ini memerlukan akses root untuk beberapa operasi${RESET}"
    echo -e "${YELLOW}[!] Jalankan dengan: sudo ./setup-linux.sh${RESET}"
    echo ""
    read -p "Lanjutkan tanpa root? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Detect distribution
if [ -f /etc/debian_version ]; then
    DISTRO="debian"
    PKG_MANAGER="apt"
elif [ -f /etc/arch-release ]; then
    DISTRO="arch"
    PKG_MANAGER="pacman"
elif [ -f /etc/fedora-release ]; then
    DISTRO="fedora"
    PKG_MANAGER="dnf"
else
    DISTRO="unknown"
    PKG_MANAGER="apt"
fi

echo -e "${CYAN}[*] Detected distribution: $DISTRO${RESET}"
echo -e "${CYAN}[*] Package manager: $PKG_MANAGER${RESET}"

# Update packages
echo -e "${CYAN}[*] Updating packages...${RESET}"
case $PKG_MANAGER in
    apt)
        apt update -y && apt upgrade -y
        ;;
    pacman)
        pacman -Syu --noconfirm
        ;;
    dnf)
        dnf upgrade --refresh -y
        ;;
esac

# Install required packages
echo -e "${CYAN}[*] Installing required packages...${RESET}"

case $PKG_MANAGER in
    apt)
        # Python
        echo -e "${GREEN}[+] Installing Python...${RESET}"
        apt install -y python3 python3-pip
        
        # libusb for USB access
        echo -e "${GREEN}[+] Installing libusb...${RESET}"
        apt install -y libusb-1.0-0-dev
        
        # Android tools (ADB) - optional but recommended
        echo -e "${GREEN}[+] Installing Android tools (ADB)...${RESET}"
        apt install -y android-tools-adb android-tools-fastboot
        
        # Build essentials
        echo -e "${GREEN}[+] Installing build essentials...${RESET}"
        apt install -y build-essential
        ;;
        
    pacman)
        echo -e "${GREEN}[+] Installing Python...${RESET}"
        pacman -S --noconfirm python python-pip
        
        echo -e "${GREEN}[+] Installing libusb...${RESET}"
        pacman -S --noconfirm libusb
        
        echo -e "${GREEN}[+] Installing Android tools...${RESET}"
        pacman -S --noconfirm android-tools
        ;;
        
    dnf)
        echo -e "${GREEN}[+] Installing Python...${RESET}"
        dnf install -y python3 python3-pip
        
        echo -e "${GREEN}[+] Installing libusb...${RESET}"
        dnf install -y libusb1-devel
        
        echo -e "${GREEN}[+] Installing Android tools...${RESET}"
        dnf install -y android-tools
        ;;
esac

# Install Python packages
echo -e "${CYAN}[*] Installing Python packages...${RESET}"

# Upgrade pip
pip3 install --upgrade pip

# Install pyusb
echo -e "${GREEN}[+] Installing pyusb...${RESET}"
pip3 install pyusb

# Create necessary directories
echo -e "${CYAN}[*] Creating directories...${RESET}"
mkdir -p logs
mkdir -p pins

# Set permissions
echo -e "${CYAN}[*] Setting permissions...${RESET}"
chmod +x src/main.py 2>/dev/null
chmod +x src/*.py 2>/dev/null
chmod +x *.sh 2>/dev/null

# Setup udev rules for USB access (requires root)
if [ "$EUID" -eq 0 ]; then
    echo -e "${CYAN}[*] Setting up udev rules for USB access...${RESET}"
    
    # Samsung devices
    cat > /etc/udev/rules.d/99-samsung.rules << 'EOF'
# Samsung Android devices
SUBSYSTEM=="usb", ATTR{idVendor}=="04e8", MODE="0666", GROUP="plugdev"
# Google/Android devices
SUBSYSTEM=="usb", ATTR{idVendor}=="18d1", MODE="0666", GROUP="plugdev"
# Generic Android devices
SUBSYSTEM=="usb", ATTR{idVendor}=="0bb4", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="0e79", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="0502", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="0b05", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="413c", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="0489", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="091e", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="18d1", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="0fce", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="19d2", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="1bbb", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="2717", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="22d9", MODE="0666", GROUP="plugdev"
EOF
    
    # Reload udev rules
    udevadm control --reload-rules
    udevadm trigger
    
    echo -e "${GREEN}[+] Udev rules installed!${RESET}"
fi

# Test Python installation
echo -e "${CYAN}[*] Testing Python installation...${RESET}"
python3 --version

# Test pyusb
echo -e "${CYAN}[*] Testing pyusb...${RESET}"
python3 -c "import usb; print('pyusb version:', usb.__version__)" 2>/dev/null || {
    echo -e "${RED}[-] pyusb installation failed!${RESET}"
    echo -e "${YELLOW}[!] Try: sudo pip3 install pyusb${RESET}"
}

# Test ADB
echo -e "${CYAN}[*] Testing ADB...${RESET}"
adb version 2>/dev/null || echo -e "${YELLOW}[!] ADB not working properly${RESET}"

# Check USB devices
echo -e "${CYAN}[*] Checking USB devices...${RESET}"
lsusb 2>/dev/null || echo -e "${YELLOW}[!] lsusb not available${RESET}"

echo ""
echo -e "${GREEN}${BOLD}╔════════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${GREEN}${BOLD}║                    ✅ SETUP SELESAI!                              ║${RESET}"
echo -e "${GREEN}${BOLD}╚════════════════════════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${CYAN}📋 PERINTAH YANG TERSEDIA:${RESET}"
echo ""
echo -e "  ${YELLOW}# Cek koneksi device${RESET}"
echo -e "  sudo python3 src/main.py --check-connection"
echo ""
echo -e "  ${YELLOW}# Tunggu device terhubung${RESET}"
echo -e "  sudo python3 src/main.py --wait-device"
echo ""
echo -e "  ${YELLOW}# Bruteforce 4-digit PIN (STEALTH MODE)${RESET}"
echo -e "  sudo python3 src/main.py -p 4 --stealth"
echo ""
echo -e "  ${YELLOW}# Bruteforce 6-digit PIN${RESET}"
echo -e "  sudo python3 src/main.py -p 6 --stealth"
echo ""
echo -e "  ${YELLOW}# Tampilkan instruksi lengkap${RESET}"
echo -e "  sudo python3 src/main.py --instructions"
echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════════════${RESET}"
echo ""
echo -e "${YELLOW}📡 SETUP USB (PC ke HP):${RESET}"
echo -e "  1. Sambungkan Android ke PC via kabel USB"
echo -e "  2. Di Android: Aktifkan USB Debugging (opsional)"
echo -e "  3. Jalankan tool dengan sudo"
echo ""
echo -e "${RED}⚠️  PERINGATAN: Gunakan HANYA pada device MILIK SENDIRI!${RESET}"
echo ""