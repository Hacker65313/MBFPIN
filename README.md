# 📱 Samsung Android PIN Bruteforce Tool

> Via USB HID (Android Open Accessory 2.0)  
> Platform: **Termux (Android OTG)** | **Kali Linux** | **Windows CMD**  
> Support: **4-digit** & **6-digit** PIN Samsung  
> **NEW:** USB Device Detection | Connection Check | Cross-Platform Support

---

## ⚠️ DISCLAIMER

> Tool ini **HANYA** untuk digunakan pada perangkat **milik sendiri**.  
> Penggunaan pada perangkat orang lain adalah **ILEGAL** dan dapat dikenakan sanksi hukum.  
> Penulis tidak bertanggung jawab atas penyalahgunaan tool ini.

---

## 🆕 Fitur Baru

### 🔌 USB Device Detection & Connection Check

Tool sekarang secara otomatis mendeteksi device yang terhubung via USB:

```bash
# Cek koneksi device sebelum bruteforce
python3 src/main.py --check-connection

# Tunggu device terhubung (max 60 detik)
python3 src/main.py --wait-device
```

Output saat device terdeteksi:
```
╔════════════════════════════════════════════════════════════════════╗
║                    📱 DEVICE DETECTED                              ║
╠════════════════════════════════════════════════════════════════════╣
║  Vendor         : Samsung                                          ║
║  USB ID         : VID:04E8:PID:6860                                ║
║  Product        : Samsung Galaxy A55 5G                            ║
╚════════════════════════════════════════════════════════════════════╝
```

### 🖥️ Cross-Platform Support

Tool mendukung 3 platform:

| Platform | Setup Script | USB Mode | Notes |
|----------|--------------|----------|-------|
| **Termux (Android)** | `setup-termux.sh` | USB OTG (HP → HP) | HP1 menyerang HP2 |
| **Linux (Kali/Ubuntu)** | `setup-linux.sh` | USB (PC → HP) | Perlu sudo |
| **Windows (CMD/PowerShell)** | `setup-windows.bat` | USB (PC → HP) | Perlu driver USB |

### 📋 Terminal Commands & Instructions

```bash
# Tampilkan instruksi lengkap
python3 src/main.py --instructions
```

### 🕵️ Stealth Mode

Mode tersembunyi untuk menghindari deteksi sistem:
- **Delay natural** dengan random jitter - seperti ketikan manusia
- **Tidak ada countdown lockout** yang terlihat di terminal
- **Aktivitas tap random** untuk menghindari timeout
- **Waktu tunggu tersebar** dalam beberapa segmen

---

## 🔧 Cara Kerja

Tool ini memanfaatkan protokol **Android Open Accessory (AOA) 2.0** untuk mensimulasikan perangkat HID (touchscreen) melalui USB. Komputer/laptop/HP yang menjalankan script ini akan terdeteksi sebagai "aksesori" oleh Android, lalu mengirimkan event sentuhan virtual untuk mencoba PIN satu per satu.

### Mode 1: USB OTG (Termux - HP ke HP)

```
┌─────────────────┐        ┌─────────────────┐
│   HP 1          │        │   HP 2          │
│   (Attacker)    │        │   (Target)      │
│                 │        │                 │
│  Termux         │  USB   │  Lock Screen    │
│  + Tool ini  ───┼──OTG───┼─► PIN Keypad   │
│                 │  Cable │                 │
│                 │        │                 │
└─────────────────┘        └─────────────────┘
```

**Setup:**
1. HP 1: Install Termux + tool ini
2. HP 2: HP yang lupa PIN
3. Sambungkan: HP 1 → USB OTG Adapter → USB Cable → HP 2
4. Jalankan tool di HP 1

### Mode 2: USB (PC ke HP)

```
┌─────────────────┐        ┌─────────────────┐
│   PC/Laptop     │        │   Android       │
│   (Linux/Win)   │        │   (Target)      │
│                 │        │                 │
│  Python         │  USB   │  Lock Screen    │
│  + Tool ini  ───┼────────┼─► PIN Keypad   │
│                 │  Cable │                 │
│                 │        │                 │
└─────────────────┘        └─────────────────┘
```

### Alur kerja:
1. **Script mendeteksi Android device via USB**
2. **Mengidentifikasi device dan menampilkan info lengkap**
3. Mengirim sinyal AOA untuk switch ke accessory mode
4. Mendaftarkan HID touchscreen virtual
5. **Menggunakan koordinat keypad yang sesuai untuk device**
6. Mensimulasikan ketukan pada keypad PIN lock screen
7. **Stealth mode: menangani lockout secara tersembunyi**
8. Menyimpan progress otomatis (bisa di-resume)

---

## 📋 Requirements

### Hardware

| Mode | Hardware |
|------|----------|
| Termux (OTG) | USB OTG Adapter + USB Cable |
| Linux | USB Cable |
| Windows | USB Cable + Driver USB |

### Software - Termux (Android)

```bash
# Jalankan setup script
chmod +x setup-termux.sh
./setup-termux.sh

# Atau manual
pkg install python libusb android-tools
pip install pyusb
```

### Software - Kali Linux / Ubuntu / Debian

```bash
# Jalankan setup script
chmod +x setup-linux.sh
sudo ./setup-linux.sh

# Atau manual
sudo apt install python3 python3-pip libusb-1.0-0-dev android-tools-adb
pip3 install pyusb
```

### Software - Windows

```batch
:: Jalankan setup script (Run as Administrator)
setup-windows.bat

:: Atau manual
:: 1. Install Python dari python.org
:: 2. pip install pyusb
:: 3. Install driver USB jika diperlukan
```

---

## 🚀 Instalasi

### Termux (Android)

```bash
# Clone / ekstrak tool
cd android-bruteforce-samsung

# Jalankan installer
chmod +x setup-termux.sh
./setup-termux.sh
```

### Linux

```bash
# Clone / ekstrak tool
cd android-bruteforce-samsung

# Jalankan installer
chmod +x setup-linux.sh
sudo ./setup-linux.sh
```

### Windows

```batch
:: Klik kanan pada setup-windows.bat
:: Pilih "Run as Administrator"

:: Atau dari CMD
setup-windows.bat
```

---

## 📖 Penggunaan

### Quick Start

```bash
# 1. Cek koneksi device
python3 src/main.py --check-connection

# 2. Jika belum terhubung, tunggu device
python3 src/main.py --wait-device --wait-timeout 120

# 3. Jalankan bruteforce
python3 src/main.py -p 4 --stealth
```

### Semua Perintah

```
🔌 CONNECTION OPTIONS:
  --check-connection    Cek koneksi USB device sebelum bruteforce
  --wait-device         Tunggu device terhubung (default: 60 detik)
  --wait-timeout N      Timeout dalam detik untuk --wait-device
  --test-connection     Test koneksi USB saja, tidak bruteforce

🔐 BRUTEFORCE OPTIONS:
  -p, --pin-length      Panjang PIN: 4 atau 6 (default: 4)
  -f, --pin-file        Path file PIN kustom
  -v, --verbose         Output debug detail
  --stealth             Aktifkan STEALTH MODE (tidak terdeteksi sistem)
  --delay MS            Delay ms setelah setiap PIN (default: 1200)
  --key-delay MS        Delay ms antar ketukan (default: 80)
  --reset               Reset progress, mulai dari awal
  --dry-run             Simulasi tanpa hardware
  --limit N             Batasi N percobaan
  --start-pin PIN       Mulai dari PIN tertentu
  --single-pin PIN      Coba satu PIN saja

ℹ️ INFO OPTIONS:
  --list-devices        Tampilkan daftar device yang didukung
  --instructions        Tampilkan instruksi penggunaan lengkap
```

### Contoh Penggunaan

```bash
# ═══════════════════════════════════════════════════════════════
# CONNECTION CHECK
# ═══════════════════════════════════════════════════════════════

# Cek apakah device terdeteksi
python3 src/main.py --check-connection

# Tunggu device terhubung (max 120 detik)
python3 src/main.py --wait-device --wait-timeout 120

# ═══════════════════════════════════════════════════════════════
# BRUTEFORCE
# ═══════════════════════════════════════════════════════════════

# 4-digit PIN dengan stealth mode (REKOMENDASI)
python3 src/main.py -p 4 --stealth

# 6-digit PIN dengan stealth mode
python3 src/main.py -p 6 --stealth

# Standard mode (dengan countdown lockout)
python3 src/main.py -p 4

# Verbose mode (tampilkan semua detail)
python3 src/main.py -p 4 --stealth --verbose

# ═══════════════════════════════════════════════════════════════
# PROGRESS CONTROL
# ═══════════════════════════════════════════════════════════════

# Mulai dari awal (reset progress)
python3 src/main.py -p 4 --stealth --reset

# Coba hanya 50 PIN pertama (untuk test)
python3 src/main.py -p 4 --stealth --limit 50

# Mulai dari PIN tertentu
python3 src/main.py -p 4 --stealth --start-pin 5000

# Coba satu PIN saja
python3 src/main.py --single-pin 1234

# ═══════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════

# Dry run (simulasi tanpa device)
python3 src/main.py -p 4 --dry-run --limit 20

# Custom delay (lebih lambat = lebih aman)
python3 src/main.py -p 4 --stealth --delay 2000 --key-delay 100

# Pakai file PIN custom
python3 src/main.py -p 4 -f pins/pins-4-smart.txt --stealth
```

### Perintah ADB (Opsional)

```bash
# Cek device via ADB
adb devices

# Restart ADB server
adb kill-server && adb start-server

# Info device
adb shell getprop ro.product.model

# Install ADB di Termux
pkg install android-tools

# Install ADB di Linux
sudo apt install android-tools-adb
```

---

## 🔢 PIN List

Tool ini menyediakan beberapa jenis PIN list:

| File | Total PIN | Deskripsi |
|------|-----------|-----------|
| `pins-4-digit.txt` | 10,000 | Semua kombinasi 4-digit |
| `pins-4-smart.txt` | 649 | PIN 4-digit prioritas tinggi ⭐ |
| `pins-6-digit.txt` | 1,000,000 | Semua kombinasi 6-digit |
| `pins-6-smart.txt` | 13,609 | PIN 6-digit prioritas tinggi ⭐ |

### Generate PIN Custom

```bash
# Generate semua PIN list
python3 src/pin_generator.py --all

# Generate hanya 4-digit
python3 src/pin_generator.py -p 4 -o pins/my-pins.txt

# Generate smart list
python3 src/pin_generator.py -p 4 --smart -o pins/smart.txt

# Generate dengan custom PIN di awal
python3 src/pin_generator.py -p 4 --custom "1234,5678,9999"
```

---

## 📁 Struktur Project

```
android-bruteforce-samsung/
├── src/
│   ├── main.py              # Entry point utama
│   ├── bruteforce.py        # Engine bruteforce
│   ├── touchscreen.py       # Controller HID touchscreen
│   ├── usb_accessory.py     # USB AOA connection
│   ├── device_detector.py   # USB device detection (NEW)
│   ├── device_database.py   # Database device Samsung
│   ├── hid_descriptor.py    # HID report descriptor
│   └── pin_generator.py     # Tool generate PIN
├── pins/
│   ├── pins-4-digit.txt
│   ├── pins-4-smart.txt
│   ├── pins-6-digit.txt
│   └── pins-6-smart.txt
├── logs/
│   ├── progress.txt         # Resume progress
│   ├── found.txt            # PIN yang ditemukan
│   └── bruteforce.log
├── setup-termux.sh          # Setup untuk Termux (NEW)
├── setup-linux.sh           # Setup untuk Linux (NEW)
├── setup-windows.bat        # Setup untuk Windows (NEW)
├── install.sh               # Installer lama
├── run_4pin.sh              # Launcher 4-digit
├── run_6pin.sh              # Launcher 6-digit
└── README.md
```

---

## 📊 Estimasi Waktu

| PIN Length | Total kombinasi | Standard Mode | Stealth Mode |
|------------|----------------|---------------|--------------|
| 4-digit | 10,000 | ~2 jam | ~1.5 jam |
| 6-digit | 1,000,000 | ~8 hari | ~5 hari |

> Catatan: Samsung lockout 30 detik setiap 5 percobaan salah

---

## 🔄 Resume / Lanjut dari Checkpoint

Jika proses terhenti, progress tersimpan di `logs/progress.txt`:

```bash
# Jalankan lagi perintah yang sama - otomatis lanjut
python3 src/main.py -p 4 --stealth

# Atau mulai dari awal
python3 src/main.py -p 4 --stealth --reset
```

---

## 🐛 Troubleshooting

### "Device tidak ditemukan"

```bash
# Cek apakah device terdeteksi sistem
lsusb | grep -i samsung      # Linux
adb devices                  # Jika USB Debugging aktif

# Termux: Cek USB OTG
# Pastikan USB OTG adapter berfungsi

# Windows: Install driver USB
# Samsung: https://www.samsung.com/us/support/downloads/
```

### "Gagal switch ke AOA mode"

- Pastikan kabel USB berfungsi baik (bukan kabel charge-only)
- Coba cabut-colok kabel USB
- Pastikan Android masih di lock screen
- Restart tool

### "Ketukan tidak tepat sasaran"

```bash
# Test dengan single PIN
python3 src/main.py --single-pin 1234

# Tambah delay
python3 src/main.py -p 4 --stealth --delay 2000 --key-delay 150
```

### "Permission denied" (Linux)

```bash
# Jalankan dengan sudo
sudo python3 src/main.py -p 4 --stealth

# Atau setup udev rules
sudo ./setup-linux.sh
```

### "pyusb not found"

```bash
# Install pyusb
pip install pyusb
# atau
pip3 install pyusb
# atau dengan sudo
sudo pip3 install pyusb
```

---

## 📝 Notes

- Tool ini bekerja **tanpa USB Debugging** aktif (via AOA)
- Tidak perlu root pada target device
- Perlu root/sudo di Linux untuk akses libusb
- Di Termux, tidak perlu root (USB host langsung diakses)
- **Stealth mode** direkomendasikan untuk menghindari deteksi
- **Connection check** sebelum bruteforce untuk memastikan device siap

---

## 🔐 Keamanan & Privasi

Tool ini dirancang untuk:
- Recovery PIN pada device milik sendiri
- Testing keamanan device sendiri
- Edukasi tentang keamanan Android

**TIDAK untuk:**
- Membuka kunci device orang lain
- Aktivitas ilegal apapun

---

## 📜 Lisensi

Tool ini dibuat untuk tujuan edukasi. Pengguna bertanggung jawab penuh atas penggunaan tool ini.

---

## 🙏 Credits

- Android Open Accessory Protocol
- Samsung Device Database
- HID Touchscreen Implementation
- MasJawa (fendipendol65)