import streamlit as st
import pandas as pd
import uuid

from datetime import date, datetime, timedelta
from modules.db import connect_db


def get_calendar_data():

    conn = connect_db()

    query = """
        SELECT
            ce.id AS calendar_event_id,
            ce.activity_id,
            ce.event_date,
            ce.event_time,
            ce.event_status,
            ce.created_from,

            a.activity,
            a.establishment,
            a.website_url,
            a.suggested_by,
            a.estimated_cost,
            a.address,
            a.activity_category,
            a.timing_type

        FROM calendar_events ce

        JOIN activities a
            ON ce.activity_id = a.id

        ORDER BY ce.event_date, ce.event_time
    """

    calendar_df = pd.read_sql_query(query, conn)

    responses_df = pd.read_sql_query(
        "SELECT * FROM responses",
        conn
    )

    users_df = pd.read_sql_query(
        "SELECT name, email, colour FROM users",
        conn
    )

    conn.close()

    return calendar_df, responses_df, users_df


def add_response(
    activity_id,
    responder,
    response,
    counter_date="",
    counter_time=""
):

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        """
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
        """,
        (
            str(uuid.uuid4()),
            activity_id,
            responder,
            response,
            counter_date,
            counter_time,
            datetime.now().isoformat(timespec="seconds")
        )
    )

    conn.commit()
    conn.close()


def latest_response_for_person(
    responses_df,
    activity_id,
    person
):

    person_responses = responses_df[
        (responses_df["activity_id"] == activity_id)
        &
        (responses_df["responder"] == person)
    ].copy()

    if person_responses.empty:
        return None

    person_responses = person_responses.sort_values(
        "created_at",
        ascending=False
    )

    return person_responses.iloc[0]["response"]


def get_going_people(
    responses_df,
    activity_id
):

    activity_responses = responses_df[
        responses_df["activity_id"] == activity_id
    ].copy()

    if activity_responses.empty:
        return []

    activity_responses = activity_responses.sort_values(
        "created_at"
    )

    latest_by_person = activity_responses.groupby(
        "responder"
    ).tail(1)

    going = latest_by_person[
        latest_by_person["response"] == "Call me committed"
    ]

    return going["responder"].tolist()


def get_rejected_people(
    responses_df,
    activity_id
):

    activity_responses = responses_df[
        responses_df["activity_id"] == activity_id
    ].copy()

    if activity_responses.empty:
        return []

    activity_responses = activity_responses.sort_values(
        "created_at"
    )

    latest_by_person = activity_responses.groupby(
        "responder"
    ).tail(1)

    rejected = latest_by_person[
        latest_by_person["response"] == "Girl no"
    ]

    return rejected["responder"].tolist()


def create_ics_content(row):

    title = f"{row['activity']} at {row['establishment']}"

    event_date = row["event_date"]

    event_time = row["event_time"] or "19:00"

    start = datetime.strptime(
        f"{event_date} {event_time}",
        "%Y-%m-%d %H:%M"
    )

    end = start + timedelta(hours=2)

    start_ics = start.strftime("%Y%m%dT%H%M%S")
    end_ics = end.strftime("%Y%m%dT%H%M%S")

    description = (
        f"Suggested by: {row['suggested_by']}\\n"
        f"Cost: {row['estimated_cost']}\\n"
        f"Website: {row['website_url']}"
    )

    ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Subordinates//Calendar Event//EN

BEGIN:VEVENT
UID:{row['calendar_event_id']}@subordinates
DTSTAMP:{datetime.now().strftime("%Y%m%dT%H%M%S")}
DTSTART:{start_ics}
DTEND:{end_ics}

SUMMARY:{title}
LOCATION:{row['address']}
DESCRIPTION:{description}

END:VEVENT
END:VCALENDAR
"""

    return ics


def render_event_card(
    row,
    responses_df,
    users_df,
    user
):

    going_people = get_going_people(
        responses_df,
        row["activity_id"]
    )

    rejected_people = get_rejected_people(
        responses_df,
        row["activity_id"]
    )

    user_response = latest_response_for_person(
        responses_df,
        row["activity_id"],
        user["name"]
    )

    suggester_colour = "#f2c6c2"

    user_match = users_df[
        users_df["name"] == row["suggested_by"]
    ]

    if not user_match.empty:
        suggester_colour = user_match.iloc[0]["colour"]

    is_solid = len(going_people) >= 1

    background_colour = "#ffffff"

    if user_response == "Girl no":
        background_colour = "#d9d9d9"

    elif is_solid:
        background_colour = suggester_colour

    event_time = row["event_time"] if row["event_time"] else "TBD"

    opacity = "0.45" if user_response == "Girl no" else "1"

    st.markdown(
f"""
<div style="
background-color:{background_colour};
padding:20px;
border-radius:18px;
margin-bottom:20px;
border-left:8px solid {suggester_colour};
box-shadow:0 4px 12px rgba(0,0,0,0.08);
opacity:{opacity};
">

<h3 style="margin-bottom:10px;">
{row['activity']} — {row['establishment']}
</h3>

<p>
<b>Date:</b> {row['event_date']} at {event_time}
</p>

<p>
<b>Suggested by:</b> {row['suggested_by']}
</p>

<p>
<b>Type:</b> {row['activity_category']}
&nbsp; | &nbsp;
<b>Status:</b> {row['event_status']}
</p>

<p>
<b>Estimated cost:</b> {row['estimated_cost']}
</p>

<p>
<b>Address:</b> {row['address']}
</p>

</div>
""",
unsafe_allow_html=True
    )

    if row["website_url"]:

        st.markdown(
            f"""
<a href="{row['website_url']}" target="_blank">
Open website
</a>
""",
            unsafe_allow_html=True
        )

    if going_people:

        st.success(
            "Who's going: " + ", ".join(going_people)
        )

    if rejected_people:

        st.caption(
            "Rejected: " + ", ".join(rejected_people)
        )

    if user_response:

        st.info(
            f"Your current response: {user_response}"
        )

    st.write("")

    col1, col2, col3 = st.columns([1, 1.3, 1])

    with col1:

        if st.button(
            "Call me committed",
            key=f"commit_{row['calendar_event_id']}"
        ):

            add_response(
                row["activity_id"],
                user["name"],
                "Call me committed"
            )

            st.success("You are committed.")

            st.rerun()

    with col2:

        counter_date = st.date_input(
            "Counter date",
            value=date.today(),
            key=f"counter_date_{row['calendar_event_id']}"
        )

        counter_time = st.time_input(
            "Counter time",
            key=f"counter_time_{row['calendar_event_id']}"
        )

        if st.button(
            "I could be down",
            key=f"could_{row['calendar_event_id']}"
        ):

            add_response(
                row["activity_id"],
                user["name"],
                "I could be down",
                counter_date.isoformat(),
                counter_time.strftime("%H:%M")
            )

            st.warning("Counter time saved.")

            st.rerun()

    with col3:

        if st.button(
            "Girl no",
            key=f"no_{row['calendar_event_id']}"
        ):

            add_response(
                row["activity_id"],
                user["name"],
                "Girl no"
            )

            st.error("Rejected.")

            st.rerun()

    if (
        user["name"] in going_people
        or user["name"] == row["suggested_by"]
    ):

        ics_content = create_ics_content(row)

        st.download_button(
            label="Download Apple Calendar Invite",
            data=ics_content,
            file_name=f"{row['activity']}_{row['event_date']}.ics",
            mime="text/calendar",
            key=f"ics_{row['calendar_event_id']}"
        )

    st.divider()


def render_shared_calendar(user):

    st.header("Shared Calendar")

    st.caption(
        "This shows fixed-date events and confirmed suggested events for the next three months."
    )

    calendar_df, responses_df, users_df = get_calendar_data()

    if calendar_df.empty:

        st.info(
            "No calendar events yet."
        )

        return

    today = date.today()

    end_date = today + timedelta(days=90)

    calendar_df["event_date_obj"] = pd.to_datetime(
        calendar_df["event_date"],
        errors="coerce"
    ).dt.date

    calendar_df = calendar_df[
        (calendar_df["event_date_obj"] >= today)
        &
        (calendar_df["event_date_obj"] <= end_date)
    ]

    if calendar_df.empty:

        st.info(
            "No events in the next three months."
        )

        return

    view_mode = st.radio(
        "Calendar view",
        [
            "Upcoming list",
            "Month-style grouped view"
        ],
        horizontal=True
    )

    if view_mode == "Upcoming list":

        for _, row in calendar_df.iterrows():

            render_event_card(
                row,
                responses_df,
                users_df,
                user
            )

    else:

        grouped = calendar_df.groupby("event_date")

        for event_date, day_events in grouped:

            st.subheader(event_date)

            for _, row in day_events.iterrows():

                render_event_card(
                    row,
                    responses_df,
                    users_df,
                    user
                )