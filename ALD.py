# run with streamlit run ALD.py

# # # # # # # # # # # # # # # # # # # # # # # # 
# Import libraries
# # # # # # # # # # # # # # # # # # # # # # # #

import streamlit as st
import time
from datetime import datetime, timedelta
import smbus

# # # # # # # # # # # # # # # # # # # # # # # #
# App configuration
# # # # # # # # # # # # # # # # # # # # # # # #

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
# Define pin list, output/input mode, and other variables
# # # # # # # # # # # # # # # # # # # # # # # #

# Relays from the hat are commanded with I2C
DEVICE_BUS = 1
DEVICE_ADDR = 0x10
bus = smbus.SMBus(DEVICE_BUS)

Prec1 = "TEB"
Prec2 = "H2"

default = {"t1": 15,
           "p1": 40,
           "t2": 10,
           "p2": 40,
           "N": 100,
           "N2": 1}
t1 = default["t1"]
p1 = default["p1"]
t2 = default["t2"]
p2 = default["p2"]
N = default["N"]
N2 = default["N2"]

# Relays attribution
RelPrec1 = 1
RelPrec2 = 2
RelS1 = 3
RelS2 = 4

# # # # # # # # # # # # # # # # # # # # # # # #
# Define global interface setup
# # # # # # # # # # # # # # # # # # # # # # # #

st.title("ALD – CVD Process")
c1, c2          = st.columns((1, 1))
remcycletext    = c1.empty()
remcycle        = c1.empty()
remcyclebar     = c1.empty()
step            = c1.empty()
step_print      = c1.empty()
remtottimetext  = c2.empty()
remtottime      = c2.empty()
remtimetext     = c2.empty()
remtime         = c2.empty()
final_time_text = c2.empty()
final_time      = c2.empty()

with open("style.css") as f:
    st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

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


def HV_ON():
    """
    Turn HV on
    """
    turn_ON(RelS2)
    time.sleep(0.05)
    turn_OFF(RelS2)


def HV_OFF():
    """
    Turn HV off
    """
    turn_ON(RelS1)
    time.sleep(0.05)
    turn_OFF(RelS1)


def initialize():
    """
    Close the relays and shut the plasma down
    """
    turn_OFF(RelPrec1)
    turn_OFF(RelPrec2)
    HV_OFF()


def print_tot_time(tot):
    """
    Print total estimated time and estimated ending time
    """
    finaltime = datetime.now() + timedelta(seconds=tot)
    remcycletext.write("# Total Estimated Time:\n")
    tot = int(tot)
    totmins, totsecs = divmod(tot, 60)
    tothours, totmins = divmod(totmins, 60)
    tottimer = '{:02d}:{:02d}:{:02d}'.format(tothours, totmins, totsecs)
    remcycle.markdown(
        "<div><h2><span class='highlight green'>"+tottimer+"</h2></span></div>", 
        unsafe_allow_html=True)
    final_time_text.write("# Estimated Ending Time:\n")
    final_time.markdown(
        "<div><h2><span class='highlight red'>"+finaltime.strftime("%H:%M")+
        "</h2></span></div>", unsafe_allow_html=True)


def countdown(t, tot):
    """
    Print time countdown and total remaining time
    """
    remtottimetext.write("# Total Remaining Time:\n")
    remtimetext.write("# Remaining time in current step:\n")
    tot = int(tot)
    if t>=1:
        while t:
            mins, secs = divmod(t, 60)
            timer = '## {:02d}:{:02d}'.format(mins, secs)
            remtime.write(timer, end="\r")
            totmins, totsecs = divmod(tot, 60)
            tothours, totmins = divmod(totmins, 60)
            tottimer = '{:02d}:{:02d}:{:02d}'.format(tothours, totmins, totsecs)
            remtottime.markdown(
                "<div><h2><span class='highlight blue'>"+tottimer+
                "</h2></span></div>", unsafe_allow_html=True)
            time.sleep(1)
            t -= 1
            tot -= 1
    else:
        time.sleep(t)


def end_recipe():
    """
    Ending procedure for recipes
    """
    turn_OFF(RelPrec1)
    turn_OFF(RelPrec2)
    HV_OFF()
    st.experimental_rerun()


def print_step(n, steps):
    """
    Print list of steps and highlight current step
    """
    annotated_steps = steps.copy()
    if n>0:
        annotated_steps[n-1] = "<span class='highlight green'>"+annotated_steps[n-1]+"</span>"
    annotated_steps = "<br><br><div>"+"<br><br>".join(annotated_steps)+"</div>"
    step_print.markdown(annotated_steps, unsafe_allow_html=True)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# RECIPES DEFINITIONS
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def ALD(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1):
    """
    Definition of ALD recipe
    """
    initialize()
    steps = ["Pulse "+prec1+" – "+str(int(t1*1000))+"ms",
             "Purge "+prec1+" – "+str(p1)+"s",
             "Pulse "+prec2+" – "+str(t2)+"s",
             "Purge "+prec2+" – "+str(p2)+"s"
             ]
    tot = (t1+p1+(t2+p2)*N2)*N
    print("\nStarting ALD procedure...", end='')
    for i in range(N):
        remcycletext.write("# Cycle number:\n")
        remcycle.markdown("<div><h2><span class='highlight green'>"+
                           str(i+1)+" / "+str(N)+"</h2></span></div>", 
                           unsafe_allow_html=True)
        remcyclebar.progress(int((i+1)/N*100))
        turn_ON(RelPrec1)
        print_step(1, steps)
        countdown(t1, tot); tot=tot-t1
        turn_OFF(RelPrec1)
        print_step(2, steps)
        countdown(p1, tot); tot=tot-p1
        for j in range(N2):
            if N2 > 1:
                remcycle.markdown("<div><h2><span class='highlight green'>" +
                                  str(i+1)+" / "+str(N)+"</span> – " +
                                  str(j+1)+" / "+str(N2)+"</h2></div>",
                                  unsafe_allow_html=True)
            turn_ON(RelPrec2)
            print_step(3, steps)
            countdown(t2, tot); tot=tot-t2
            turn_OFF(RelPrec2)
            print_step(4, steps)
            countdown(p2, tot); tot=tot-p2
    st.balloons(); time.sleep(2)
    end_recipe()


def PEALD(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1):
    """
    Definition of PEALD recipe
    """
    initialize()
    tot = (t1+p1+(t2+p2)*N2)*N
    steps = ["Pulse "+prec1+" – "+str(int(t1*1000))+"ms",
             "Purge "+prec1+" – "+str(p1)+"s",
             "Pulse "+prec2+" + Plasma – "+str(t2)+"s",
             "Purge "+prec2+" – "+str(p2)+"s"
             ]
    print("\nStarting PEALD procedure...", end='')
    for i in range(N):
        remcycletext.write("# Cycle number:\n")
        remcycle.markdown("<div><h2><span class='highlight green'>" +
                          str(i+1)+" / "+str(N)+"</h2></span></div>",
                          unsafe_allow_html=True)
        remcyclebar.progress(int((i+1)/N*100))
        turn_ON(RelPrec1)
        print_step(1, steps)
        countdown(t1, tot); tot=tot-t1
        turn_OFF(RelPrec1)
        print_step(2, steps)
        countdown(p1, tot); tot=tot-p1
        for j in range(N2):
            if N2 > 1:
                remcycle.markdown("<div><h2><span class='highlight green'>" +
                                  str(i+1)+" / "+str(N)+"</span> – " +
                                  str(j+1)+" / "+str(N2)+"</h2></div>",
                                  unsafe_allow_html=True)
            turn_ON(RelPrec2)
            HV_ON()
            print_step(3, steps)
            countdown(t2, tot); tot=tot-t2
            turn_OFF(RelPrec2)
            HV_OFF()
            print_step(4, steps)
            countdown(p2, tot); tot=tot-p2
    st.balloons(); time.sleep(2)
    end_recipe()


def CVD(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1):
    """
    Definition of CVD recipe
    """
    initialize()
    steps = ["Pulse "+prec1+" – "+str(int(t1*1000))+"ms",
             "Purge "+prec1+" – "+str(p1)+"s",
             ]
    tot = (t1+p1)*N
    print("\nStarting CVD procedure...", end='')
    for i in range(N):
        remcycletext.write("# Cycle number:\n")
        remcycle.markdown("<div><h2><span class='highlight green'>" +
                          str(i+1)+" / "+str(N)+"</h2></span></div>",
                          unsafe_allow_html=True)
        remcyclebar.progress(int((i+1)/N*100))
        turn_ON(RelPrec1)
        print_step(1, steps)
        countdown(t1, tot); tot=tot-t1
        turn_OFF(RelPrec1)
        print_step(2, steps)
        countdown(p1, tot); tot=tot-p1
    st.balloons(); time.sleep(2)
    end_recipe()


def PECVD(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1):
    """
    Definition of PECVD recipe
    """
    initialize()
    steps = ["Pulse "+prec1+" – "+str(int(t1*1000))+"ms",
             "Purge "+prec1+" – "+str(p1)+"s",
             "Plasma – "+str(t2)+"s",
             "Purge – "+str(p2)+"s"
             ]
    tot=(t1+p1+(t2+p2)*N2)*N
    print("\nStarting CVD procedure...", end='')
    for i in range(N):
        remcycletext.write("# Cycle number:\n")
        remcycle.markdown("<div><h2><span class='highlight green'>" +
                          str(i+1)+" / "+str(N)+"</h2></span></div>",
                          unsafe_allow_html=True)
        remcyclebar.progress(int((i+1)/N*100))
        turn_ON(RelPrec1)
        print_step(1, steps)
        countdown(t1, tot); tot=tot-t1
        turn_OFF(RelPrec1)
        print_step(2, steps)
        countdown(p1, tot); tot=tot-p1
        for j in range(N2):
            if N2 > 1:
                remcycle.markdown("<div><h2><span class='highlight green'>" +
                                  str(i+1)+" / "+str(N)+"</span> – " +
                                  str(j+1)+" / "+str(N2)+"</h2></div>",
                                  unsafe_allow_html=True)
            HV_ON()
            print_step(3, steps)
            countdown(t2, tot); tot=tot-t2
            turn_OFF(RelPrec2)
            HV_OFF()
            print_step(4, steps)
            countdown(p2, tot); tot=tot-p2
    st.balloons(); time.sleep(2)
    end_recipe()


def Purge(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1):
    """
    Definition of a Precursor 1 Purge
    """
    print("\nStarting purging procedure...", end='')
    t1 = int(t1*1000)
    steps = ["Pulse "+prec1+" – "+str(t1)+"s"]
    initialize()
    turn_ON(RelPrec1)
    print_step(1, steps)
    countdown(t1, t1)
    turn_OFF(RelPrec1)
    st.balloons(); time.sleep(2)
    end_recipe()


def Plasma_clean(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1):
    """
    Definition of a Plasma cleaning
    """
    print("\nStarting Plasma cleaning procedure...", end='')
    steps = ["Pulse "+prec2+" – "+str(t2)+"s"]
    initialize()
    turn_ON(RelPrec2)
    HV_ON()
    print_step(1, steps)
    countdown(t2, t2)
    turn_OFF(RelPrec2)
    HV_OFF()
    st.balloons(); time.sleep(2)
    end_recipe()

# # # # # # # # # # # # # # # # # # # # # # # #
# Define interactive interface for chosing recipe parameters
# # # # # # # # # # # # # # # # # # # # # # # #
initialize()

funcmap = {'ALD': ALD, 'PEALD': PEALD,
           'CVD': CVD, 'PECVD': PECVD, 
           'Purge': Purge, 'Plasma Cleaning': Plasma_clean}

recipe = st.sidebar.selectbox(
    'Select Recipe', 
    ['ALD', 'PEALD', 'CVD', 'PECVD', 'Purge', 'Plasma Cleaning'], 
    key="recipe")

st.sidebar.write("## Recipe Parameters")
layout = st.sidebar.columns([1, 1])

if recipe == "ALD" or recipe == "PEALD" or recipe == "PECVD" or recipe == "CVD":
    prec1 = layout[0].text_input("Precursor 1:", Prec1)
    t1 = layout[0].slider("Pulse "+prec1+" (ms):", min_value=0,
                          step=1, max_value=100, value=default["t1"], key="t1")
    p1 = layout[0].slider("Purge "+prec1+" (s):", min_value=0,
                          step=1, max_value=100, value=default["p1"], key="p1")
    if recipe != "CVD":
        prec2text = layout[1].empty()
        if recipe == "PECVD":
            prec2 = prec2text.text_input("Precursor 2:", "Plasma")
        else:
            prec2 = prec2text.text_input("Precursor 2:", Prec2)
        t2 = layout[1].slider("Pulse "+prec2+" (s):", min_value=0,
                            step=1, max_value=100, value=default["t2"], key="t2")
        p2 = layout[1].slider("Purge "+prec2+" (s):", min_value=0,
                            step=1, max_value=100, value=default["p2"], key="p2")
        N2 = layout[1].slider("N repeat "+prec2+":", min_value=0,
                            step=1, max_value=20, value=default["N2"], key="N2")
    N = layout[0].slider("N Cycles:", min_value=0,
                            step=1, max_value=500, value=default["N"], key="N")
elif recipe == "Purge":
    prec1 = st.sidebar.text_input("Precursor 1:", Prec1)
    t1 = st.sidebar.slider("Pulse "+prec1+" (s):", min_value=0,
                          step=1, max_value=500, value=150, key="t1")
elif recipe == "Plasma Cleaning":
    prec2 = st.sidebar.text_input("Precursor 2:", "H2 + Plasma")
    t2 = st.sidebar.slider("Pulse "+prec2+" (s):", min_value=0,
                          step=1, max_value=1000, value=500, key="t2")

if recipe == "ALD" or recipe == "PEALD" or recipe == "PECVD":
    print_tot_time((t1/1000+p1+(t2+p2)*N2)*N)
elif recipe == "CVD":
    print_tot_time((t1/1000+p1)*N)
elif recipe == "Purge":
    print_tot_time(t1)
elif recipe == "Plasma Cleaning":
    print_tot_time(t2)

layout[0].write("\n")
layout = st.sidebar.columns([1, 1])

# # # # # # # # # # # # # # # # # # # # # # # #
# STOP button
# # # # # # # # # # # # # # # # # # # # # # # #
STOP = layout[0].button("STOP PROCESS")
if STOP:
    end_recipe()

# # # # # # # # # # # # # # # # # # # # # # # #
# GO button
# # # # # # # # # # # # # # # # # # # # # # # #
GObutton = layout[1].button('GO')
if GObutton:
    funcmap[recipe](t1=t1/1000, p1=p1, t2=t2, p2=p2, N=N, N2=N2)
