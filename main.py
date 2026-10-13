import can
import time

sender = can.Bus(
    interface="virtual",
    channel="canscope"
)

receiver = can.Bus(
    interface = "virtual",
    channel="canscope"
)

rpm = 1000

for i in range(10):
    data = rpm.to_bytes(2, byteorder="big")

    message = can.Message(
        arbitration_id=0x100,
        data = data,
        is_extended_id=False
    )

    sender.send(message)
    received = receiver.recv(timeout=1.0)

    if received is not None:
        received_rpm = int.from_bytes(
            received.data,
            byteorder="big"
        )

        print(
            f"[0x{received.arbitration_id:X}] "
            f"RPM: {received_rpm} rpm"
        )

    rpm += 100
    time.sleep(0.5)

sender.shutdown()
receiver.shutdown()