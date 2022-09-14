"""Basic functionalities to communicate over RS232 with MKS controller."""

import socket
import serial
import serial.serialutil

class MKS:
    """Basic functionalities to communicate over RS232 with MKS controller."""

    (ETHERNET, SERIAL) = (0, 1)
    ethernet_timeout = 1.0  # Ethernet timeout in seconds
    serial_timeout = 1000  # serial timeout in milliseconds
    serial_timeout = 1000  # serial timeout in milliseconds

    ##########################################################################
    # Initialization
    ##########################################################################
    def __init__(self, host_addr, host_port=None, host_mode=None,
                 host_baudrate=None, host_bytesize=None, host_parity=None,
                 host_stopbits=None):
        """
        Connect to MKS device.

        :param host_addr: device address (IP address, host name or COM port)
        :param host_port: Port for Ethernet communication
        :param host_mode: 0: Ethernet, 1: Serial communication
        """
        self.host_addr = host_addr

        # Default host port for Modbus/TCP is 502
        if host_port is None:
            self.host_port = 502
        else:
            if (host_port > 0 and host_port <= 65535):
                self.host_port = host_port
            else:
                raise ValueError(
                    'Invalid communication port ({0})'.format(host_port))

        # Try to guess communication mode (serial or Ethernet) from host_address
        # if no mode has been specified
        if host_mode is None:
            # Host addresses not starting with "COM..." are handled as Ethernet
            # addresses
            if not (self.host_addr[0:3].upper() == "COM"):
                self.host_mode = self.ETHERNET
            # Check if COM port number is in range
            else:
                try:
                    # COM port number must be in the range of 1 to 255
                    com_port_number = int(self.host_addr[3:])
                    if (com_port_number > 0) and (com_port_number <= 255):
                        self.host_mode = self.SERIAL
                # Otherwise it is an Ethernet connection
                except ValueError:
                    self.host_mode = self.ETHERNET

        # Host communication mode (serial or Ethernet) has explicitly been
        # specified
        else:
            if host_mode == self.ETHERNET:
                self.host_mode = self.ETHERNET
            elif host_mode == self.SERIAL:
                self.host_mode = self.SERIAL
            else:
                raise ValueError(
                    'Unknown communication mode ({0}).'.format(host_mode))

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

        # Set first transaction number to start with
        self.transaction_number = 0x0000

    ##########################################################################
    # Connection Handling
    ##########################################################################

    def open(self):
        """
        Open communication channel to MKS controller.

        :return: True if successful, False in case of error
        """
        # Create a TCP/IP socket
        if self.host_mode == self.ETHERNET:
            try:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.settimeout(self.ethernet_timeout)
                self._socket.connect((self.host_addr, self.host_port))
            except socket.timeout:
                return False
            except Exception:
                return False
            return True

        # Create serial socket
        elif self.host_mode == self.SERIAL:
            self._socket = serial.Serial()
            try:
                self._socket.setPort(self.host_addr)
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

        # Unknown host mode. This case should not occur.
        else:
            raise ValueError(
                'Unknown communication mode ({0}).'.format(
                    self.host_mode))

    def isopen(self):
        """
        Return status of communication channel to MKS controller.

        :return: Returns boolean value. True if channel is open, false if
        channel is closed or not initialized
        """
        state = False

        if self.host_mode == self.ETHERNET:
            try:
                if self._socket is not None:
                    return True
            except BaseException:
                pass
            return False

        elif self.host_mode == self.SERIAL:
            try:
                state = self._socket.is_open
            except Exception:
                state = False

        return state

    def close(self):
        """Terminates communication with MKS controller."""
        if self.host_mode == self.ETHERNET:
            self._socket.shutdown(2)
            self._socket.close()

        elif self.host_mode == self.SERIAL:
            self._socket.close()

    ##########################################################################
    # Communication with MKS Controller
    ##########################################################################

    def on_all(self):
        """
        ON ALL
        """
        self._socket.write(b"ON 0\r")
    
    def off_all(self):
        """
        OFF ALL
        """
        self._socket.write(b"OF 0\r")
    
    def on_channel(self, channel: int):
        """
        ON channel
        """
        if channel > 4 or channel < 0:
            raise Exception("Channel number must be between 0 and 4.")
        tosend = f"ON {channel}\r"
        self._socket.write(tosend.encode())
    
    def off_channel(self, channel: int):
        """
        OFF ALL
        """
        if channel > 4 or channel < 0:
            raise Exception("Channel number must be between 0 and 4.")
        tosend = f"OF {channel}\r"
        self._socket.write(tosend.encode())
    
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
        tosend = f"RA {channel} R\r"
        self._socket.write(tosend.encode())
        ans = self._socket.readline().decode("utf-8")
        return(sccm[str(ans)] * factor)
    
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
        tosend = f"FS {channel} {permil}\r"
        self._socket.write(tosend.encode())
    
    def get_actual_flow(self, channel: int):
        """
        Get actual flow of a channel (in SCCM)
        """
        range = self.get_range(channel)
        if channel > 4 or channel < 1:
            raise Exception("Channel number must be between 1 and 4.")
        tosend = f"FL {channel}\r"
        self._socket.write(tosend.encode())
        ans = self._socket.readline().decode("utf-8")
        return(ans / 1000 * range)


if __name__ == '__main__':  # running sample
    mks_address = "COM3"  # ip: "10.6.0.59"
    mksctrl = MKS(mks_address)
    if mksctrl.open():
        print(f"Connection is open.")
        mksctrl.close()
    else:
        print("Error: Unable to open connection to generator.")
