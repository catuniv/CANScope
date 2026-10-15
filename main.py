import threading
from simulator.ecu_simulator import run_simulator
from core.receiver import run_receiver

receiver_thread = threading.Thread(
    target = run_receiver
)

simulator_thread = threading.Thread(
    target = run_simulator
)

receiver_thread.start()
simulator_thread.start()

receiver_thread.join()
simulator_thread.join()
