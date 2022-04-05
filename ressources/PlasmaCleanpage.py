import streamlit as st
import time
from datetime import datetime, timedelta
from dateutil import parser
from ressources.setup import *


def app():
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
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)


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
        if t >= 1:
            while t:
                mins, secs = divmod(t, 60)
                timer = '{:02d}:{:02d}'.format(mins, secs)
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


    def print_step(n, steps):
        """
        Print list of steps and highlight current step
        """
        annotated_steps = steps.copy()
        if n > 0:
            annotated_steps[n-1] = "<span class='highlight green'>" + \
                annotated_steps[n-1]+"</span>"
        annotated_steps = "<br><br><div>"+"<br><br>".join(annotated_steps)+"</div>"
        step_print.markdown(annotated_steps, unsafe_allow_html=True)

    def Plasma_clean(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1, plasma=1, recipe="Plasma cleaning", prec1="TEB", prec2="H2"):
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
    
    # # # # # # # # # # # # # #

    initialize()
    st.sidebar.write("## Recipe Parameters")
    layout = st.sidebar.columns([1, 1])

    prec2 = st.sidebar.text_input("Precursor 2:", "H2 + Plasma", key="prec2")
    t2 = st.sidebar.number_input("Pulse "+prec2+" (s):", min_value=0,
                        step=1, value=500, key="t2")
    plasma = st.sidebar.number_input("Plasma power (W):", min_value=0.,
                        step=1., value=default["plasma"], key="plasma")

    print_tot_time(t2)


    # # # # # # # # # # # # # # # # # # # # # # # #
    # STOP button
    # # # # # # # # # # # # # # # # # # # # # # # #
    
    test_plasma = st.sidebar.button('Test connection to RF generator')
    if test_plasma:
        set_plasma(plasma)

    layout = st.sidebar.columns([1, 1])

    STOP = layout[0].button("STOP PROCESS")
    if STOP:
        end_time = datetime.now().strftime(f"%Y-%m-%d-%H:%M:%S")
        duration = f"{parser.parse(end_time)-parser.parse(st.session_state['start_time'])}"
        duration_s = sum(int(x) * 60 ** i for i, x in enumerate(reversed(duration.split(':'))))
        cycles_done = int(duration_s / st.session_state['cycle_time'])+1
        write_to_log(st.session_state['logname'], end=end_time, 
                    duration=duration,
                    cycles_done=cycles_done,
                    ending = "forced")
        end_recipe()

    # # # # # # # # # # # # # # # # # # # # # # # #
    # GO button
    # # # # # # # # # # # # # # # # # # # # # # # #
    GObutton = layout[1].button('GO')
    if GObutton:
        Plasma_clean(t1=t1, p1=p1, t2=t2, p2=p2, N=N, N2=N2,
                     plasma=plasma, prec2=prec2)

