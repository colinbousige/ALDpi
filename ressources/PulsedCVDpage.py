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
        annotated_steps = "<br><br><div>" + \
            "<br><br>".join(annotated_steps)+"</div>"
        step_print.markdown(annotated_steps, unsafe_allow_html=True)

    def PulsedCVD(t1=0.015, p1=40, t2=10, p2=40, N=100, N2=1, plasma=1, recipe="Pulsed CVD", prec1="TEB", prec2="H2"):
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

    # # # # # # # # # # # # # # 

    initialize()
    st.sidebar.write("## Recipe Parameters")
    layout = st.sidebar.columns([1, 1])

    prec1 = st.sidebar.text_input("Precursor 1:", Prec1)
    t1 = st.sidebar.number_input("Pulse "+prec1+" (ms):", min_value=0,
                        step=1, value=default["t1"], key="t1")
    t1 = t1/1000
    p1 = st.sidebar.number_input("Purge "+prec1+" (s):", min_value=0,
                        step=1, value=default["p1"], key="p1")
    N = st.sidebar.number_input("N Cycles:", min_value=0,
                        step=1, value=default["N"], key="N")

    print_tot_time((t1+p1)*N)

    # # # # # # # # # # # # # # # # # # # # # # # #
    # STOP button
    # # # # # # # # # # # # # # # # # # # # # # # #

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
        PulsedCVD(t1=t1, p1=p1, t2=t2, p2=p2, N=N, N2=N2,
                  plasma=plasma, prec1=prec1)

