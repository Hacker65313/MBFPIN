#!/bin/bash
# ══════════════════════════════════════════════════════════════
#  INSTALLER - Samsung Android PIN Bruteforce Tool
#  Support: Kali Linux & Termux (Android)
# ══════════════════════════════════════════════════════════════

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║   Samsung Android PIN Bruteforce - Installer        ║"
    echo "║   Platform: Kali Linux / Termux                     ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

info()    { echo -e "${GREEN}[+]${NC} $1"; }
warn()    { echo -e "${YELLOW}[!]${NC} $1"; }
error()   { echo -e "${RED}[-]${NC} $1"; }
step()    { echo -e "${BOLD}${CYAN}[*]${NC} $1"; }

banner

# ── Deteksi platform ──────────────────────────────────────────
detect_platform() {
    if [ -d "/data/data/com.termux" ] || [ -n "$TERMUX_VERSION" ]; then
        echo "termux"
    elif grep -qi "kali" /etc/os-release 2>/dev/null; then
        echo "kali"
    elif grep -qi "debian\|ubuntu\|parrot" /etc/os-release 2>/dev/null; then
        echo "debian"
    else
        echo "linux"
    fi
}

PLATFORM=$(detect_platform)
info "Platform terdeteksi: ${BOLD}$PLATFORM${NC}"

# ── Install dependencies ──────────────────────────────────────
install_deps() {
    step "Menginstall dependencies..."

    if [ "$PLATFORM" = "termux" ]; then
        # ── Termux ──────────────────────────────────────
        step "Install paket Termux..."
        pkg update -y
        pkg install -y python python-pip libusb clang make

        # pyusb
        pip install pyusb --upgrade

        info "Termux deps selesai!"

    else
        # ── Kali Linux / Debian ──────────────────────────
        step "Install paket system (apt)..."

        # Cek root
        if [ "$(id -u)" -ne 0 ]; then
            warn "Tidak root, pakai sudo..."
            SUDO="sudo"
        else
            SUDO=""
        fi

        $SUDO apt-get update -qq
        $SUDO apt-get install -y \
            python3 \
            python3-pip \
            python3-venv \
            libusb-1.0-0 \
            libusb-1.0-0-dev \
            usbutils \
            2>/dev/null

        # pyusb
        step "Install Python packages..."
        pip3 install pyusb --upgrade 2>/dev/null || \
            $SUDO pip3 install pyusb --upgrade

        # udev rules untuk akses USB tanpa root
        step "Setup udev rules untuk USB access..."
        RULES_FILE="/etc/udev/rules.d/51-android-aoa.rules"
        $SUDO bash -c "cat > $RULES_FILE" << 'UDEV'
# Android devices - AOA mode
SUBSYSTEM=="usb", ATTR{idVendor}=="18d1", MODE="0666", GROUP="plugdev"
# Samsung
SUBSYSTEM=="usb", ATTR{idVendor}=="04e8", MODE="0666", GROUP="plugdev"
# Xiaomi
SUBSYSTEM=="usb", ATTR{idVendor}=="2717", MODE="0666", GROUP="plugdev"
# Huawei
SUBSYSTEM=="usb", ATTR{idVendor}=="12d1", MODE="0666", GROUP="plugdev"
# HTC
SUBSYSTEM=="usb", ATTR{idVendor}=="0bb4", MODE="0666", GROUP="plugdev"
# Sony
SUBSYSTEM=="usb", ATTR{idVendor}=="054c", MODE="0666", GROUP="plugdev"
# OPPO/OnePlus
SUBSYSTEM=="usb", ATTR{idVendor}=="22d9", MODE="0666", GROUP="plugdev"
# Motorola
SUBSYSTEM=="usb", ATTR{idVendor}=="1bbb", MODE="0666", GROUP="plugdev"
UDEV

        $SUDO udevadm control --reload-rules 2>/dev/null
        $SUDO udevadm trigger 2>/dev/null
        info "udev rules ditambahkan: $RULES_FILE"
        info "Kali Linux deps selesai!"
    fi
}

# ── Buat virtual environment (Linux only) ────────────────────
setup_venv() {
    if [ "$PLATFORM" != "termux" ]; then
        step "Setup Python virtual environment..."
        python3 -m venv venv 2>/dev/null
        if [ -d "venv" ]; then
            source venv/bin/activate
            pip install pyusb --upgrade -q
            info "venv aktif. Gunakan: source venv/bin/activate"
        fi
    fi
}

# ── Buat launcher script ─────────────────────────────────────
create_launcher() {
    step "Membuat launcher scripts..."

    # Launcher 4-pin
    cat > run_4pin.sh << 'EOF'
#!/bin/bash
# Launcher bruteforce 4-digit PIN
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Aktifkan venv jika ada
[ -f "venv/bin/activate" ] && source venv/bin/activate

echo "[*] Memulai bruteforce 4-digit PIN..."
echo "[*] Tekan Ctrl+C untuk pause dan simpan progress"
echo ""

if [ "$(id -u)" -ne 0 ] && [ -z "$TERMUX_VERSION" ]; then
    exec sudo python3 src/main.py -p 4 "$@"
else
    exec python3 src/main.py -p 4 "$@"
fi
EOF

    # Launcher 6-pin
    cat > run_6pin.sh << 'EOF'
#!/bin/bash
# Launcher bruteforce 6-digit PIN
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

[ -f "venv/bin/activate" ] && source venv/bin/activate

echo "[*] Memulai bruteforce 6-digit PIN..."
echo "[*] Tekan Ctrl+C untuk pause dan simpan progress"
echo ""

if [ "$(id -u)" -ne 0 ] && [ -z "$TERMUX_VERSION" ]; then
    exec sudo python3 src/main.py -p 6 "$@"
else
    exec python3 src/main.py -p 6 "$@"
fi
EOF

    # Test koneksi
    cat > test_connection.sh << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
[ -f "venv/bin/activate" ] && source venv/bin/activate

if [ "$(id -u)" -ne 0 ] && [ -z "$TERMUX_VERSION" ]; then
    exec sudo python3 src/main.py --test-connection
else
    exec python3 src/main.py --test-connection
fi
EOF

    chmod +x run_4pin.sh run_6pin.sh test_connection.sh
    info "Launcher scripts dibuat!"
}

# ── Verifikasi instalasi ─────────────────────────────────────
verify_install() {
    step "Verifikasi instalasi..."

    # Cek Python
    if command -v python3 &>/dev/null; then
        PY_VER=$(python3 --version)
        info "Python: $PY_VER ✓"
    else
        error "Python3 tidak ditemukan!"
        exit 1
    fi

    # Cek pyusb
    if python3 -c "import usb.core" 2>/dev/null; then
        info "pyusb: ✓"
    else
        error "pyusb tidak terinstall!"
        warn "Coba: pip3 install pyusb"
    fi

    # Cek libusb
    if [ "$PLATFORM" != "termux" ]; then
        if ldconfig -p 2>/dev/null | grep -q "libusb-1.0"; then
            info "libusb-1.0: ✓"
        else
            warn "libusb-1.0 mungkin tidak terinstall"
            warn "Coba: sudo apt install libusb-1.0-0"
        fi
    fi

    # Cek file PIN
    if [ -f "pins/pins-4-digit.txt" ]; then
        COUNT=$(wc -l < pins/pins-4-digit.txt)
        info "PIN 4-digit: $COUNT entries ✓"
    else
        warn "File pins/pins-4-digit.txt tidak ditemukan!"
    fi

    if [ -f "pins/pins-6-digit.txt" ]; then
        COUNT=$(wc -l < pins/pins-6-digit.txt)
        info "PIN 6-digit: $COUNT entries ✓"
    else
        warn "File pins/pins-6-digit.txt tidak ditemukan!"
    fi
}

# ── Main ─────────────────────────────────────────────────────
install_deps
setup_venv
create_launcher
verify_install

echo ""
echo -e "${GREEN}${BOLD}══════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}  ✅  Instalasi selesai!${NC}"
echo -e "${GREEN}${BOLD}══════════════════════════════════════════${NC}"
echo ""
echo -e "${BOLD}Cara penggunaan:${NC}"
echo ""
echo -e "  ${CYAN}Test koneksi USB:${NC}"
echo "  ./test_connection.sh"
echo ""
echo -e "  ${CYAN}Bruteforce 4-digit PIN:${NC}"
echo "  ./run_4pin.sh"
echo ""
echo -e "  ${CYAN}Bruteforce 6-digit PIN:${NC}"
echo "  ./run_6pin.sh"
echo ""
echo -e "  ${CYAN}Opsi tambahan:${NC}"
echo "  ./run_4pin.sh --verbose          # detail output"
echo "  ./run_4pin.sh --reset            # mulai dari awal"
echo "  ./run_4pin.sh --limit 100        # coba 100 PIN saja"
echo "  ./run_4pin.sh --start-pin 5000   # mulai dari PIN 5000"
echo ""
echo -e "  ${CYAN}Manual (langsung):${NC}"
echo "  sudo python3 src/main.py -p 4"
echo "  sudo python3 src/main.py -p 6 --verbose"
echo ""
echo -e "${YELLOW}⚠️  Jalankan dengan sudo di Linux (kecuali Termux)${NC}"
echo ""