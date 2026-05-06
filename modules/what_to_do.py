import streamlit as st

import pandas as pd

import uuid

from datetime import datetime, date, timedelta

from modules.db import connect_db

def add_availability(activity_id, person, available_date, available_time):

    conn = connect_db()

    cur = conn.cursor()

    cur.execute("""

        INSERT INTO responses (

            id,

            activity_id,

            responder,

            response,

            counter_date,

            counter_time,

            created_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?)

    """, (

        str(uuid.uuid4()),

        activity_id,

        person,

        "Available",

        available_date,

        available_time,

        datetime.now().isoformat(timespec="seconds")

    ))

    conn.commit()

    conn.close()

def create_calendar_suggestion(activity_id, event_date, event_time):

    conn = connect_db()

    cur = conn.cursor()

    existing = cur.execute("""

        SELECT id

        FROM calendar_events

        WHERE activity_id = ? AND event_date = ? AND event_time = ?

    """, (activity_id, event_date, event_time)).fetchone()

    if existing:

        conn.close()

        return False

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

        "What should we do availability match",

        datetime.now().isoformat(timespec="seconds")

    ))

    conn.commit()

    conn.close()

    return True

def check_for_matches(activity_id):

    conn = connect_db()

    responses_df = pd.read_sql_query("""

        SELECT *

        FROM responses

        WHERE activity_id = ? AND response = 'Available'

    """, conn, params=(activity_id,))

    conn.close()

    if responses_df.empty:

        return None

    grouped = responses_df.groupby(["counter_date", "counter_time"])

    for (available_date, available_time), group in grouped:

        unique_people = group["responder"].nunique()

        if unique_people >= 2:

            return {

                "date": available_date,

                "time": available_time,

                "people": group["responder"].unique().tolist()

            }

    return None

def render_what_to_do(user):

    st.header("What should we do?")

    st.caption("This section is for activities without a final fixed date yet.")

    conn = connect_db()

    activities_df = pd.read_sql_query("""

        SELECT *

        FROM activities

        WHERE timing_type IN ('Any time', 'Fixed day')

        ORDER BY activity_category, created_at DESC

    """, conn)

    responses_df = pd.read_sql_query("""

        SELECT *

        FROM responses

        WHERE response = 'Available'

    """, conn)

    conn.close()

    if activities_df.empty:

        st.info("No flexible activities logged yet.")

        return

    for activity_category in activities_df["activity_category"].dropna().unique():

        st.subheader(activity_category)

        category_df = activities_df[activities_df["activity_category"] == activity_category]

        for _, row in category_df.iterrows():

            with st.expander(f"{row['activity']} — {row['establishment']}"):

                st.write(f"**Suggested by:** {row['suggested_by']}")

                st.write(f"**Timing type:** {row['timing_type']}")

                st.write(f"**Cost:** {row['estimated_cost']}")

                st.write(f"**Address:** {row['address']}")

                st.write(f"**Website:** {row['website_url']}")

                if row["timing_type"] == "Fixed day":

                    st.write(f"**Available days:** {row['fixed_days']}")

                    st.write(f"**Available times:** {row['fixed_day_times']}")

                st.write("**Suggested options from original logger:**")

                st.write(f"1. {row['preferred_option_1_date']} at {row['preferred_option_1_time']}")

                if row["preferred_option_2_date"]:

                    st.write(f"2. {row['preferred_option_2_date']} at {row['preferred_option_2_time']}")

                if row["preferred_option_3_date"]:

                    st.write(f"3. {row['preferred_option_3_date']} at {row['preferred_option_3_time']}")

                max_date = date.today() + timedelta(days=60)

                col1, col2 = st.columns(2)

                with col1:

                    available_date = st.date_input(

                        "I am free on",

                        value=date.today(),

                        min_value=date.today(),

                        max_value=max_date,

                        key=f"available_date_{row['id']}"

                    )

                with col2:

                    available_time = st.time_input(

                        "At around",

                        key=f"available_time_{row['id']}"

                    )

                if st.button("Add my availability", key=f"add_availability_{row['id']}"):

                    add_availability(

                        row["id"],

                        user["name"],

                        available_date.isoformat(),

                        available_time.strftime("%H:%M")

                    )

                    match = check_for_matches(row["id"])

                    if match:

                        created = create_calendar_suggestion(

                            row["id"],

                            match["date"],

                            match["time"]

                        )

                        if created:

                            st.success(

                                f"Match found with {', '.join(match['people'])}. "

                                f"This has been added to the shared calendar as a suggestion."

                            )

                        else:

                            st.info("This matched time is already on the shared calendar.")

                    else:

                        st.success("Availability added.")

                    st.rerun()

                existing = responses_df[responses_df["activity_id"] == row["id"]]

                if not existing.empty:

                    st.write("**Current availability added:**")

                    st.dataframe(

                        existing[["responder", "counter_date", "counter_time", "created_at"]],

                        use_container_width=True

                    )