#!/usr/bin/env python3
"""
PIN List Generator untuk Samsung Android Bruteforce
Menghasilkan daftar PIN 4-digit dan 6-digit berdasarkan frekuensi penggunaan
Support custom PIN addition
"""

import os
import argparse
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
#  PIN Statistics - Berdasarkan riset keamanan
#  Sumber: Data breach analysis, security research papers
# ─────────────────────────────────────────────────────────────────────────────

# 4-digit PIN paling populer (berdasarkan riset)
# Total ~27% dari semua PIN 4-digit adalah PIN di bawah ini
POPULAR_4DIGIT_PINS = [
    # Top 20 - Paling sering digunakan (20% dari total)
    "1234", "1111", "0000", "1212", "7777",
    "1004", "2000", "4444", "2222", "6969",
    "9999", "3333", "5555", "6666", "1122",
    "1313", "8888", "4321", "2001", "1010",
    
    # Patterns - Pola umum
    "0123", "1230", "4567", "5678", "6789",
    "7890", "8901", "9012", "2345", "3456",
    "9876", "8765", "7654", "6543", "5432",
    
    # Repeated pairs
    "1122", "2233", "3344", "4455", "5566",
    "6677", "7788", "8899", "9900", "0011",
    
    # Years (birth years 1950-2024)
    "1990", "1991", "1992", "1993", "1994",
    "1995", "1996", "1997", "1998", "1999",
    "2000", "2001", "2002", "2003", "2004",
    "2005", "2006", "2007", "2008", "2009",
    "2010", "2011", "2012", "2013", "2014",
    "2015", "2016", "2017", "2018", "2019",
    "2020", "2021", "2022", "2023", "2024",
    "1980", "1981", "1982", "1983", "1984",
    "1985", "1986", "1987", "1988", "1989",
    
    # Dates (MMDD format)
    "0101", "0202", "0303", "0404", "0505",
    "0606", "0707", "0808", "0909", "1010",
    "1111", "1212", "0112", "0212", "0312",
    "0412", "0512", "0612", "0712", "0812",
    "0912", "1012", "1112", "1231", "1225",
    
    # Keyboard patterns
    "2580", "0852", "1379", "9753", "1590",
    "3570", "1597", "3579", "1470", "3690",
    
    # Samsung specific patterns
    "0000", "1234", "1111", "5555", "8888",
    "0909", "0606", "0707", "0505", "0808",
]

# 6-digit PIN paling populer
# Sumber: Analysis dari data breach
POPULAR_6DIGIT_PINS = [
    # Top patterns
    "123456", "111111", "000000", "121212", "654321",
    "666666", "696969", "999999", "112233", "123123",
    "159753", "456789", "012345", "777777", "100200",
    "131313", "101010", "789456", "520520", "520131",
    
    # Repeated digits
    "111111", "222222", "333333", "444444", "555555",
    "666666", "777777", "888888", "999999", "000000",
    
    # Sequential
    "123456", "234567", "345678", "456789", "567890",
    "678901", "789012", "890123", "901234", "012345",
    "654321", "543210", "432109", "321098", "210987",
    
    # Birth dates (DDMMYY format)
    "010199", "020299", "030399", "040499", "050599",
    "060699", "070799", "080899", "090999", "101099",
    "111199", "121299", "010100", "010101", "010102",
    "010103", "010104", "010105", "010106", "010107",
    "010108", "010109", "010110", "010111", "010112",
    
    # Years (YYYY format variations)
    "199001", "199102", "199203", "199304", "199405",
    "199506", "199607", "199708", "199809", "199910",
    "200001", "200102", "200203", "200304", "200405",
    "200506", "200607", "200708", "200809", "200910",
    
    # Keyboard patterns
    "147258", "258369", "159357", "147369", "258147",
    "369258", "951753", "852456", "789456", "123789",
    
    # Samsung specific
    "000000", "123456", "111111", "888888", "555555",
]


def generate_4digit_pins():
    """Generate semua 4-digit PIN (0000-9999) dengan urutan berdasarkan popularitas"""
    pins = []
    
    # Tambahkan popular PIN dulu (tanpa duplikat)
    seen = set()
    for pin in POPULAR_4DIGIT_PINS:
        if pin not in seen and len(pin) == 4 and pin.isdigit():
            pins.append(pin)
            seen.add(pin)
    
    # Tambahkan semua kombinasi 4-digit yang tersisa
    for i in range(10000):
        pin = f"{i:04d}"
        if pin not in seen:
            pins.append(pin)
            seen.add(pin)
    
    return pins


def generate_6digit_pins():
    """Generate semua 6-digit PIN (000000-999999) dengan urutan berdasarkan popularitas"""
    pins = []
    
    # Tambahkan popular PIN dulu (tanpa duplikat)
    seen = set()
    for pin in POPULAR_6DIGIT_PINS:
        if pin not in seen and len(pin) == 6 and pin.isdigit():
            pins.append(pin)
            seen.add(pin)
    
    # Tambahkan semua kombinasi 6-digit yang tersisa
    for i in range(1000000):
        pin = f"{i:06d}"
        if pin not in seen:
            pins.append(pin)
            seen.add(pin)
    
    return pins


def generate_smart_4digit_pins():
    """
    Generate 4-digit PIN dengan prioritas tinggi
    Total: ~500 PIN yang paling mungkin digunakan
    """
    pins = []
    seen = set()
    
    # 1. Semua popular PIN
    for pin in POPULAR_4DIGIT_PINS:
        if pin not in seen and len(pin) == 4 and pin.isdigit():
            pins.append(pin)
            seen.add(pin)
    
    # 2. Semua tahun (1950-2025)
    for year in range(1950, 2026):
        pin = str(year)
        if pin not in seen:
            pins.append(pin)
            seen.add(pin)
    
    # 3. Semua tanggal (MMDD format)
    for month in range(1, 13):
        for day in range(1, 32):
            pin = f"{month:02d}{day:02d}"
            if pin not in seen:
                pins.append(pin)
                seen.add(pin)
    
    # 4. Pattern pins (AAAA, AABB, ABAB)
    for i in range(10):
        pins.append(f"{i}{i}{i}{i}")  # AAAA
        for j in range(10):
            if f"{i}{i}{j}{j}" not in seen:  # AABB
                pins.append(f"{i}{i}{j}{j}")
            if f"{i}{j}{i}{j}" not in seen:  # ABAB
                pins.append(f"{i}{j}{i}{j}")
    
    # Remove duplicates while preserving order
    result = []
    seen = set()
    for pin in pins:
        if pin not in seen and len(pin) == 4 and pin.isdigit():
            result.append(pin)
            seen.add(pin)
    
    return result


def generate_smart_6digit_pins():
    """
    Generate 6-digit PIN dengan prioritas tinggi
    Total: ~1000 PIN yang paling mungkin digunakan
    """
    pins = []
    seen = set()
    
    # 1. Semua popular PIN
    for pin in POPULAR_6DIGIT_PINS:
        if pin not in seen and len(pin) == 6 and pin.isdigit():
            pins.append(pin)
            seen.add(pin)
    
    # 2. Tanggal lengkap (DDMMYY)
    for day in range(1, 32):
        for month in range(1, 13):
            for year in range(90, 100):  # 1990-1999
                pin = f"{day:02d}{month:02d}{year:02d}"
                if pin not in seen:
                    pins.append(pin)
                    seen.add(pin)
            for year in range(0, 26):  # 2000-2025
                pin = f"{day:02d}{month:02d}{year:02d}"
                if pin not in seen:
                    pins.append(pin)
                    seen.add(pin)
    
    # 3. Pattern pins
    for i in range(10):
        pins.append(f"{i}{i}{i}{i}{i}{i}")  # AAAAAA
        for j in range(10):
            if f"{i}{i}{i}{j}{j}{j}" not in seen:  # AAABBB
                pins.append(f"{i}{i}{i}{j}{j}{j}")
            if f"{i}{j}{i}{j}{i}{j}" not in seen:  # ABABAB
                pins.append(f"{i}{j}{i}{j}{i}{j}")
    
    # Remove duplicates while preserving order
    result = []
    seen = set()
    for pin in pins:
        if pin not in seen and len(pin) == 6 and pin.isdigit():
            result.append(pin)
            seen.add(pin)
    
    return result


def add_custom_pins(pins_list, custom_pins):
    """Tambahkan custom PIN ke awal list"""
    seen = set(pins_list)
    new_pins = []
    
    for pin in custom_pins:
        pin = pin.strip()
        if pin.isdigit() and pin not in seen:
            new_pins.append(pin)
            seen.add(pin)
    
    # Letakkan custom PIN di awal
    return new_pins + pins_list


def save_pins(pins, filename, header=""):
    """Simpan PIN list ke file"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w') as f:
        if header:
            f.write(f"# {header}\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total PIN: {len(pins):,}\n")
            f.write("#" + "="*60 + "\n")
        
        for pin in pins:
            f.write(f"{pin}\n")
    
    print(f"[+] Saved {len(pins):,} PIN to {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate PIN list untuk Samsung bruteforce',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh:
  # Generate semua 4-digit PIN (10000)
  python3 pin_generator.py -p 4 -o pins/pins-4-digit.txt

  # Generate semua 6-digit PIN (1000000)
  python3 pin_generator.py -p 6 -o pins/pins-6-digit.txt

  # Generate smart 4-digit PIN (prioritas tinggi, ~500 PIN)
  python3 pin_generator.py -p 4 --smart -o pins/pins-4-smart.txt

  # Generate dengan custom PIN di awal
  python3 pin_generator.py -p 4 --custom "1234,5678,9999" -o pins/custom.txt

  # Generate dan tampilkan statistik
  python3 pin_generator.py -p 4 --stats
        """
    )
    
    parser.add_argument('-p', '--pin-length', type=int, choices=[4, 6], default=4,
                        help='Panjang PIN (4 atau 6 digit)')
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='Output file path')
    parser.add_argument('--smart', action='store_true',
                        help='Generate hanya PIN dengan prioritas tinggi')
    parser.add_argument('--custom', type=str, default=None,
                        help='Custom PINs (comma-separated) - akan diletakkan di awal')
    parser.add_argument('--stats', action='store_true',
                        help='Tampilkan statistik saja')
    parser.add_argument('--all', action='store_true',
                        help='Generate semua (4-digit full, 6-digit full, smart)')
    
    args = parser.parse_args()
    
    # Mode: generate semua
    if args.all:
        print("\n" + "="*60)
        print("  GENERATE SEMUA PIN LIST")
        print("="*60)
        
        print("\n[*] Generating 4-digit PIN (full)...")
        pins_4 = generate_4digit_pins()
        save_pins(pins_4, "pins/pins-4-digit.txt", "4-digit PIN list (full)")
        
        print("\n[*] Generating 6-digit PIN (full)...")
        pins_6 = generate_6digit_pins()
        save_pins(pins_6, "pins/pins-6-digit.txt", "6-digit PIN list (full)")
        
        print("\n[*] Generating 4-digit PIN (smart)...")
        pins_4_smart = generate_smart_4digit_pins()
        save_pins(pins_4_smart, "pins/pins-4-smart.txt", "4-digit PIN list (smart)")
        
        print("\n[*] Generating 6-digit PIN (smart)...")
        pins_6_smart = generate_smart_6digit_pins()
        save_pins(pins_6_smart, "pins/pins-6-smart.txt", "6-digit PIN list (smart)")
        
        print("\n" + "="*60)
        print("  SELESAI!")
        print("="*60)
        return
    
    # Generate PIN berdasarkan args
    if args.pin_length == 4:
        if args.smart:
            pins = generate_smart_4digit_pins()
            header = "4-digit PIN list (smart - high priority)"
        else:
            pins = generate_4digit_pins()
            header = "4-digit PIN list (full)"
    else:
        if args.smart:
            pins = generate_smart_6digit_pins()
            header = "6-digit PIN list (smart - high priority)"
        else:
            pins = generate_6digit_pins()
            header = "6-digit PIN list (full)"
    
    # Tambahkan custom PIN jika ada
    if args.custom:
        custom_pins = [p.strip() for p in args.custom.split(',')]
        pins = add_custom_pins(pins, custom_pins)
        print(f"[+] Added {len(custom_pins)} custom PIN(s) to the beginning")
    
    # Tampilkan statistik
    if args.stats:
        print("\n" + "="*60)
        print(f"  {args.pin_length}-DIGIT PIN STATISTICS")
        print("="*60)
        print(f"  Total PIN generated: {len(pins):,}")
        print(f"  First 10 PINs: {pins[:10]}")
        print(f"  Last 10 PINs:  {pins[-10:]}")
        print("="*60)
        return
    
    # Save ke file
    if args.output:
        save_pins(pins, args.output, header)
    else:
        # Default output
        suffix = "-smart" if args.smart else ""
        output = f"pins/pins-{args.pin_length}-digit{suffix}.txt"
        save_pins(pins, output, header)


if __name__ == '__main__':
    main()