Development Status

CANScope currently supports:

* Real-time CAN message analysis
* Dashboard visualization
* CAN statistics and frequency monitoring
* Real-time graphs
* CAN logging and replay
* DBC-based decoding
* CAN message transmission
* Virtual ECU simulation
* ECU online/offline monitoring

The core software prototype is now complete.

Development is temporarily paused while the physical vehicle testbed is being built.

Next Steps

STM32-based ECUs will be integrated with the vehicle for motor control, steering, encoder feedback, sensors, and real CAN communication.

After the hardware platform is completed, Raspberry Pi and SocketCAN will be added to connect CANScope to the physical CAN bus.

CAN security features, attack simulations, and IDS functionality will be added later as advanced extensions.
