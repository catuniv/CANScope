import threading

from simulator.engine_ecu import run_engine_ecu
from simulator.vehicle_ecu import run_vehicle_ecu
from simulator.battery_ecu import run_battery_ecu


def run_simulator():

    engine_thread = threading.Thread(
        target=run_engine_ecu,
        daemon=True
    )

    vehicle_thread = threading.Thread(
        target=run_vehicle_ecu,
        daemon=True
    )

    battery_thread = threading.Thread(
        target=run_battery_ecu,
        daemon=True
    )

    engine_thread.start()
    vehicle_thread.start()
    battery_thread.start()

    engine_thread.join()
    vehicle_thread.join()
    battery_thread.join()