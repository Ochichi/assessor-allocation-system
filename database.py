from sqlalchemy import create_engine, text
import os


# Create database folder
os.makedirs("database", exist_ok=True)


# Create database connection
engine = create_engine(
    "sqlite:///database/allocation.db"
)


# Create allocation table

def create_tables():

    with engine.connect() as conn:

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vvid TEXT,
            assessor_name TEXT,
            testing_date TEXT,
            school_name TEXT,
            allocated_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """))

        conn.commit()



# Save assessor allocation

def save_allocation(vvid, name, date, school):

    with engine.connect() as conn:

        conn.execute(
            text("""
            INSERT INTO allocations
            (
                vvid,
                assessor_name,
                testing_date,
                school_name
            )
            VALUES
            (
                :vvid,
                :name,
                :date,
                :school
            )
            """),
            {
                "vvid": vvid,
                "name": name,
                "date": date,
                "school": school
            }
        )

        conn.commit()



# Check if assessor already has allocation on the selected date

def check_existing_allocation(vvid, date):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
            SELECT *
            FROM allocations
            WHERE vvid = :vvid
            AND testing_date = :date
            """),
            {
                "vvid": vvid,
                "date": date
            }
        )

        return result.fetchone()



# Check if school still has available assessor slots

def check_school_capacity(date, school, required):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
            SELECT COUNT(*)
            FROM allocations
            WHERE testing_date = :date
            AND school_name = :school
            """),
            {
                "date": date,
                "school": school
            }
        )

        current_allocations = result.scalar()


        return current_allocations < required



# Return only schools that still have available slots

def get_available_schools(date, schedule):

    available_schools = []


    for _, row in schedule.iterrows():

        if row["Testing Date"] == date:

            school = row["School Name"]
            required = row["Required Assessors"]


            with engine.connect() as conn:

                result = conn.execute(
                    text("""
                    SELECT COUNT(*)
                    FROM allocations
                    WHERE testing_date = :date
                    AND school_name = :school
                    """),
                    {
                        "date": date,
                        "school": school
                    }
                )


                allocated = result.scalar()


            remaining = required - allocated


            if remaining > 0:

                available_schools.append(
                    {
                        "School Name": school,
                        "Available Slots": remaining
                    }
                )


    return available_schools