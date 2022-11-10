# run with streamlit run app.py

import streamlit as st
from ressources.multipage import MultiPage
from ressources.setup import *
from ressources import pageALD, pageCVD, pagePEALD, pagePECVD, pagePlasmaClean
from ressources import pagePulsedPECVD, pagePulsedCVD, pagePurge

app = MultiPage()

st.markdown(
    f'''
        <style>
            .sidebar .sidebar-content {{
                width: 400px;
            }}
        </style>
    ''',
    unsafe_allow_html=True
)

app.add_page("ALD", pageALD.app)
app.add_page("PEALD", pagePEALD.app)
app.add_page("CVD", pageCVD.app)
app.add_page("Pulsed CVD", pagePulsedCVD.app)
app.add_page("PECVD", pagePECVD.app)
app.add_page("Pulsed PECVD", pagePulsedPECVD.app)
app.add_page("Plasma cleaning", pagePlasmaClean.app)
app.add_page("Purge", pagePurge.app)

app.run()
