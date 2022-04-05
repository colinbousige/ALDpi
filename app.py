# run with streamlit run app.py

# # # # # # # # # # # # # # # # # # # # # # # # 
# Import libraries
# # # # # # # # # # # # # # # # # # # # # # # #

import streamlit as st
from ressources.multipage import MultiPage
from ressources.setup import *
from ressources import ALDpage, PEALDpage, CVDpage, PECVDpage, PulsedCVDpage, PulsedPECVDpage, PlasmaCleanpage, Purgepage

app = MultiPage()

st.markdown(
    """
        <style>
        [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
            width: 400px;
        }
        [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
            width: 400px;
            margin-left: -400px;
        }
        </style>
        """,
    unsafe_allow_html=True
)

app.add_page("ALD", ALDpage.app)
app.add_page("PEALD", PEALDpage.app)
app.add_page("CVD", CVDpage.app)
app.add_page("Pulsed CVD", PulsedCVDpage.app)
app.add_page("PECVD", PECVDpage.app)
app.add_page("Pulsed PECVD", PulsedPECVDpage.app)
app.add_page("Plasma cleaning", PlasmaCleanpage.app)
app.add_page("Purge", Purgepage.app)

app.run()
