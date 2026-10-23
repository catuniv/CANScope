import can
import time


def run_engine_ecu():

    bus = can.Bus(
        interface="virtual",
        channel="canscope"
    )

    rpm = 900
    rpm_direction = 1
    ecu_name = "Engine ECU"
    period = 0.1

    while True:

        rpm_data = rpm.to_bytes(
            2,
            byteorder="little"
        )

        rpm_message = can.Message(
            arbitration_id=0x100,
            data=rpm_data,
            is_extended_id=False
        )

        bus.send(
            rpm_message
        )

        rpm += 150 * rpm_direction

        if rpm >= 3500:
            rpm_direction = -1

        elif rpm <= 900:
            rpm_direction = 1

        time.sleep(period)