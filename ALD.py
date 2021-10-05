# run with streamlit run ALD.py

# # # # # # # # # # # # # # # # # # # # # # # # 
# Import libraries
# # # # # # # # # # # # # # # # # # # # # # # #

import streamlit as st
import time
from datetime import datetime, timedelta
# import gpiozero

# # # # # # # # # # # # # # # # # # # # # # # #
# Define pin list, output/input mode, and other variables
# # # # # # # # # # # # # # # # # # # # # # # #

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
pin_list = {"PinPrec1": 1,
            "PinPrec2": 2, 
            "PinS1": 3, 
            "PinS2": 4}
# relayPrec1 = gpiozero.OutputDevice(pin_list["PinPrec1"], active_high=True, initial_value=False)
# relayPrec2 = gpiozero.OutputDevice(pin_list["PinPrec2"], active_high=True, initial_value=False)
# relayS1 = gpiozero.OutputDevice(pin_list["PinS1"], active_high=True, initial_value=False)
# relayS2 = gpiozero.OutputDevice(pin_list["PinS2"], active_high=True, initial_value=False)

# # # # # # # # # # # # # # # # # # # # # # # #
# Define global interface setup
# # # # # # # # # # # # # # # # # # # # # # # #

st.set_page_config(layout="wide")

st.title("ALD – CVD Process")
c1, c2 = st.columns((1, 1))
remcycletext = c1.empty()
remcycle = c1.empty()
step = c1.empty()
step_print = c1.empty()
remtottimetext = c2.empty()
remtottime = c2.empty()
remtimetext = c2.empty()
remtime = c2.empty()
final_time_text = c2.empty()
final_time = c2.empty()

def local_css(file_name):
    """
    Define style from css file
    """
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()),
                    unsafe_allow_html=True)

local_css("style.css")


# # # # # # # # # # # # # # # # # # # # # # # #
# Define functions
# # # # # # # # # # # # # # # # # # # # # # # #

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
    if t>1:
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


def HV_ON():
    """
    Turn HV on
    """
    # relayS2.on()
    time.sleep(0.05)
    # relayS2.off()


def HV_OFF():
    """
    Turn HV off
    """
    # relayS1.on()
    time.sleep(0.05)
    # relayS1.off()


def end_recipe():
    """
    Ending procedure for recipes
    """
    print("...Done.")
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


def ALD(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1):
    """
    Definition of ALD recipe
    """
    # relayPrec1.off()
    # relayPrec2.off()
    HV_OFF()
    steps = ["Pulse "+prec1+" – "+str(int(t1*1000))+"ms",
             "Purge "+prec1+" – "+str(p1)+"s",
             "Pulse "+prec2+" – "+str(t2)+"s",
             "Purge "+prec2+" – "+str(p2)+"s"
             ]
    tot = (t1+p1+(t2+p2)*N2)*N
    print("\nStarting ALD procedure...\n")
    for i in range(N):
        remcycletext.write("# Cycle number:\n")
        remcycle.markdown("<div><h2><span class='highlight green'>"+
                           str(i+1)+" / "+str(N)+"</h2></span></div>", 
                           unsafe_allow_html=True)
        # relayPrec1.on()
        print_step(1, steps)
        countdown(t1, tot); tot=tot-t1
        # relayPrec1.off()
        print_step(2, steps)
        countdown(p1, tot); tot=tot-p1
        for j in range(N2):
            if N2 > 1:
                remcycle.markdown("<div><h2><span class='highlight green'>" +
                                  str(i+1)+" / "+str(N)+"</span> – " +
                                  str(j+1)+" / "+str(N2)+"</h2></div>",
                                  unsafe_allow_html=True)
            # relayPrec2.on()
            print_step(3, steps)
            countdown(t2, tot); tot=tot-t2
            # relayPrec2.off()
            print_step(4, steps)
            countdown(p2, tot); tot=tot-p2
    end_recipe()


def PEALD(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1):
    """
    Definition of PEALD recipe
    """
    # relayPrec1.off()
    # relayPrec2.off()
    HV_OFF()
    tot = (t1+p1+(t2+p2)*N2)*N
    steps = ["Pulse "+prec1+" – "+str(int(t1*1000))+"ms",
             "Purge "+prec1+" – "+str(p1)+"s",
             "Pulse "+prec2+" + Plasma – "+str(t2)+"s",
             "Purge "+prec2+" – "+str(p2)+"s"
             ]
    print("\nStarting PEALD procedure...\n")
    for i in range(N):
        remcycletext.write("# Cycle number:\n")
        remcycle.markdown("<div><h2><span class='highlight green'>" +
                          str(i+1)+" / "+str(N)+"</h2></span></div>",
                          unsafe_allow_html=True)
        # relayPrec1.on()
        print_step(1, steps)
        countdown(t1, tot); tot=tot-t1
        # relayPrec1.off()
        print_step(2, steps)
        countdown(p1, tot); tot=tot-p1
        for j in range(N2):
            if N2 > 1:
                remcycle.markdown("<div><h2><span class='highlight green'>" +
                                  str(i+1)+" / "+str(N)+"</span> – " +
                                  str(j+1)+" / "+str(N2)+"</h2></div>",
                                  unsafe_allow_html=True)
            # relayPrec2.on()
            HV_ON()
            print_step(3, steps)
            countdown(t2, tot); tot=tot-t2
            # relayPrec2.off()
            HV_OFF()
            print_step(4, steps)
            countdown(p2, tot); tot=tot-p2
    end_recipe()


def CVD(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1):
    """
    Definition of CVD recipe
    """
    # relayPrec1.off()
    # relayPrec2.off()
    HV_OFF()
    steps = ["Pulse "+prec1+" – "+str(int(t1*1000))+"ms",
             "Purge "+prec1+" – "+str(p1)+"s",
             ]
    tot = (t1+p1)*N
    print("\nStarting CVD procedure...\n")
    for i in range(N):
        remcycletext.write("# Cycle number:\n")
        remcycle.markdown("<div><h2><span class='highlight green'>" +
                          str(i+1)+" / "+str(N)+"</h2></span></div>",
                          unsafe_allow_html=True)
        # relayPrec1.on()
        print_step(1, steps)
        countdown(t1, tot); tot=tot-t1
        # relayPrec1.off()
        print_step(2, steps)
        countdown(p1, tot); tot=tot-p1
    end_recipe()


def PECVD(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1):
    """
    Definition of PECVD recipe
    """
    # relayPrec1.off()
    # relayPrec2.off()
    HV_OFF()
    steps = ["Pulse "+prec1+" – "+str(int(t1*1000))+"ms",
             "Purge "+prec1+" – "+str(p1)+"s",
             "Plasma – "+str(t2)+"s",
             "Purge – "+str(p2)+"s"
             ]
    tot=(t1+p1+(t2+p2)*N2)*N
    print("\nStarting CVD procedure...\n")
    for i in range(N):
        remcycletext.write("# Cycle number:\n")
        remcycle.markdown("<div><h2><span class='highlight green'>" +
                          str(i+1)+" / "+str(N)+"</h2></span></div>",
                          unsafe_allow_html=True)
        # relayPrec1.on()
        print_step(1, steps)
        countdown(t1, tot); tot=tot-t1
        # relayPrec1.off()
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
            # relayPrec2.off()
            HV_OFF()
            print_step(4, steps)
            countdown(p2, tot); tot=tot-p2
    end_recipe()


def Purge(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1):
    """
    Definition of a Precursor 1 Purge
    """
    t1 = int(t1*1000)
    steps = ["Pulse "+prec1+" – "+str(t1)+"s"]
    # relayPrec1.off()
    # relayPrec2.off()
    HV_OFF()
    # relayPrec1.on()
    print_step(1, steps)
    countdown(t1, t1)
    # relayPrec1.off()
    end_recipe()


def Plasma_clean(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1):
    """
    Definition of a Plasma cleaning
    """
    steps = ["Pulse "+prec2+" – "+str(t2)+"s"]
    # relayPrec1.off()
    # relayPrec2.off()
    HV_OFF()
    # relayPrec2.on()
    HV_ON()
    print_step(1, steps)
    countdown(t2, t2)
    # relayPrec2.off()
    HV_OFF()
    end_recipe()

# # # # # # # # # # # # # # # # # # # # # # # #
# Define interactive interface for chosing recipe parameters
# # # # # # # # # # # # # # # # # # # # # # # #
funcmap = {'ALD': ALD, 'PEALD': PEALD,
           'CVD': CVD, 'PECVD': PECVD, 
           'Purge': Purge, 'Plasma Cleaning': Plasma_clean}

# relayPrec1.off()
# relayPrec2.off()
HV_OFF()

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
    # relayPrec1.off()
    # relayPrec2.off()
    HV_OFF()
    end_recipe()

# # # # # # # # # # # # # # # # # # # # # # # #
# GO button
# # # # # # # # # # # # # # # # # # # # # # # #
GObutton = layout[1].button('GO')
if GObutton:
    funcmap[recipe](t1=t1/1000, p1=p1, t2=t2, p2=p2, N=N, N2=N2)
