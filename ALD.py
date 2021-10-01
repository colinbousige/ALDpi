# run with streamlit run ALD.py

import streamlit as st
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

st.title("""
ALD – CVD Process
""")
c1, c2 = st.columns((1, 1))

PinPrec1 = 1
PinPrec2 = 2
PinS1 = 3
PinS2 = 4

remtottimetext = c2.empty()
remtottime = c2.empty()
remtimetext = c2.empty()
remtime = c2.empty()
remcycletext = c1.empty()
remcycle = c1.empty()
step = c1.empty()
step_print = c1.empty()

# import RPi.GPIO as GPIO

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(17, GPIO.OUT)
# GPIO.output(17, GPIO.LOW)

# time.sleep(0.25)

# GPIO.output(17, GPIO.HIGH)
# GPIO.cleanup()

# define the countdown func.

def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()),
                    unsafe_allow_html=True)

local_css("style.css")

def print_tot_time(tot):
    finaltime = datetime.now() + timedelta(seconds=tot)
    remcycletext.write("# Total Estimated Time:\n")
    tot = int(tot)
    totmins, totsecs = divmod(tot, 60)
    tothours, totmins = divmod(totmins, 60)
    tottimer = '{:02d}:{:02d}:{:02d}'.format(
                tothours, totmins, totsecs)
    remcycle.markdown(
        "<div><h2><span class='highlight blue'>"+tottimer+"</h2></span></div>", unsafe_allow_html=True)
    remtottimetext.write("# Estimated Ending Time:\n")
    remtottime.markdown(
        "<div><h2><span class='highlight red'>"+finaltime.strftime("%H:%M")+"</h2></span></div>", unsafe_allow_html=True)

def countdown(t, tot):
    remtottimetext.write("# Total Remaining Time:\n")
    remtimetext.write("# Remaining time in current step:\n")
    tot = int(tot)
    if t>1:
        while t:
            mins, secs = divmod(t, 60)
            timer = '## {:02d}:{:02d}'.format(mins, secs)
            remtime.write(timer, end="\r")
            totmins, totsecs = divmod(tot, 60)
            tothours, totmins = divmod(totmins, 60)
            tottimer = '{:02d}:{:02d}:{:02d}'.format(tothours, totmins, totsecs)
            remtottime.markdown(
                "<div><h2><span class='highlight red'>"+tottimer+"</h2></span></div>", unsafe_allow_html=True)
            time.sleep(1)
            t -= 1
            tot -= 1
    else:
        time.sleep(t)

def open_relay(Pin):
    print(str(Pin)+' opened')
    # GPIO.output(Pin, GPIO.HIGH)

def close_relay(Pin):
    print(str(Pin)+' closed')
    # GPIO.output(Pin, GPIO.LOW)

def HV_ON():
    open_relay(PinS2)
    time.sleep(0.05)
    close_relay(PinS2)

def HV_OFF():
    open_relay(PinS1)
    time.sleep(0.05)
    close_relay(PinS1)

def print_step(n, steps):
    annotated_steps = steps.copy()
    if n>0:
        annotated_steps[n-1] = "<span class='highlight blue'>"+annotated_steps[n-1]+"</span>"
    annotated_steps = "<br><br><div>"+"<br><br>".join(annotated_steps)+"</div>"
    step_print.markdown(annotated_steps, unsafe_allow_html=True)

def ALD(t1=0.015, p1=40, t2=10, p2=40, N=100):
    """
    Definition of ALD recipe
    """
    close_relay(PinPrec1)
    close_relay(PinPrec2)
    HV_OFF()
    steps = ["Pulse Precursor 1 – "+str(int(t1*1000))+"ms",
             "Purge Precursor 1 – "+str(p1)+"s",
             "Pulse Precursor 2 – "+str(t2)+"s",
             "Purge Precursor 2 – "+str(p2)+"s"
             ]
    tot = (t1+t2+p1+p2)*N
    print("\nStarting ALD procedure...\n")
    for i in range(N):
        remcycletext.write("# Cycle number:\n")
        remcycle.write('# '+str(i+1)+" / "+str(N))
        open_relay(PinPrec1)
        print_step(1, steps)
        countdown(t1, tot); tot=tot-t1
        close_relay(PinPrec1)
        print_step(2, steps)
        countdown(p1, tot); tot=tot-p1
        open_relay(PinPrec2)
        print_step(3, steps)
        countdown(t2, tot); tot=tot-t2
        close_relay(PinPrec2)
        print_step(4, steps)
        countdown(p2, tot); tot=tot-p2


def PEALD(t1=0.015, p1=40, t2=10, p2=40, N=100):
    """
    Definition of PEALD recipe
    """
    close_relay(PinPrec1)
    close_relay(PinPrec2)
    HV_OFF()
    tot = (t1+t2+p1+p2)*N
    steps = ["Pulse Precursor 1 – "+str(int(t1*1000))+"ms",
             "Purge Precursor 1 – "+str(p1)+"s",
             "Pulse Precursor 2 + Plasma – "+str(t2)+"s",
             "Purge Precursor 2 – "+str(p2)+"s"
             ]
    print("\nStarting PEALD procedure...\n")
    for i in range(N):
        remcycletext.write("# Cycle number:\n")
        remcycle.write('# '+str(i+1))
        open_relay(PinPrec1)
        print_step(1, steps)
        countdown(t1, tot); tot=tot-t1
        close_relay(PinPrec1)
        print_step(2, steps)
        countdown(p1, tot); tot=tot-p1
        open_relay(PinPrec2)
        HV_ON()
        print_step(3, steps)
        countdown(t2, tot); tot=tot-t2
        close_relay(PinPrec2)
        HV_OFF()
        print_step(4, steps)
        countdown(p2, tot); tot=tot-p2


def CVD(t1=0.015, p1=40, t2=0, p2=0, N=100):
    """
    Definition of CVD recipe
    """
    close_relay(PinPrec1)
    close_relay(PinPrec2)
    HV_OFF()
    steps = ["Pulse Precursor 1 – "+str(int(t1*1000))+"ms",
             "Purge Precursor 1 – "+str(p1)+"s",
             ]
    tot = (t1+t2+p1+p2)*N
    print("\nStarting CVD procedure...\n")
    for i in range(N):
        remcycletext.write("# Cycle number:\n")
        remcycle.write('# '+str(i+1))
        open_relay(PinPrec1)
        print_step(1, steps)
        countdown(t1, tot); tot=tot-t1
        close_relay(PinPrec1)
        print_step(2, steps)
        countdown(p1, tot); tot=tot-p1

def PECVD(t1=0.015, p1=40, t2=10, p2=40, N=100):
    """
    Definition of PECVD recipe
    """
    close_relay(PinPrec1)
    close_relay(PinPrec2)
    HV_OFF()
    steps = ["Pulse Precursor 1 – "+str(int(t1*1000))+"ms",
             "Purge Precursor 1 – "+str(p1)+"s",
             "Plasma – "+str(t2)+"s",
             "Purge – "+str(p2)+"s"
             ]
    tot=(t1+t2+p1+p2)*N
    print("\nStarting CVD procedure...\n")
    for i in range(N):
        remcycletext.write("# Cycle number:\n")
        remcycle.write('# '+str(i+1))
        open_relay(PinPrec1)
        print_step(1, steps)
        countdown(t1, tot); tot=tot-t1
        close_relay(PinPrec1)
        print_step(2, steps)
        countdown(p1, tot); tot=tot-p1
        HV_ON()
        print_step(3, steps)
        countdown(t2, tot); tot=tot-t2
        close_relay(PinPrec2)
        HV_OFF()
        print_step(4, steps)
        countdown(p2, tot); tot=tot-p2


funcmap = {'ALD': ALD, 'PEALD': PEALD,
           'CVD': CVD, 'PECVD': PECVD}


st.sidebar.write("## Recipe Parameters")
layout = st.sidebar.columns([1, 1])
t1 = layout[0].slider("Pulse Precursor 1 (ms):", min_value=0,
                            step=1, max_value=100, value=15, key="t1")
p1 = layout[1].slider("Purge Precursor 1 (s):", min_value=0,
                        step=1, max_value=100, value=30, key="p1")
t2 = layout[0].slider("Pulse Precursor 2 (s):", min_value=0,
                        step=1, max_value=100, value=10, key="t2")
p2 = layout[1].slider("Purge Precursor 2 (s):", min_value=0,
                        step=1, max_value=100, value=40, key="p2")
N = layout[0].slider("N Cycles:", min_value=0,
                        step=1, max_value=1000, value=100, key="N")
recipe = layout[1].selectbox(
    'Select Recipe', ['ALD', 'PEALD', 'CVD', 'PECVD'], key=1)

if recipe != "CVD":
    print_tot_time((t1/1000+t2+p1+p2)*N)
else:
    print_tot_time((t1/1000+p1)*N)

layout[0].write("\n")

layout = st.sidebar.columns([1, 1])

GObutton = layout[0].button('GO')
if GObutton:
    funcmap[recipe](t1/1000, p1, t2, p2, N)
STOP = layout[1].button("STOP")
if STOP:
    close_relay(PinPrec1)
    close_relay(PinPrec2)
    HV_OFF()

