import cantools

db = cantools.database.load_file(
    "dbc/canscope.dbc"
)

# RPM
rpm_data = bytes([
    0xB8,
    0x0B
])

rpm_decoded = db.decode_message(
    0x100,
    rpm_data
)

print(rpm_decoded)


# Speed
speed_data = bytes([
    0x32
])

speed_decoded = db.decode_message(
    0x101,
    speed_data
)

print(speed_decoded)

# Battery
battery_data = bytes([
    0x64
])
battery_decoded = db.decode_message(
    0x102,
    battery_data
)

print(battery_decoded)