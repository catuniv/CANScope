import can
import time
from core.decoder import decode_message

def run_receiver(on_message):

    bus = can.Bus(
        interface="virtual",
        channel="canscope"
    )

    start_time = time.time()
    message_count = 0


    while True:
        message = bus.recv(timeout=1.0)

        if message is not None:
            message_count += 1
            data_hex = message.data.hex(" ").upper()
            timestamp = time.time() - start_time
            decoded = decode_message(message)

            can_id = f"0x{message.arbitration_id:X}"

            on_message(
                timestamp,
                can_id,
                message.dlc,
                data_hex,
                decoded
                )

            if message.arbitration_id == 0x102:
                print()

