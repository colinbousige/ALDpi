import streamlit as st
import smbus
import ressources.citobase as cb

st.set_page_config(
    page_title="ALD – CVD Process",
    page_icon=":hammer_and_pick:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://lmi.cnrs.fr/author/colin-bousige/',
        'Report a bug': "https://lmi.cnrs.fr/author/colin-bousige/",
        'About': """
        ## ALD – CVD Process
        Version date 2021-10-27.

        This app was made by [Colin Bousige](https://lmi.cnrs.fr/author/colin-bousige/). Contact me for support, requests, or to signal a bug.
        """
    }
)



# # # # # # # # # # # # # # # # # # # # # # # #
# Define variables
# # # # # # # # # # # # # # # # # # # # # # # #

# Relays from the hat are commanded with I2C
DEVICE_BUS = 1
DEVICE_ADDR = 0x10
bus = smbus.SMBus(DEVICE_BUS)

# Default precursor names
Prec1 = "TEB"
Prec2 = "H2"

# Default recipe values
default = {"t1": 15, # in ms
           "p1": 40, # in s
           "t2": 10, # in s
           "p2": 40, # in s
           "N": 100, # in s
           "N2": 1, # in s
           "plasma": 300.0} # in Watts
t1 = default["t1"]
p1 = default["p1"]
t2 = default["t2"]
p2 = default["p2"]
N = default["N"]
N2 = default["N2"]
plasma = default["plasma"]

# Relays attribution
RelPrec1 = 1
RelPrec2 = 2
RelS1 = 3
RelS2 = 4

# IP Address of the Cito Plus RF generator, connected by Ethernet
cito_address = "169.254.1.1"
citoctrl = cb.CitoBase(host_mode=0, host_addr=cito_address) # 0 for Ethernet

# For writing into the log at the end of the recipe, whether it's a normal or forced ending
if 'logname' not in st.session_state:
    st.session_state['logname'] = ''
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = ''
if 'cycle_time' not in st.session_state:
    st.session_state['cycle_time'] = ''

# # # # # # # # # # # # # # # # # # # # # # # #
# Define functions
# # # # # # # # # # # # # # # # # # # # # # # #

def turn_ON(relay):
    """
    Open relay from the hat with I2C command
    """
    bus.write_byte_data(DEVICE_ADDR, relay, 0xFF)


def turn_OFF(relay):
    """
    Close relay from the hat with I2C command
    """
    bus.write_byte_data(DEVICE_ADDR, relay, 0x00)


def set_plasma(plasma, logname=None):
    """
    Open the connection to the RF generator and setup the plasma power
    """
    if citoctrl.open():
        citoctrl.set_power_setpoint_watts(plasma)  # set the rf power
        st.success("Connection with RF generator OK.")
        st.info(f"RF power setpoint: {citoctrl.get_power_setpoint_watts()[1]}")
    else:
        st.error("Can't open connection to the RF generator.")
        if logname is not None:
            write_to_log(logname, plasma_active="No")
        return(False)


def HV_ON():
    """
    Turn HV on
    """
    citoctrl.set_rf_on()


def HV_OFF():
    """
    Turn HV off
    """
    citoctrl.set_rf_off()  # turn off the rf


def initialize():
    """
    Make sure the relays are closed
    """
    turn_OFF(RelPrec1)
    turn_OFF(RelPrec2)


def append_to_file(logfile="log.txt", text=""):
    with open(logfile, 'a') as fd:
        fd.write(f'{text}\n')


def write_to_log(logname, **kwargs):
    toprint = {str(key): str(value) for key, value in kwargs.items()}
    append_to_file(logname, text='\n'.join('{:15}  {}'.format(
        key, value) for key, value in toprint.items()))


def end_recipe():
    """
    Ending procedure for recipes
    """
    turn_OFF(RelPrec1)
    turn_OFF(RelPrec2)
    if citoctrl.open():
        HV_OFF()
        citoctrl.close()
    st.experimental_rerun()
