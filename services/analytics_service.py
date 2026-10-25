
import pandas as pd
from db import get_db


def load_members():
    db = get_db()
    return pd.read_sql_query(
        "SELECT * FROM members",
        db
    )


def load_memberships():
    db = get_db()
    return pd.read_sql_query(
        "SELECT * FROM memberships",
        db
    )


def load_attendance():
    db = get_db()
    return pd.read_sql_query(
        "SELECT * FROM attendance",
        db
    )


def load_workouts():
    db = get_db()
    return pd.read_sql_query(
        "SELECT * FROM workout_plans",
        db
    )


def load_workout_progress():
    db = get_db()
    return pd.read_sql_query(
        "SELECT * FROM workout_progress",
        db
    )
