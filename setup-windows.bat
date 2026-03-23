@echo off
REM ╔════════════════════════════════════════════════════════════════════╗
REM ║     SAMSUNG ANDROID PIN BRUTEFORCE - WINDOWS SETUP SCRIPT        ║
REM ║     Install dependencies untuk Windows CMD / PowerShell          ║
REM ╚════════════════════════════════════════════════════════════════════╝
REM
REM Penggunaan:
REM   Klik kanan -> Run as Administrator
REM   atau jalankan dari CMD: setup-windows.bat
REM
REM Setup untuk USB (PC ke HP):
REM   PC/Laptop -> USB Cable -> Android Target

color 0A
title Samsung PIN Bruteforce - Windows Setup

echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║     SAMSUNG PIN BRUTEFORCE - WINDOWS SETUP                        ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [+] Running as Administrator
) else (
    echo [!] WARNING: Not running as Administrator
    echo [!] Some operations may fail
    echo.
    echo [!] Right-click and select "Run as Administrator"
    echo.
    pause
)

REM Check Python installation
echo [*] Checking Python installation...
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo [+] Python is installed:
    python --version
) else (
    echo [-] Python is NOT installed!
    echo.
    echo [!] Please install Python 3.7+ from:
    echo     https://www.python.org/downloads/
    echo.
    echo [!] Make sure to check "Add Python to PATH" during installation
    echo.
    goto :install_python
)

REM Check pip
echo.
echo [*] Checking pip...
pip --version >nul 2>&1
if %errorLevel% == 0 (
    echo [+] pip is installed:
    pip --version
) else (
    echo [-] pip is NOT installed!
    echo [!] Installing pip...
    python -m ensurepip --default-pip
)

REM Install pyusb
echo.
echo [*] Installing pyusb...
pip install pyusb --quiet
if %errorLevel% == 0 (
    echo [+] pyusb installed successfully
) else (
    echo [-] Failed to install pyusb
    echo [!] Try: pip install pyusb --user
)

REM Install other dependencies
echo.
echo [*] Installing other dependencies...
pip install colorama --quiet

REM Create directories
echo.
echo [*] Creating directories...
if not exist "logs" mkdir logs
if not exist "pins" mkdir pins
echo [+] Directories created

REM Download libusb for Windows
echo.
echo [*] Setting up libusb for Windows...
echo [!] Note: On Windows, libusb is included with pyusb
echo [!] If you encounter USB errors, download Zadig from:
echo     https://zadig.akeo.ie/
echo.
echo [!] Use Zadig to install libusb-win32 driver for your Android device

REM Check ADB
echo.
echo [*] Checking ADB...
adb version >nul 2>&1
if %errorLevel% == 0 (
    echo [+] ADB is installed:
    adb version
) else (
    echo [!] ADB is not in PATH
    echo [!] Install Android SDK Platform Tools from:
    echo     https://developer.android.com/studio/releases/platform-tools
    echo.
    echo [!] Or download minimal ADB:
    echo     https://forum.xda-developers.com/t/official-tool-minimal-adb-and-fastboot.2317790/
)

REM Create run scripts
echo.
echo [*] Creating run scripts...

REM run_4pin.bat
echo @echo off > run_4pin.bat
echo color 0A >> run_4pin.bat
echo title Samsung PIN Bruteforce - 4-digit >> run_4pin.bat
echo echo. >> run_4pin.bat
echo echo [*] Running 4-digit PIN bruteforce... >> run_4pin.bat
echo python src\main.py -p 4 --stealth >> run_4pin.bat
echo pause >> run_4pin.bat

REM run_6pin.bat
echo @echo off > run_6pin.bat
echo color 0A >> run_6pin.bat
echo title Samsung PIN Bruteforce - 6-digit >> run_6pin.bat
echo echo. >> run_6pin.bat
echo echo [*] Running 6-digit PIN bruteforce... >> run_6pin.bat
echo python src\main.py -p 6 --stealth >> run_6pin.bat
echo pause >> run_6pin.bat

REM check_connection.bat
echo @echo off > check_connection.bat
echo color 0B >> check_connection.bat
echo title Check Device Connection >> check_connection.bat
echo echo. >> check_connection.bat
echo echo [*] Checking device connection... >> check_connection.bat
echo python src\main.py --check-connection >> check_connection.bat
echo pause >> check_connection.bat

echo [+] Run scripts created

REM Test Python and pyusb
echo.
echo [*] Testing Python and pyusb...
python -c "import usb; print('[+] pyusb version:', usb.__version__)" 2>nul
if %errorLevel% == 0 (
    echo [+] All tests passed!
) else (
    echo [-] Test failed! Check Python installation
)

echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                    SETUP SELESAI!                                 ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo 📋 PERINTAH YANG TERSEDIA:
echo.
echo   # Cek koneksi device
echo   python src\main.py --check-connection
echo   atau: check_connection.bat
echo.
echo   # Bruteforce 4-digit PIN (STEALTH MODE)
echo   python src\main.py -p 4 --stealth
echo   atau: run_4pin.bat
echo.
echo   # Bruteforce 6-digit PIN
echo   python src\main.py -p 6 --stealth
echo   atau: run_6pin.bat
echo.
echo   # Tampilkan instruksi lengkap
echo   python src\main.py --instructions
echo.
echo ════════════════════════════════════════════════════════════════════
echo.
echo 📡 SETUP USB (PC ke HP):
echo   1. Sambungkan Android ke PC via kabel USB
echo   2. Di Android: Aktifkan USB Debugging (opsional)
echo   3. Jika device tidak terdeteksi, install driver USB:
echo      - Samsung: https://www.samsung.com/us/support/downloads/
echo      - Universal: https://adb.clockworkmod.com/
echo   4. Jalankan tool
echo.
echo ⚠️  PERINGATAN: Gunakan HANYA pada device MILIK SENDIRI!
echo.
pause
exit /b 0

:install_python
echo.
echo [*] Opening Python download page...
start https://www.python.org/downloads/
echo.
echo [!] Please install Python and run this script again.
pause
exit /b 1