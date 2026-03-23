#!/bin/bash
#
# Quick launcher untuk Samsung PIN Bruteforce
#

# Colors
GREEN='\033[92m'
YELLOW='\033[93m'
CYAN='\033[96m'
RESET='\033[0m'

# Detect platform
if [ -n "$PREFIX" ] && [ -d "/data/data/com.termux" ]; then
    PYTHON="python3"
    SUDO=""
else
    PYTHON="python3"
    SUDO="sudo"
fi

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║     SAMSUNG PIN BRUTEFORCE - QUICK LAUNCHER                       ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo -e "${RESET}"

echo -e "${CYAN}Pilih opsi:${RESET}"
echo ""
echo "  1) Cek koneksi device"
echo "  2) Tunggu device terhubung"
echo "  3) Bruteforce 4-digit PIN (STEALTH)"
echo "  4) Bruteforce 6-digit PIN (STEALTH)"
echo "  5) Bruteforce 4-digit PIN (STANDARD)"
echo "  6) Bruteforce 6-digit PIN (STANDARD)"
echo "  7) Test single PIN"
echo "  8) Dry-run test (tanpa device)"
echo "  9) Tampilkan instruksi"
echo "  0) Keluar"
echo ""
read -p "Pilihan [0-9]: " choice

case $choice in
    1)
        $SUDO $PYTHON src/main.py --check-connection
        ;;
    2)
        read -p "Timeout (detik) [60]: " timeout
        timeout=${timeout:-60}
        $SUDO $PYTHON src/main.py --wait-device --wait-timeout $timeout
        ;;
    3)
        $SUDO $PYTHON src/main.py -p 4 --stealth
        ;;
    4)
        $SUDO $PYTHON src/main.py -p 6 --stealth
        ;;
    5)
        $SUDO $PYTHON src/main.py -p 4
        ;;
    6)
        $SUDO $PYTHON src/main.py -p 6
        ;;
    7)
        read -p "Masukkan PIN (4/6 digit): " pin
        $SUDO $PYTHON src/main.py --single-pin $pin
        ;;
    8)
        read -p "Jumlah PIN test [20]: " limit
        limit=${limit:-20}
        $PYTHON src/main.py -p 4 --dry-run --limit $limit
        ;;
    9)
        $PYTHON src/main.py --instructions
        ;;
    0)
        echo -e "${YELLOW}Keluar...${RESET}"
        exit 0
        ;;
    *)
        echo -e "${YELLOW}Pilihan tidak valid!${RESET}"
        exit 1
        ;;
esac