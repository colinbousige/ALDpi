"""Basic functionalities to communicate over RS232 with MKS controller."""

import socket
import serial
import serial.serialutil

class MKS:
    """Basic functionalities to communicate over RS232 with MKS controller."""

    ##########################################################################
    # Initialization
    ##########################################################################
    def __init__(self, host_port="/dev/ttyUSB0", 
                 host_baudrate=None, 
                 host_bytesize=None, 
                 host_parity=None,
                 host_stopbits=None):
        """
        Connect to MKS device.

        :param host_port: device port address
        """
        self.host_port = host_port

        # Parameters for serial communication
        if host_baudrate is None:
            self.baudrate = 9600
        else:
            self.baudrate = host_baudrate

        if host_bytesize is None:
            self.bytesize = serial.EIGHTBITS
        else:
            self.bytesize = host_bytesize

        if host_parity is None:
            self.parity = serial.PARITY_ODD
        else:
            self.parity = host_parity

        if host_stopbits is None:
            self.stopbits = serial.STOPBITS_ONE
        else:
            self.stopbits = host_stopbits


    ##########################################################################
    # Connection Handling
    ##########################################################################

    def open(self):
        """
        Open communication channel to MKS controller.

        :return: True if successful, False in case of error
        """
        self._socket = serial.Serial()
        try:
            self._socket.setPort(self.host_port)
            self._socket.baudrate = self.baudrate
            self._socket.bytesize = self.bytesize
            self._socket.parity = self.parity
            self._socket.stopbits = self.stopbits
            self._socket.open()
        except serial.serialutil.SerialException:
            return False
        except Exception:
            return False
        return True

    def isopen(self):
        """
        Return status of communication channel to MKS controller.

        :return: Returns boolean value. True if channel is open, false if
        channel is closed or not initialized
        """
        state = False
        try:
            state = self._socket.is_open
        except Exception:
            state = False

        return state

    def close(self):
        """Terminates communication with MKS controller."""
        self._socket.close()

    ##########################################################################
    # Communication with MKS Controller
    ##########################################################################

    def on_all(self):
        """
        ON ALL
        """
        self._socket.write(b"ON 0\r\n")
        self._socket.close()
        self._socket.open()
    
    def off_all(self):
        """
        OFF ALL
        """
        self._socket.write(b"OF 0\r\n")
        self._socket.close()
        self._socket.open()
    
    def on_channel(self, channel: int):
        """
        ON channel
        """
        if channel > 4 or channel < 0:
            raise Exception("Channel number must be between 0 and 4.")
        tosend = f"ON {channel}\r\n"
        self._socket.write(tosend.encode())
        self._socket.close()
        self._socket.open()
    
    def off_channel(self, channel: int):
        """
        OFF ALL
        """
        if channel > 4 or channel < 0:
            raise Exception("Channel number must be between 0 and 4.")
        tosend = f"OF {channel}\r\n"
        self._socket.write(tosend.encode())
        self._socket.close()
        self._socket.open()
    
    def get_corr_factor(self, channel: int):
        """
        Get correction factor of channel
        """
        if channel > 4 or channel < 1:
            raise Exception("Channel number must be between 1 and 4.")
        tosend = f"GC {channel} R\r\n"
        self._socket.write(tosend.encode())
        ans = self._socket.readline().decode("utf-8")
        return(float(ans)/100.0)
    
    def get_range(self, channel: int):
        """
        Get range setup of channel (in SCCM)
        """
        if channel > 4 or channel < 1:
            raise Exception("Channel number must be between 1 and 4.")
        sccm = {"0": 1.000, "1": 2.000, "2": 5.000, "3": 10.00, "4": 20.00, 
                "5": 50.00, "6": 100.0, "7": 200.0, "8": 500.0, "9": 1000, 
                "10": 2000, "11": 5000, "12": 10000, "13": 20000, "14": 50000, 
                "15": 100000, "16": 200000, "17": 400000, "18": 500000, 
                "38": 30000, "39": 300000}
        factor = self.get_corr_factor(channel)
        tosend = f"RA {channel} R\r\n"
        self._socket.write(tosend.encode())
        ans = self._socket.readline().decode("utf-8")
        return(sccm[str(int(ans))] * factor)
    
    def set_setpoint(self, channel: int, setpoint: float):
        """
        Enter setpoint of a channel (in SCCM)
        """
        range = self.get_range(channel)
        if channel > 4 or channel < 1:
            raise Exception("Channel number must be between 1 and 4.")
        if setpoint < 0 or setpoint > range:
            raise Exception(f"Setpoint must be between 0 and {range}.")
        permil = int(setpoint * 1000 / range)
        tosend = f"FS {channel} {permil}\r\n"
        self._socket.write(tosend.encode())
    
    def get_actual_flow(self, channel: int):
        """
        Get actual flow of a channel (in SCCM)
        """
        range = self.get_range(channel)
        if channel > 4 or channel < 1:
            raise Exception("Channel number must be between 1 and 4.")
        tosend = f"FL {channel}\r\n"
        self._socket.write(tosend.encode())
        ans = self._socket.readline().decode("utf-8")
        return(float(ans) / 1000 * range)


if __name__ == '__main__':  # running sample
    mks_address = "/dev/ttyUSB0"  # ip: "10.6.0.59"
    mksctrl = MKS(mks_address)
    if mksctrl.open():
        print(f"Connection is open.")
        mksctrl.close()
    else:
        print("Error: Unable to open connection to generator.")
