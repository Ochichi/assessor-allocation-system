import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

from database import (
    create_tables,
    save_allocation,
    check_existing_allocation,
    check_school_capacity,
    get_available_schools
)


# Create database tables
create_tables()


# Page title
st.title("Assessor School Allocation System")


# Load data files

assessors = pd.read_csv(
    "data/assessors.csv"
)

schedule = pd.read_csv(
    "data/testing_schedule.csv"
)


# =========================
# LOGIN SECTION
# =========================

st.subheader("Assessor Login")

vvid = st.text_input("Enter VVID")


if st.button("Login"):

    assessor = assessors[
        assessors["VVID"].astype(str).str.strip()
        ==
        str(vvid).strip()
    ]


    if not assessor.empty:

        st.session_state.logged = True
        st.session_state.vvid = str(vvid).strip()
        st.session_state.name = assessor.iloc[0]["Name"]

        st.success(
            f"Welcome {st.session_state.name}"
        )


    else:

        st.error(
            "Invalid VVID"
        )


# =========================
# ALLOCATION SECTION
# =========================

if st.session_state.get("logged"):


    st.divider()

    st.subheader(
        "Select Testing Date"
    )


    dates = schedule[
        "Testing Date"
    ].unique()


    selected_date = st.selectbox(
        "Testing Date",
        dates
    )


    # Check if assessor already has allocation

    existing = check_existing_allocation(
        st.session_state.vvid,
        selected_date
    )


    if existing:

        st.warning(
            "You already have an allocation on this date."
        )


    else:


        # Get only available schools

        available_schools = get_available_schools(
            selected_date,
            schedule
        )


        if len(available_schools) == 0:

            st.warning(
                "No schools available on this date."
            )


        else:


            school_options = [
                f"{x['School Name']} ({x['Available Slots']} slots available)"
                for x in available_schools
            ]


            selected_school_display = st.selectbox(
                "Select School",
                school_options
            )


            school = selected_school_display.split(" (")[0]



            if st.button("Confirm Allocation"):


                # Get required assessors from schedule

                required = schedule[
                    (schedule["Testing Date"] == selected_date)
                    &
                    (schedule["School Name"] == school)
                ]["Required Assessors"].iloc[0]



                # Final capacity check

                available = check_school_capacity(
                    selected_date,
                    school,
                    required
                )



                if available:


                    save_allocation(
                        st.session_state.vvid,
                        st.session_state.name,
                        selected_date,
                        school
                    )


                    st.success(
                        "Allocation successful"
                    )


                else:


                    st.error(
                        f"{school} is already full. Please select another school."
                    )



# =========================
# ALLOCATION REPORT
# =========================

st.divider()

st.subheader(
    "Allocation Report"
)


engine = create_engine(
    "sqlite:///database/allocation.db"
)


allocations = pd.read_sql(
    "SELECT * FROM allocations",
    engine
)


st.dataframe(
    allocations
)