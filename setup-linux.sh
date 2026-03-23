#!/bin/bash
#
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║     SAMSUNG ANDROID PIN BRUTEFORCE - LINUX SETUP SCRIPT           ║
# ║     Install dependencies untuk Kali Linux / Ubuntu / Debian       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
#
# Penggunaan:
#   chmod +x setup-linux.sh
#   sudo ./setup-linux.sh
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
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║     SAMSUNG PIN BRUTEFORCE - LINUX SETUP                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
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
        
        # libusb for USB access - CRITICAL for PyUSB
        echo -e "${GREEN}[+] Installing libusb...${RESET}"
        apt install -y libusb-1.0-0-dev libusb-1.0-0
        
        # Android tools (ADB) - optional but recommended
        echo -e "${GREEN}[+] Installing Android tools (ADB)...${RESET}"
        apt install -y android-tools-adb android-tools-fastboot
        
        # Build essentials
        echo -e "${GREEN}[+] Installing build essentials...${RESET}"
        apt install -y build-essential
        
        # USB utilities
        echo -e "${GREEN}[+] Installing USB utilities...${RESET}"
        apt install -y usbutils
        ;;
        
    pacman)
        echo -e "${GREEN}[+] Installing Python...${RESET}"
        pacman -S --noconfirm python python-pip
        
        echo -e "${GREEN}[+] Installing libusb...${RESET}"
        pacman -S --noconfirm libusb
        
        echo -e "${GREEN}[+] Installing Android tools...${RESET}"
        pacman -S --noconfirm android-tools
        
        echo -e "${GREEN}[+] Installing USB utilities...${RESET}"
        pacman -S --noconfirm usbutils
        ;;
        
    dnf)
        echo -e "${GREEN}[+] Installing Python...${RESET}"
        dnf install -y python3 python3-pip
        
        echo -e "${GREEN}[+] Installing libusb...${RESET}"
        dnf install -y libusb1-devel libusb1
        
        echo -e "${GREEN}[+] Installing Android tools...${RESET}"
        dnf install -y android-tools
        
        echo -e "${GREEN}[+] Installing USB utilities...${RESET}"
        dnf install -y usbutils
        ;;
esac

# Install Python packages
echo -e "${CYAN}[*] Installing Python packages...${RESET}"

# Upgrade pip
pip3 install --upgrade pip

# Install pyusb - CRITICAL for USB communication
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

# Test libusb installation
echo -e "${CYAN}[*] Testing libusb installation...${RESET}"
if [ -f "/usr/lib/x86_64-linux-gnu/libusb-1.0.so" ]; then
    echo -e "${GREEN}[+] libusb found at /usr/lib/x86_64-linux-gnu/libusb-1.0.so${RESET}"
elif [ -f "/usr/lib/aarch64-linux-gnu/libusb-1.0.so" ]; then
    echo -e "${GREEN}[+] libusb found at /usr/lib/aarch64-linux-gnu/libusb-1.0.so${RESET}"
else
    echo -e "${YELLOW}[!] libusb location may vary, testing backend...${RESET}"
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
        '/usr/lib/x86_64-linux-gnu/libusb-1.0.so',
        '/usr/lib/aarch64-linux-gnu/libusb-1.0.so',
        '/usr/lib/arm-linux-gnueabihf/libusb-1.0.so',
        '/usr/lib/libusb-1.0.so',
        '/usr/local/lib/libusb-1.0.so',
        'libusb-1.0.so.0',
        'libusb-1.0.so',
    ]
    
    for path in libusb_paths:
        try:
            backend = usb.backend.libusb1.get_backend(find_library=lambda x: path)
            if backend:
                print('\033[92m[+] USB backend found at:', path, '\033[0m')
                break
        except:
            continue
    
    if not backend:
        # Try default
        backend = usb.backend.libusb1.get_backend()
        if backend:
            print('\033[92m[+] USB backend found using default discovery\033[0m')
        else:
            print('\033[91m[-] No USB backend found!\033[0m')
            print('\033[93m[!] Make sure libusb is installed: sudo apt install libusb-1.0-0\033[0m')
            sys.exit(1)
    
    # Try to list devices
    print('\033[96m[*] Scanning USB devices...\033[0m')
    devices = list(usb.core.find(find_all=True, backend=backend))
    print('\033[92m[+] Found', len(devices), 'USB device(s)\033[0m')
    
except ImportError as e:
    print('\033[91m[-] pyusb installation failed:', e, '\033[0m')
    print('\033[93m[!] Try: sudo pip3 install pyusb\033[0m')
    sys.exit(1)
except Exception as e:
    print('\033[91m[-] Error:', e, '\033[0m')
    print('\033[93m[!] Make sure libusb is installed: sudo apt install libusb-1.0-0\033[0m')
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
    echo -e "${YELLOW}║     sudo apt install libusb-1.0-0 libusb-1.0-0-dev                          ║${RESET}"
    echo -e "${YELLOW}║                                                                              ║${RESET}"
    echo -e "${YELLOW}║  2. Install pyusb dengan sudo:                                               ║${RESET}"
    echo -e "${YELLOW}║     sudo pip3 install pyusb                                                  ║${RESET}"
    echo -e "${YELLOW}║                                                                              ║${RESET}"
    echo -e "${YELLOW}║  3. Jalankan tool dengan sudo untuk akses USB:                               ║${RESET}"
    echo -e "${YELLOW}║     sudo python3 src/main.py --check-connection                             ║${RESET}"
    echo -e "${YELLOW}║                                                                              ║${RESET}"
    echo -e "${YELLOW}║  4. Cek apakah device terdeteksi:                                            ║${RESET}"
    echo -e "${YELLOW}║     lsusb                                                                    ║${RESET}"
    echo -e "${YELLOW}║                                                                              ║${RESET}"
    echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════════════════════╝${RESET}"
fi

# Test ADB
echo -e "${CYAN}[*] Testing ADB...${RESET}"
adb version 2>/dev/null || echo -e "${YELLOW}[!] ADB not working properly${RESET}"

# Check USB devices
echo -e "${CYAN}[*] Checking USB devices...${RESET}"
lsusb 2>/dev/null || echo -e "${YELLOW}[!] lsusb not available${RESET}"

echo ""
echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${GREEN}${BOLD}║                    ✅ SETUP SELESAI!                              ║${RESET}"
echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════════════════════════════════╝${RESET}"
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
echo -e "${CYAN}══════════════════════════════════════════════════════════════════════════${RESET}"
echo ""
echo -e "${YELLOW}📡 SETUP USB (PC ke HP):${RESET}"
echo -e "  1. Sambungkan Android ke PC via kabel USB"
echo -e "  2. Di Android: Aktifkan USB Debugging (opsional)"
echo -e "  3. Jalankan tool dengan sudo"
echo ""
echo -e "${RED}⚠️  PERINGATAN: Gunakan HANYA pada device MILIK SENDIRI!${RESET}"
echo ""