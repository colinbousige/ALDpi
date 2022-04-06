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

