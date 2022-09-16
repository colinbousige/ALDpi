import ressources.mksserial as mks

mksctrl = mks.MKS('/dev/ttyUSB0')
mksctrl.open()
mksctrl.get_range(1)
mksctrl.get_corr_factor(1)
mksctrl.get_actual_flow(1)
mksctrl.set_setpoint(1, 30)
mksctrl.on_channel(1)
mksctrl.on_all()
mksctrl.get_actual_flow(1)
mksctrl.off_channel(1)
mksctrl.off_all()
mksctrl.close()


import serial

# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
	port='/dev/ttyUSB0',
	baudrate=9600,
	parity=serial.PARITY_ODD,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS
)

ser.open()
ser.isOpen()
ser.write(b"OF 0\r\n")
ser.write(b"ON 1\r\n")
ser.write(b"ON 0\r\n")


def get_corr_factor(self, channel: int):
    """
    Get correction factor of channel
    """
    if channel > 4 or channel < 1:
        raise Exception("Channel number must be between 1 and 4.")
    tosend = f"GC {channel} R\r"
    self._socket.write(tosend.encode())
    ans = self._socket.readline().decode("utf-8")
    return(float(ans))


tosend = f"GC 1 R\r\n"
ser.write(tosend.encode())
ans = ser.readline().decode("utf-8")
(float(ans)/100)
