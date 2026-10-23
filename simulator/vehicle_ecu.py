import can
import time


def run_vehicle_ecu():

    bus = can.Bus(
        interface="virtual",
        channel="canscope"
    )

    speed = 0
    speed_direction = 1
    ecu_name = "Vehicle ECU"
    period = 0.2

    while True:

        speed_data = speed.to_bytes(
            1,
            byteorder="little"
        )

        speed_message = can.Message(
            arbitration_id=0x101,
            data=speed_data,
            is_extended_id=False
        )

        bus.send(
            speed_message
        )

        speed += 3 * speed_direction

        if speed >= 80:
            speed_direction = -1

        elif speed <= 0:
            speed = 0
            speed_direction = 1

        time.sleep(period)