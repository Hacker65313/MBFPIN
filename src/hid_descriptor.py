"""
HID Report Descriptor untuk Android Open Accessory (AOA) Touchscreen
Compatible dengan Samsung devices via USB HID
"""

# HID Touchscreen Report Descriptor - Digitizer/Stylus
# Koordinat X/Y: 0 - 10000 (normalized)
TOUCHSCREEN_REPORT_DESC = bytes([
    0x05, 0x0D,        # Usage Page (Digitizer)
    0x09, 0x02,        # Usage (Pen)
    0xA1, 0x01,        # Collection (Application)
    0x09, 0x20,        #   Usage (Stylus)
    0xA1, 0x00,        #   Collection (Physical)
    0x09, 0x42,        #     Usage (Tip Switch)
    0x09, 0x32,        #     Usage (In Range)
    0x15, 0x00,        #     Logical Minimum (0)
    0x25, 0x01,        #     Logical Maximum (1)
    0x75, 0x01,        #     Report Size (1)
    0x95, 0x02,        #     Report Count (2)
    0x81, 0x02,        #     Input (Data,Var,Abs)
    0x75, 0x01,        #     Report Size (1)
    0x95, 0x06,        #     Report Count (6)
    0x81, 0x01,        #     Input (Const,Array,Abs)
    0x05, 0x01,        #     Usage Page (Generic Desktop)
    0x09, 0x01,        #     Usage (Pointer)
    0xA1, 0x00,        #     Collection (Physical)
    0x09, 0x30,        #       Usage (X)
    0x09, 0x31,        #       Usage (Y)
    0x16, 0x00, 0x00,  #       Logical Minimum (0)
    0x26, 0x10, 0x27,  #       Logical Maximum (10000)
    0x36, 0x00, 0x00,  #       Physical Minimum (0)
    0x46, 0x10, 0x27,  #       Physical Maximum (10000)
    0x66, 0x00, 0x00,  #       Unit (None)
    0x75, 0x10,        #       Report Size (16)
    0x95, 0x02,        #       Report Count (2)
    0x81, 0x02,        #       Input (Data,Var,Abs)
    0x91, 0x02,        #       Output (Data,Var,Abs)
    0x95, 0x03,        #       Report Count (3)
    0x91, 0x02,        #       Output (Data,Var,Abs)
    0xC0,              #     End Collection
    0xC0,              #   End Collection
    0xC0,              # End Collection
])

# AOA 2.0 Control Request Constants
AOA_GET_PROTOCOL         = 51
AOA_SEND_IDENT           = 52
AOA_START_ACCESSORY      = 53
AOA_REGISTER_HID         = 54
AOA_UNREGISTER_HID       = 55
AOA_SET_HID_REPORT_DESC  = 56
AOA_SEND_HID_EVENT       = 57
AOA_AUDIO_SUPPORT        = 58

# Accessory identification strings
MANUFACTURER  = "Samsung Bruteforce Tool"
MODEL         = "PinUnlocker"
DESCRIPTION   = "Android PIN Bruteforce via HID"
VERSION       = "1.0"
URI           = "https://github.com/local"
SERIAL        = "00000001"