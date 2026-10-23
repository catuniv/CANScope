import can
import time


def run_battery_ecu():

    bus = can.Bus(
        interface="virtual",
        channel="canscope"
    )

    battery = 100
    battery_count = 0
    ecu_name = "Battery ECU"
    period = 1.0

    while True:

        battery_data = battery.to_bytes(
            1,
            byteorder="little"
        )

        battery_message = can.Message(
            arbitration_id=0x102,
            data=battery_data,
            is_extended_id=False
        )

        bus.send(
            battery_message
        )

        battery_count += 1

        if battery_count >= 10:

            if battery > 0:
                battery -= 1

            battery_count = 0

        time.sleep(period)