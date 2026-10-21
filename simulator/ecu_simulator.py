import can
import time

def run_simulator():

    bus = can.Bus(
        interface="virtual",
        channel="canscope"
    )

    rpm = 900
    speed = 0
    battery = 100

    rpm_direction = 1
    speed_direction = 1

    battery_count = 0

    while True:
        rpm_data = rpm.to_bytes(
            2,
            byteorder="little"
        )

        rpm_message = can.Message(
            arbitration_id = 0x100,
            data=rpm_data,
            is_extended_id = False
        )

        speed_data = speed.to_bytes(
            1,
            byteorder = "little"
        )

        speed_message = can.Message(
            arbitration_id = 0x101,
            data=speed_data,
            is_extended_id = False
        )

        battery_data = battery.to_bytes(
            1,
            byteorder = "little"
        )

        battery_message = can.Message(
            arbitration_id = 0x102,
            data=battery_data,
            is_extended_id = False
        )

        bus.send(rpm_message)
        bus.send(speed_message)
        bus.send(battery_message)

        # RPM 가속 / 감속
        rpm += 150 * rpm_direction

        if rpm >= 3500:
            rpm_direction = -1
        elif rpm <= 900:
            rpm_direction = 1

        # Speed 가속 / 감속
        speed += 3 * speed_direction

        if speed >= 80:
            speed_direction = -1
        elif speed <= 0:
            speed = 0
            speed_direction = 1

        # Battery는 천천히 감소
        battery_count += 1

        if battery_count >= 20:
            if battery > 0:
                battery -= 1
            battery_count = 0

        time.sleep(0.5)