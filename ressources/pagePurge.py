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
    t1 = st.sidebar.number_input("Pulse "+prec1+" (s):", min_value=0,
                        step=1, value=150, key="t1")

    print_tot_time(t1)


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
        Purge(t1=t1, p1=p1, t2=t2, p2=p2, N=N, N2=N2,
              plasma=plasma, prec1=prec1)

