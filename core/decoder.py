def decode_message(message):

    if message.arbitration_id == 0x100:

        rpm = int.from_bytes(
            message.data,
            byteorder="big"
        )

        return f"RPM={rpm} rpm"

    elif message.arbitration_id == 0x101:

        speed = int.from_bytes(
            message.data,
            byteorder="big"
        )

        return f"Speed={speed} km/h"

    elif message.arbitration_id == 0x102:

        battery = int.from_bytes(
            message.data,
            byteorder="big"
        )

        return f"Battery={battery} %"

    else:
        return "Unknown"