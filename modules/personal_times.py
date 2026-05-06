import streamlit as st

import pandas as pd

import uuid

from datetime import date, time

from modules.db import connect_db

def render_personal_times(user):

    st.header("Personal Times")

    time_type = st.selectbox(

        "Type of time",

        [

            "I can't do anything - don't contact me",

            "I WANNA GO OUT"

        ]

    )

    col1, col2 = st.columns(2)

    with col1:

        start_date = st.date_input("Start date", value=date.today())

        start_time = st.time_input("Start time", value=time(18, 0))

    with col2:

        end_date = st.date_input("End date", value=date.today())

        end_time = st.time_input("End time", value=time(23, 0))

    note = st.text_input("Note")

    if st.button("Save personal time"):

        conn = connect_db()

        cur = conn.cursor()

        cur.execute("""

            INSERT INTO personal_times (

                id, person, start_date, start_time, end_date, end_time, time_type, note

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)

        """, (

            str(uuid.uuid4()),

            user["name"],

            start_date.isoformat(),

            start_time.strftime("%H:%M"),

            end_date.isoformat(),

            end_time.strftime("%H:%M"),

            time_type,

            note

        ))

        conn.commit()

        conn.close()

        st.success("Personal time saved.")

        st.rerun()

    st.subheader("Your saved times")

    conn = connect_db()

    my_times = pd.read_sql_query("""

        SELECT start_date, start_time, end_date, end_time, time_type, note

        FROM personal_times

        WHERE person = ?

        ORDER BY start_date, start_time

    """, conn, params=(user["name"],))

    conn.close()

    if my_times.empty:

        st.info("No personal times saved yet.")

    else:

        st.dataframe(my_times, use_container_width=True)