import streamlit as st
import time
from datetime import datetime, timedelta
from dateutil import parser
from ressources.setup import *


def app():
    framework()
    initialize()
    st.sidebar.write("## Recipe Parameters")
    layout = st.sidebar.columns([1, 1])

    prec1 = layout[0].text_input("Precursor 1:", Prec1, key="prec1")
    t1 = layout[0].number_input("Pulse "+prec1+" (ms):", min_value=0,
                        step=1, value=default["t1"], key="t1")
    t1 = t1/1000
    p1 = layout[0].number_input("Purge "+prec1+" (s):", min_value=0,
                        step=1, value=default["p1"], key="p1")
    prec2 = layout[1].text_input("Precursor 2 + Plasma:", Prec2, key="prec2")
    t2 = layout[1].number_input("Pulse "+prec2+" (s):", min_value=0,
                        step=1, value=default["t2"], key="t2")
    p2 = layout[1].number_input("Purge "+prec2+" (s):", min_value=0,
                        step=1, value=default["p2"], key="p2")
    N2 = layout[1].number_input("N repeat "+prec2+":", min_value=0,
                        step=1, value=default["N2"], key="N2")
    N = layout[0].number_input("N Cycles:", min_value=0,
                            step=1, value=default["N"], key="N")
    plasma = st.sidebar.number_input("Plasma power (W):", min_value=0, max_value=600,
                                step=1, value=default["plasma"], key="plasma")

    print_tot_time((t1+p1+(t2+p2)*N2)*N)
    set_plasma(plasma)

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
        PEALD(t1=t1, p1=p1, t2=t2, p2=p2, N=N, N2=N2,
              plasma=plasma, prec1=prec1, prec2=prec2)

