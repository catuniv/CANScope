import can

def run_receiver():

    bus = can.Bus(
        interface="virtual",
        channel="canscope"
    )


    while True:
        message = bus.recv(timeout=1.0)

        if message is not None:

            # Rpm
            if message.arbitration_id == 0x100:
                rpm = int.from_bytes(
                    message.data,
                    byteorder="big"
                )
                print(f"[0x100] RPM     : {rpm} rpm")
            # Speed
            elif message.arbitration_id == 0x101:
                speed = int.from_bytes(
                    message.data,
                    byteorder="big"
                )
                print(f"[0x101] Speed   : {speed} km/h")
            # Battery
            elif message.arbitration_id == 0x102:
                battery = int.from_bytes(
                    message.data,
                    byteorder="big"
                )
                print(f"[0x102] Battery   : {battery} %\n")
                