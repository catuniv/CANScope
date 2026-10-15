import can
import time

def run_simulator():

    bus = can.Bus(
        interface="virtual",
        channel="canscope"
    )

    rpm = 1000
    speed = 10
    battery = 100

    while True:
        rpm_data = rpm.to_bytes(
            2,
            byteorder="big"
        )

        rpm_message = can.Message(
            arbitration_id = 0x100,
            data=rpm_data,
            is_extended_id = False
        )

        speed_data = speed.to_bytes(
            1,
            byteorder = "big"
        )

        speed_message = can.Message(
            arbitration_id = 0x101,
            data=speed_data,
            is_extended_id = False
        )

        battery_data = battery.to_bytes(
            1,
            byteorder = "big"
        )

        battery_message = can.Message(
            arbitration_id = 0x102,
            data=battery_data,
            is_extended_id = False
        )

        bus.send(rpm_message)
        bus.send(speed_message)
        bus.send(battery_message)

        rpm += 100
        speed += 1

        if rpm > 3000:
            rpm = 1000
            battery -= 1

        if speed > 30:
            speed > 10

        time.sleep(0.5)