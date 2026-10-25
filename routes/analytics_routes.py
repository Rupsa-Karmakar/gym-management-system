
from datetime import date

import pandas as pd
from flask import Blueprint, jsonify

from services.analytics_service import (
    load_members,
    load_memberships,
    load_attendance,
    load_workouts,
    load_workout_progress,
)

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.get("/analytics/summary")
def analytics_summary():
    try:
        members = load_members()
        memberships = load_memberships()
        attendance = load_attendance()
        workouts = load_workouts()
        progress = load_workout_progress()

        # Existing statistics
        total_members = len(members)
        total_memberships = len(memberships)

        total_revenue = 0.0
        plan_distribution = {}

        if not memberships.empty:
            if "amount" in memberships.columns:
                total_revenue = float(memberships["amount"].sum())

            if "plan" in memberships.columns:
                plan_distribution = {
                    str(plan): int(count)
                    for plan, count
                    in memberships["plan"].value_counts().items()
                }

        # Attendance statistics
        total_attendance_records = len(attendance)

        unique_members_attended = (
            int(attendance["member_id"].nunique())
            if "member_id" in attendance.columns
            else 0
        )

        # Workout plan statistics
        total_workout_plans = len(workouts)
        total_workout_progress_records = len(progress)

        completed_workouts = 0
        pending_workouts = 0

        if not progress.empty and "completed" in progress.columns:
            completed_workouts = int(
                (progress["completed"] == 1).sum()
            )
            pending_workouts = int(
                (progress["completed"] == 0).sum()
            )

        workout_completion_rate = (
            round(
                completed_workouts
                / total_workout_progress_records * 100,
                2,
            )
            if total_workout_progress_records > 0
            else 0.0
        )

        # Active memberships: valid today
        today = date.today().isoformat()
        active_memberships = 0

        if not memberships.empty and {
            "start_date", "end_date"
        }.issubset(memberships.columns):
            start_dates = pd.to_datetime(
                memberships["start_date"],
                errors="coerce"
            )
            end_dates = pd.to_datetime(
                memberships["end_date"],
                errors="coerce"
            )

            active_memberships = int(
                (
                    (start_dates <= pd.Timestamp(today))
                    & (end_dates >= pd.Timestamp(today))
                ).sum()
            )

        return jsonify({
            # Existing fields — preserved
            "total_members": total_members,
            "total_memberships": total_memberships,
            "total_revenue": round(total_revenue, 2),
            "membership_plan_distribution": plan_distribution,

            # New attendance statistics
            "total_attendance_records": total_attendance_records,
            "unique_members_attended": unique_members_attended,

            # New workout statistics
            "total_workout_plans": total_workout_plans,
            "total_workout_progress_records":
                total_workout_progress_records,
            "completed_workouts": completed_workouts,
            "pending_workouts": pending_workouts,
            "workout_completion_rate": workout_completion_rate,

            # New membership statistic
            "active_memberships": active_memberships,
        }), 200

    except Exception:
        return jsonify({
            "error": "Unable to generate analytics summary"
        }), 500
