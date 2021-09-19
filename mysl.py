
## Thepchai Srinoi 6130809121

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk

# SETTING PAGE CONFIG TO WIDE MODE
st.set_page_config(layout="wide")

# LOADING DATA
data1 = pd.read_csv('https://raw.githubusercontent.com/Maplub/odsample/master/20190101.csv')
data2 = pd.read_csv('https://raw.githubusercontent.com/Maplub/odsample/master/20190102.csv')
data3 = pd.read_csv('https://raw.githubusercontent.com/Maplub/odsample/master/20190103.csv')
data4 = pd.read_csv('https://raw.githubusercontent.com/Maplub/odsample/master/20190104.csv')
data5 = pd.read_csv('https://raw.githubusercontent.com/Maplub/odsample/master/20190105.csv')
# @st.cache(persist=True)

# PREPARED FOR VISUALIZATION
data = (((data1.append(data2)).append(data3)).append(data4)).append(data5)
data = data[['latstartl','lonstartl','timestart']]
data = data.reset_index(drop=True)
data[['date' , 'time' ]] = data['timestart'].str.split(' ',expand=True)
x = data['date'].str.split('/',expand=True)
data['timestart'] = x[2] + '/' + x[1] + '/' + x[0] + ' ' + data['time']
data['timestart'] = pd.to_datetime(data['timestart'])

# CREATING FUNCTION FOR MAPS

def map(data, lat, lon, zoom):
    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": lat,
            "longitude": lon,
            "zoom": zoom,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=data,
                get_position=["lon", "lat"],
                radius=100,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        ]
    ))

# LAYING OUT THE TOP SECTION OF THE APP
row1_1, row1_2 = st.beta_columns((2,3))

with row1_1:
    st.title("Bangkok Uber Ridesharing Data : Thepchai Srinoi")
    day_selected = st.slider("Select date of pickup", 1, 5)
    hour_selected = st.slider("Select date of pickup", 0, 23)

with row1_2:
    st.write(
    """
    ##
    Examining how Uber pickups vary over time in Bangkok and at its major landmark.
    By sliding the slider on the left you can view different slices of time and explore different transportation trends.
    """)

# FILTERING DATA BY DATE AND HOUR SELECTED
data = data[(data['timestart'].dt.day == day_selected) & (data['timestart'].dt.hour == hour_selected)]

# LAYING OUT THE MIDDLE SECTION OF THE APP WITH THE MAPS
row2_1, row2_2, row2_3, row2_4 = st.beta_columns((2,1,1,1))

# SETTING THE ZOOM LOCATIONS FOR THE LANDMARK
DONMUENGAIRPORT = [13.913312260542407, 100.60413432443109]
BTSSIAM  = [13.745893093999975, 100.53414718395867]
MOCHITBUSTERMINAL = [13.811274719071283, 100.5479664569791]
zoom_level = 12
midpoint = (np.average(data['latstartl']), np.average(data['lonstartl']))

with row2_1:
    st.write("**All Bangkok from %i:00 and %i:00**" % (hour_selected, (hour_selected + 1) % 24))
    map(data, midpoint[0], midpoint[1], 11)

with row2_2:
    st.write("**DONMUENG AIRPORT**")
    map(data, DONMUENGAIRPORT[0],DONMUENGAIRPORT[1], zoom_level)

with row2_3:
    st.write("**BTS SIAM**")
    map(data, BTSSIAM[0],BTSSIAM[1], zoom_level)

with row2_4:
    st.write("**MOCHIT BUS TERMINAL**")
    map(data, MOCHITBUSTERMINAL[0],MOCHITBUSTERMINAL[1], zoom_level)

# FILTERING DATA FOR THE HISTOGRAM
filtered = data[
    (data['timestart'].dt.hour >= hour_selected) & (data['timestart'].dt.hour < (hour_selected + 1))
    ]

hist = np.histogram(filtered['timestart'].dt.minute, bins=60, range=(0, 60))[0]

chart_data = pd.DataFrame({"minute": range(60), "pickups": hist})

# LAYING OUT THE HISTOGRAM SECTION

st.write("")

st.write("**Breakdown of rides per minute between %i:00 and %i:00**" % (hour_selected, (hour_selected + 1) % 24))

st.altair_chart(alt.Chart(chart_data)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("pickups:Q"),
        tooltip=['minute', 'pickups']
    ).configure_mark(
        opacity=0.5,
        color='red'
    ), use_container_width=True)
