import streamlit as st
import time
from datetime import datetime, timedelta
from dateutil import parser
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
# Define default variables
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
           "plasma": 300} # in Watts
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

# IP Address of the Cito Plus RF generator, connected by Ethernet
cito_address = "169.254.1.1"
citoctrl = cb.CitoBase(host_mode=0, host_addr=cito_address) # 0 for Ethernet

# For writing into the log at the end of the recipe, 
# whether it's a normal or forced ending
if 'logname' not in st.session_state:
    st.session_state['logname'] = ''
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = ''
if 'cycle_time' not in st.session_state:
    st.session_state['cycle_time'] = ''


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
        st.info(f"Setpoint: {plasma} W - Value: {citoctrl.get_power_setpoint_watts()[1]} W")
        if logname is not None:
            write_to_log(logname, plasma_active="Yes")
    else:
        st.error("Can't open connection to the RF generator.")
        if logname is not None:
            write_to_log(logname, plasma_active="No")
        return(False)


def HV_ON():
    """
    Turn HV on
    """
    if citoctrl.open():
        citoctrl.set_rf_on()


def HV_OFF():
    """
    Turn HV off
    """
    if citoctrl.open():
        citoctrl.set_rf_off()  # turn off the rf


def initialize():
    """
    Make sure the relays are closed
    """
    turn_OFF(RelPrec1)
    turn_OFF(RelPrec2)


def append_to_file(logfile="log.txt", text=""):
    """
    Function to easily append text to a logfile
    """
    with open(logfile, 'a') as fd:
        fd.write(f'{text}\n')


def write_to_log(logname, **kwargs):
    """
    Function to easily create and update a logfile
    """
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


def framework():
    """
    Defines the style and the positions of the printing areas
    """
    global c1, c2, remcycletext, remcycle, remcyclebar, step_print
    global remtottimetext, remtottime, remtime, final_time_text, final_time
    c1, c2 = st.columns((1, 1))
    remcycletext = c1.empty()
    remcycle = c1.empty()
    remcyclebar = c1.empty()
    step_print = c1.empty()
    remtottimetext = c2.empty()
    remtottime = c2.empty()
    remtime = c2.empty()
    final_time_text = c2.empty()
    final_time = c2.empty()
    with open("ressources/style.css") as f:
        st.markdown('<style>{}</style>'.format(f.read()),
                    unsafe_allow_html=True)


def print_tot_time(tot):
    """
    Print total estimated time and estimated ending time
    """
    finaltime = datetime.now() + timedelta(seconds=tot)
    remcycletext.write("# Total Time:\n")
    tot = int(tot)
    totmins, totsecs = divmod(tot, 60)
    tothours, totmins = divmod(totmins, 60)
    tottimer = '{:02d}:{:02d}:{:02d}'.format(tothours, totmins, totsecs)
    remcycle.markdown(
        "<div><h2><span class='highlight green'>"+tottimer+"</h2></span></div>",
        unsafe_allow_html=True)
    final_time_text.write("# Ending Time:\n")
    final_time.markdown(
        "<div><h2><span class='highlight red'>"+finaltime.strftime("%H:%M") +
        "</h2></span></div>", unsafe_allow_html=True)


def countdown(t, tot):
    """
    Print time countdown and total remaining time
    """
    remtottimetext.write("# Remaining Time:\n")
    tot = int(tot)
    while t>0:
        if t >= 1:
            mins, rest = divmod(t, 60)
            secs, mil = divmod(rest, 1)
            timer = '{:02d}:{:02d}:{:03d}'.format(int(mins), int(secs), int(mil*1000))
            remtime.markdown(
                f"<div><h2>Current step: <span class='highlight blue'>{timer}</h2></span></div>",
                unsafe_allow_html=True)
            totmins, totsecs = divmod(tot, 60)
            tothours, totmins = divmod(totmins, 60)
            tottimer = '{:02d}:{:02d}:{:02d}'.format(
                tothours, totmins, totsecs)
            remtottime.markdown(
                f"<div><h2>Total: <span class='highlight blue'>{tottimer}</h2></span></div>",
                unsafe_allow_html=True)
            time.sleep(1)
            t -= 1
            tot -= 1
        else:
            time.sleep(t)
            t -= 1


def print_step(n, steps):
    """
    Print list of steps and highlight current step
    """
    annotated_steps = steps.copy()
    if n > 0:
        annotated_steps[n-1] = "<span class='highlight green'>" + \
            annotated_steps[n-1]+"</span>"
    annotated_steps = "<br><br><div>" + \
        "<br><br>".join(annotated_steps)+"</div>"
    step_print.markdown(annotated_steps, unsafe_allow_html=True)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#  RECIPE DEFINITIONS
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def ALD(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1, plasma=1, 
        recipe="ALD", prec1="TEB", prec2="H2"):
    """
    Definition of ALD recipe
    """
    initialize()
    start_time = datetime.now().strftime(f"%Y-%m-%d-%H:%M:%S")
    st.session_state['start_time'] = start_time
    st.session_state['logname'] = f"Logs/{start_time}_{recipe}.txt"
    tot = (t1+p1+(t2+p2)*N2)*N
    st.session_state['cycle_time'] = tot/N
    write_to_log(st.session_state['logname'], recipe=recipe, start=start_time,
                   t1=t1, p1=p1, t2=t2, p2=p2, N=N, N2=N2, time_per_cycle=timedelta(seconds=st.session_state['cycle_time']))
    steps = [f"Pulse {prec1} – {int(t1*1000)} ms",
             f"Purge {prec1} – {p1} s",
             f"Pulse {prec2} – {t2} s",
             f"Purge {prec2} – {p2} s"
            ]
    for i in range(N):
        remcycletext.write("# Cycle number:\n")
        remcycle.markdown("<div><h2><span class='highlight green'>" +
                            str(i+1)+" / "+str(N)+"</h2></span></div>",
                            unsafe_allow_html=True)
        remcyclebar.progress(int((i+1)/N*100))
        turn_ON(RelPrec1)
        print_step(1, steps)
        countdown(t1, tot)
        tot = tot-t1
        turn_OFF(RelPrec1)
        print_step(2, steps)
        countdown(p1, tot)
        tot = tot-p1
        for j in range(N2):
            if N2 > 1:
                remcycle.markdown("<div><h2><span class='highlight green'>" +
                                    str(i+1)+" / "+str(N)+"</span> – " +
                                    str(j+1)+" / "+str(N2)+"</h2></div>",
                                    unsafe_allow_html=True)
            turn_ON(RelPrec2)
            print_step(3, steps)
            countdown(t2, tot)
            tot = tot-t2
            turn_OFF(RelPrec2)
            print_step(4, steps)
            countdown(p2, tot)
            tot = tot-p2
    end_time = datetime.now().strftime(f"%Y-%m-%d-%H:%M:%S")
    st.balloons()
    time.sleep(2)
    write_to_log(st.session_state['logname'], end=end_time,
                    duration=f"{parser.parse(end_time)-parser.parse(start_time)}",
                    ending="normal")
    end_recipe()


def Purge(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1, plasma=1, 
          recipe="Purge", prec1="TEB", prec2="H2"):
    """
    Definition of a Precursor 1 Purge
    """
    steps = [f"Pulse {prec1} – {t1} s"]
    initialize()
    start_time = datetime.now().strftime(f"%Y-%m-%d-%H:%M:%S")
    st.session_state['start_time'] = start_time
    st.session_state['logname'] = f"Logs/{start_time}_{recipe}.txt"
    tot = t1
    st.session_state['cycle_time'] = tot
    write_to_log(st.session_state['logname'], recipe=recipe, start=start_time,
                 t1=t1)
    turn_ON(RelPrec1)
    print_step(1, steps)
    countdown(t1, t1)
    turn_OFF(RelPrec1)
    end_time = datetime.now().strftime(f"%Y-%m-%d-%H:%M:%S")
    st.balloons()
    time.sleep(2)
    write_to_log(st.session_state['logname'], end=end_time,
                 duration=f"{parser.parse(end_time)-parser.parse(start_time)}",
                 ending="normal")
    end_recipe()


def PulsedCVD(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1, plasma=1, 
              recipe="Pulsed CVD", prec1="TEB", prec2="H2"):
    """
    Definition of pulsed CVD recipe
    """
    initialize()
    start_time = datetime.now().strftime(f"%Y-%m-%d-%H:%M:%S")
    st.session_state['start_time'] = start_time
    st.session_state['logname'] = f"Logs/{start_time}_{recipe}.txt"
    tot = (t1+p1)*N
    st.session_state['cycle_time'] = tot/N
    write_to_log(st.session_state['logname'], recipe=recipe, start=start_time,
                t1=t1, p1=p1, N=N, time_per_cycle=timedelta(seconds=st.session_state['cycle_time']))
    steps = [f"Pulse {prec1} – {int(t1*1000)} ms",
            f"Purge {prec1} – {p1} s",
            ]
    for i in range(N):
        remcycletext.write("# Cycle number:\n")
        remcycle.markdown("<div><h2><span class='highlight green'>" +
                            str(i+1)+" / "+str(N)+"</h2></span></div>",
                            unsafe_allow_html=True)
        remcyclebar.progress(int((i+1)/N*100))
        turn_ON(RelPrec1)
        print_step(1, steps)
        countdown(t1, tot)
        tot = tot-t1
        turn_OFF(RelPrec1)
        print_step(2, steps)
        countdown(p1, tot)
        tot = tot-p1
    end_time = datetime.now().strftime(f"%Y-%m-%d-%H:%M:%S")
    st.balloons()
    time.sleep(2)
    write_to_log(st.session_state['logname'], end=end_time,
                    duration=f"{parser.parse(end_time)-parser.parse(start_time)}",
                    ending="normal")
    end_recipe()


def PECVD(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1, plasma=1, 
          recipe="PECVD", prec1="TEB", prec2="H2"):
    """
    Definition of PECVD recipe
    """
    initialize()
    start_time = datetime.now().strftime(f"%Y-%m-%d-%H:%M:%S")
    st.session_state['start_time'] = start_time
    st.session_state['logname'] = f"Logs/{start_time}_{recipe}.txt"
    tot = t1
    st.session_state['cycle_time'] = tot
    write_to_log(st.session_state['logname'], recipe=recipe, start=start_time,
                 t1=t1, plasma=plasma,
                 time_per_cycle=timedelta(seconds=st.session_state['cycle_time']))
    set_plasma(plasma, st.session_state['logname'])
    steps = [f"Pulse {prec1} – {t1} s"]
    remcycletext.write(f"# Pulsing {prec1}...\n")
    turn_ON(RelPrec1)
    HV_ON()
    print_step(1, steps)
    countdown(t1, tot)
    turn_OFF(RelPrec1)
    HV_OFF()
    end_time = datetime.now().strftime(f"%Y-%m-%d-%H:%M:%S")
    st.balloons()
    time.sleep(2)
    write_to_log(st.session_state['logname'], end=end_time,
                 duration=f"{parser.parse(end_time)-parser.parse(start_time)}",
                 ending="normal")
    end_recipe()


def PulsedPECVD(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1, plasma=1, 
                recipe="Pulsed PECVD", prec1="TEB", prec2="H2"):
    """
    Definition of pulsed PECVD recipe
    """
    initialize()
    start_time = datetime.now().strftime(f"%Y-%m-%d-%H:%M:%S")
    st.session_state['start_time'] = start_time
    st.session_state['logname'] = f"Logs/{start_time}_{recipe}.txt"
    tot = (t1+p1+(t2+p2)*N2)*N
    st.session_state['cycle_time'] = tot/N
    write_to_log(st.session_state['logname'], recipe=recipe, start=start_time,
                 t1=t1, p1=p1, t2=t2, p2=p2, N=N, N2=N2, plasma=plasma,
                 time_per_cycle=timedelta(seconds=st.session_state['cycle_time']))
    set_plasma(plasma, st.session_state['logname'])
    steps = [f"Pulse {prec1} - {int(t1*1000)} ms",
             f"Purge {prec1} - {p1} s",
             f"Plasma – {t2} s",
             f"Purge – {p2} s"
             ]
    for i in range(N):
        remcycletext.write("# Cycle number:\n")
        remcycle.markdown("<div><h2><span class='highlight green'>" +
                          str(i+1)+" / "+str(N)+"</h2></span></div>",
                          unsafe_allow_html=True)
        remcyclebar.progress(int((i+1)/N*100))
        turn_ON(RelPrec1)
        print_step(1, steps)
        countdown(t1, tot)
        tot = tot-t1
        turn_OFF(RelPrec1)
        print_step(2, steps)
        countdown(p1, tot)
        tot = tot-p1
        for j in range(N2):
            if N2 > 1:
                remcycle.markdown("<div><h2><span class='highlight green'>" +
                                  str(i+1)+" / "+str(N)+"</span> – " +
                                  str(j+1)+" / "+str(N2)+"</h2></div>",
                                  unsafe_allow_html=True)
            HV_ON()
            print_step(3, steps)
            countdown(t2, tot)
            tot = tot-t2
            turn_OFF(RelPrec2)
            HV_OFF()
            print_step(4, steps)
            countdown(p2, tot)
            tot = tot-p2
    end_time = datetime.now().strftime(f"%Y-%m-%d-%H:%M:%S")
    st.balloons()
    time.sleep(2)
    write_to_log(st.session_state['logname'], end=end_time,
                 duration=f"{parser.parse(end_time)-parser.parse(start_time)}",
                 ending="normal")
    end_recipe()


def Plasma_clean(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1, plasma=1, 
                 recipe="Plasma cleaning", prec1="TEB", prec2="H2"):
    """
    Definition of a Plasma cleaning
    """
    initialize()
    steps = [f"Pulse {prec2} – {t2} s"]
    start_time = datetime.now().strftime(f"%Y-%m-%d-%H:%M:%S")
    st.session_state['start_time'] = start_time
    st.session_state['logname'] = f"Logs/{start_time}_{recipe}.txt"
    tot = t2
    st.session_state['cycle_time'] = tot
    write_to_log(st.session_state['logname'], recipe=recipe, start=start_time,
                 t2=t2, plasma=plasma)
    set_plasma(plasma, st.session_state['logname'])
    turn_ON(RelPrec2)
    HV_ON()
    print_step(1, steps)
    countdown(t2, t2)
    turn_OFF(RelPrec2)
    HV_OFF()
    end_time = datetime.now().strftime(f"%Y-%m-%d-%H:%M:%S")
    st.balloons()
    time.sleep(2)
    write_to_log(st.session_state['logname'], end=end_time,
                 duration=f"{parser.parse(end_time)-parser.parse(start_time)}",
                 ending="normal")
    end_recipe()


def PEALD(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1, plasma=1, 
          recipe="PEALD", prec1="TEB", prec2="H2"):
    """
    Definition of PEALD recipe
    """
    initialize()
    start_time = datetime.now().strftime(f"%Y-%m-%d-%H:%M:%S")
    st.session_state['start_time'] = start_time
    st.session_state['logname'] = f"Logs/{start_time}_{recipe}.txt"
    tot = (t1+p1+(t2+p2)*N2)*N
    st.session_state['cycle_time'] = tot/N
    write_to_log(st.session_state['logname'], recipe=recipe, start=start_time,
                 t1=t1, p1=p1, t2=t2, p2=p2, N=N, N2=N2, plasma=plasma,
                 time_per_cycle=timedelta(seconds=st.session_state['cycle_time']))
    set_plasma(plasma, st.session_state['logname'])
    steps = [f"Pulse {prec1} – {int(t1*1000)} ms",
             f"Purge {prec1} – {p1} s",
             f"Pulse {prec2} + Plasma – {t2} s",
             f"Purge {prec2} – {p2} s"
             ]
    for i in range(N):
        remcycletext.write("# Cycle number:\n")
        remcycle.markdown("<div><h2><span class='highlight green'>" +
                          str(i+1)+" / "+str(N)+"</h2></span></div>",
                          unsafe_allow_html=True)
        remcyclebar.progress(int((i+1)/N*100))
        turn_ON(RelPrec1)
        print_step(1, steps)
        countdown(t1, tot)
        tot = tot-t1
        turn_OFF(RelPrec1)
        print_step(2, steps)
        countdown(p1, tot)
        tot = tot-p1
        for j in range(N2):
            if N2 > 1:
                remcycle.markdown("<div><h2><span class='highlight green'>" +
                                  str(i+1)+" / "+str(N)+"</span> – " +
                                  str(j+1)+" / "+str(N2)+"</h2></div>",
                                  unsafe_allow_html=True)
            turn_ON(RelPrec2)
            HV_ON()
            print_step(3, steps)
            countdown(t2, tot)
            tot = tot-t2
            turn_OFF(RelPrec2)
            HV_OFF()
            print_step(4, steps)
            countdown(p2, tot)
            tot = tot-p2
    end_time = datetime.now().strftime(f"%Y-%m-%d-%H:%M:%S")
    st.balloons()
    time.sleep(2)
    write_to_log(st.session_state['logname'], end=end_time,
                 duration=f"{parser.parse(end_time)-parser.parse(start_time)}",
                 ending="normal")
    end_recipe()


def CVD(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1, plasma=1, recipe="CVD", prec1="TEB", prec2="H2"):
    """
    Definition of CVD recipe
    """
    initialize()
    start_time = datetime.now().strftime(f"%Y-%m-%d-%H:%M:%S")
    st.session_state['start_time'] = start_time
    st.session_state['logname'] = f"Logs/{start_time}_{recipe}.txt"
    tot = t1
    st.session_state['cycle_time'] = tot
    write_to_log(st.session_state['logname'], recipe=recipe, start=start_time,
                 t1=t1, time_per_cycle=timedelta(seconds=st.session_state['cycle_time']))
    steps = [f"Pulse {prec1} – {t1} s"]
    remcycletext.write(f"# Pulsing {prec1}...\n")
    turn_ON(RelPrec1)
    print_step(1, steps)
    countdown(t1, tot)
    turn_OFF(RelPrec1)
    end_time = datetime.now().strftime(f"%Y-%m-%d-%H:%M:%S")
    st.balloons()
    time.sleep(2)
    write_to_log(st.session_state['logname'], end=end_time,
                 duration=f"{parser.parse(end_time)-parser.parse(start_time)}",
                 ending="normal")
    end_recipe()
