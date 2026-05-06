import streamlit as st

import pandas as pd

import uuid

from datetime import date, datetime, timedelta, time

from modules.db import (

    connect_db,

    MASTER_EXCEL_PATH,

    TYPE_1_EXCEL_PATH,

    TYPE_2_EXCEL_PATH,

    TYPE_3_EXCEL_PATH

)

def export_all_activities_to_excel():

    conn = connect_db()

    df = pd.read_sql_query("SELECT * FROM activities ORDER BY created_at DESC", conn)

    conn.close()

    df.to_excel(MASTER_EXCEL_PATH, index=False)

    df[df["timing_type"] == "Any time"].to_excel(TYPE_1_EXCEL_PATH, index=False)

    df[df["timing_type"] == "Fixed day"].to_excel(TYPE_2_EXCEL_PATH, index=False)

    df[df["timing_type"] == "Fixed date"].to_excel(TYPE_3_EXCEL_PATH, index=False)

def create_calendar_event_for_fixed_date(activity_id, event_date, event_time):

    conn = connect_db()

    cur = conn.cursor()

    cur.execute("""

        INSERT INTO calendar_events (

            id,

            activity_id,

            event_date,

            event_time,

            event_status,

            created_from,

            created_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?)

    """, (

        str(uuid.uuid4()),

        activity_id,

        event_date,

        event_time,

        "Suggestion",

        "Fixed date activity",

        datetime.now().isoformat(timespec="seconds")

    ))

    conn.commit()

    conn.close()

def render_three_options(timing_prefix, default_time):

    max_date = date.today() + timedelta(days=60)

    option_1_date = ""

    option_1_time = ""

    option_2_date = ""

    option_2_time = ""

    option_3_date = ""

    option_3_time = ""

    st.caption("Add up to three date/time options. Dates must be within the next 2 months.")

    col1, col2 = st.columns(2)

    with col1:

        option_1_date = st.date_input(

            "Option 1 date",

            value=date.today(),

            min_value=date.today(),

            max_value=max_date,

            key=f"{timing_prefix}_option1_date"

        ).isoformat()

    with col2:

        option_1_time = st.time_input(

            "Option 1 time",

            value=default_time,

            key=f"{timing_prefix}_option1_time"

        ).strftime("%H:%M")

    col3, col4 = st.columns(2)

    with col3:

        use_option_2 = st.checkbox("Add option 2", key=f"{timing_prefix}_use_option2")

        if use_option_2:

            option_2_date = st.date_input(

                "Option 2 date",

                value=date.today(),

                min_value=date.today(),

                max_value=max_date,

                key=f"{timing_prefix}_option2_date"

            ).isoformat()

    with col4:

        if use_option_2:

            option_2_time = st.time_input(

                "Option 2 time",

                value=default_time,

                key=f"{timing_prefix}_option2_time"

            ).strftime("%H:%M")

    col5, col6 = st.columns(2)

    with col5:

        use_option_3 = st.checkbox("Add option 3", key=f"{timing_prefix}_use_option3")

        if use_option_3:

            option_3_date = st.date_input(

                "Option 3 date",

                value=date.today(),

                min_value=date.today(),

                max_value=max_date,

                key=f"{timing_prefix}_option3_date"

            ).isoformat()

    with col6:

        if use_option_3:

            option_3_time = st.time_input(

                "Option 3 time",

                value=default_time,

                key=f"{timing_prefix}_option3_time"

            ).strftime("%H:%M")

    return (

        option_1_date,

        option_1_time,

        option_2_date,

        option_2_time,

        option_3_date,

        option_3_time

    )

def render_activity_log(user):

    st.header("Log a new activity")

    max_date = date.today() + timedelta(days=60)

    activity = st.text_input("Activity itself", placeholder="Bottomless brunch, pool bar, DJ night...")

    establishment = st.text_input("Name of establishment")

    website_url = st.text_input("Website URL")

    estimated_cost = st.text_input("Estimated cost", placeholder="€20, €50, free...")

    address = st.text_input("Address")

    timing_type = st.selectbox(

        "When can this activity happen?",

        [

            "Any time",

            "Fixed day",

            "Fixed date"

        ]

    )

    activity_category = st.selectbox(

        "Kind of activity",

        [

            "Bar",

            "Restaurant",

            "Night Event",

            "Active Activity/Event",

            "Coffee",

            "Art",

            "Cultural",

            "Shopping",

            "Chill",

            "Other"

        ]

    )

    fixed_event_date = ""

    fixed_event_time = ""

    fixed_days = []

    fixed_day_times = ""

    preferred_option_1_date = ""

    preferred_option_1_time = ""

    preferred_option_2_date = ""

    preferred_option_2_time = ""

    preferred_option_3_date = ""

    preferred_option_3_time = ""

    st.divider()

    if timing_type == "Any time":

        st.subheader("Preferred dates and times")

        (

            preferred_option_1_date,

            preferred_option_1_time,

            preferred_option_2_date,

            preferred_option_2_time,

            preferred_option_3_date,

            preferred_option_3_time

        ) = render_three_options("type1", time(19, 0))

    elif timing_type == "Fixed day":

        st.subheader("Fixed days and times")

        days = [

            "Monday",

            "Tuesday",

            "Wednesday",

            "Thursday",

            "Friday",

            "Saturday",

            "Sunday"

        ]

        fixed_days = st.multiselect("Select the days this activity is available", days)

        fixed_day_times = st.text_input(

            "What times on these days?",

            placeholder="Example: Sundays 12:00-16:00, Fridays after 20:00"

        )

        st.subheader("Preferred dates and times")

        (

            preferred_option_1_date,

            preferred_option_1_time,

            preferred_option_2_date,

            preferred_option_2_time,

            preferred_option_3_date,

            preferred_option_3_time

        ) = render_three_options("type2", time(12, 0))

    elif timing_type == "Fixed date":

        st.subheader("Fixed event date and time")

        col1, col2 = st.columns(2)

        with col1:

            fixed_event_date = st.date_input(

                "Event date",

                value=date.today(),

                min_value=date.today(),

                max_value=max_date,

                key="fixed_event_date"

            ).isoformat()

        with col2:

            fixed_event_time = st.time_input(

                "Event time",

                value=time(20, 0),

                key="fixed_event_time"

            ).strftime("%H:%M")

    st.divider()

    if st.button("Save activity"):

        if not activity.strip():

            st.error("Please enter the activity itself.")

            st.stop()

        if not establishment.strip():

            st.error("Please enter the establishment name.")

            st.stop()

        if timing_type == "Fixed day" and not fixed_days:

            st.error("Please select at least one fixed day.")

            st.stop()

        activity_id = str(uuid.uuid4())

        created_at = datetime.now().isoformat(timespec="seconds")

        conn = connect_db()

        cur = conn.cursor()

        cur.execute("""

            INSERT INTO activities (

                id,

                activity,

                establishment,

                website_url,

                suggested_by,

                estimated_cost,

                address,

                activity_category,

                timing_type,

                fixed_event_date,

                fixed_event_time,

                fixed_days,

                fixed_day_times,

                preferred_option_1_date,

                preferred_option_1_time,

                preferred_option_2_date,

                preferred_option_2_time,

                preferred_option_3_date,

                preferred_option_3_time,

                status,

                created_at

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (

            activity_id,

            activity,

            establishment,

            website_url,

            user["name"],

            estimated_cost,

            address,

            activity_category,

            timing_type,

            fixed_event_date,

            fixed_event_time,

            ", ".join(fixed_days),

            fixed_day_times,

            preferred_option_1_date,

            preferred_option_1_time,

            preferred_option_2_date,

            preferred_option_2_time,

            preferred_option_3_date,

            preferred_option_3_time,

            "Suggestion",

            created_at

        ))

        conn.commit()

        conn.close()

        if timing_type == "Fixed date":

            create_calendar_event_for_fixed_date(activity_id, fixed_event_date, fixed_event_time)

        export_all_activities_to_excel()

        st.success("Activity saved successfully.")

        st.info("If this was a fixed date event, it has also been added to the shared calendar.")