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

    prec1 = st.sidebar.text_input("Precursor 1 + Plasma:", Prec1)
    t1 = st.sidebar.number_input("Pulse "+prec1+" (s):", min_value=0.,
                        step=1., value=120., key="t1")
    plasma = st.sidebar.number_input("Plasma power (W):", min_value=0, max_value=600,
                                    step=1, value=default["plasma"], key="plasma")
    print_tot_time(t1)
    set_plasma(plasma)

    # # # # # # # # # # # # # # # # # # # # # # # #
    # STOP button
    # # # # # # # # # # # # # # # # # # # # # # # #

    layout = st.sidebar.columns([1, 1])

    STOP = layout[0].button("STOP PROCESS")
    if STOP:
        end_time = datetime.now().strftime(f"%Y-%m-%d-%H:%M:%S")
        duration = f"{parser.parse(end_time)-parser.parse(st.session_state['start_time'])}"
        write_to_log(st.session_state['logname'], end=end_time, 
                    duration=duration,
                    ending = "forced")
        end_recipe()

    # # # # # # # # # # # # # # # # # # # # # # # #
    # GO button
    # # # # # # # # # # # # # # # # # # # # # # # #
    GObutton = layout[1].button('GO')
    if GObutton:
        PECVD(t1=t1, p1=p1, t2=t2, p2=p2, N=N, N2=N2, plasma=plasma, prec1=prec1)

