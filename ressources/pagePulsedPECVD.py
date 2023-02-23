import streamlit as st
import time
from datetime import datetime, timedelta
from dateutil import parser
from ressources.setup import *

def app():
    framework()
    initialize(wait=-1)
    
    st.sidebar.write("## Recipe Parameters")
    wait = st.sidebar.number_input("Waiting time befor starting:", min_value=0,
                            step=1, value=300, key="wait")
    
    layout = st.sidebar.columns([1, 1])

    prec1 = layout[0].text_input("Precursor 1:", Prec1, key="prec1")
    t1 = layout[0].number_input("Pulse "+prec1+" (ms):", min_value=0,
                        step=1, value=default["t1"], key="t1")
    t1 = t1/1000
    p1 = layout[0].number_input("Purge "+prec1+" (s):", min_value=0.,
                        step=1., value=default["p1"], key="p1")
    t2 = layout[1].number_input("Pulse Plasma (s):", min_value=0.,
                        step=1., value=default["t2"], key="t2")
    p2 = layout[1].number_input("Purge Plasma (s):", min_value=0.,
                        step=1., value=default["p2"], key="p2")
    N2 = layout[1].number_input("N repeat Plasma:", min_value=0,
                        step=1, value=default["N2"], key="N2")
    N = layout[1].number_input("N Cycles:", min_value=0,
                            step=1, value=default["N"], key="N")
    plasma = layout[0].number_input("Plasma power (W):", min_value=0, max_value=600,
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
        if len(st.session_state['logname']) > 0:
            duration = f"{parser.parse(end_time)-parser.parse(st.session_state['start_time'])}"
            write_to_log(st.session_state['logname'], end=end_time,
                         duration=duration,
                         ending="forced")
        end_recipe()

    # # # # # # # # # # # # # # # # # # # # # # # #
    # GO button
    # # # # # # # # # # # # # # # # # # # # # # # #
    GObutton = layout[1].button('GO')
    if GObutton:
        PulsedPECVD(t1=t1, p1=p1, t2=t2, p2=p2, N=N, N2=N2,
                    plasma=plasma, prec1=prec1, wait=wait)

