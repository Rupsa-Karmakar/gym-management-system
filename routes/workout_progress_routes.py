
from flask import Blueprint, request, jsonify
from db import get_db

progress_bp = Blueprint("workout_progress", __name__)


# GET: View all workout progress records
@progress_bp.get("/workout-progress")
def list_progress():
    db = get_db()

    rows = db.execute("""
        SELECT
            p.id,
            p.workout_id,
            w.exercise_name,
            w.member_id,
            m.name AS member_name,
            p.workout_date,
            p.completed,
            p.notes
        FROM workout_progress p
        JOIN workout_plans w ON p.workout_id = w.id
        JOIN members m ON w.member_id = m.id
        ORDER BY p.id DESC
    """).fetchall()

    return jsonify([dict(row) for row in rows]), 200


# POST: Record workout progress
@progress_bp.post("/workout-progress")
def add_progress():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    required = ["workout_id", "workout_date", "completed"]
    missing = [field for field in required if field not in data]

    if missing:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing
        }), 400

    try:
        workout_id = int(data["workout_id"])
        completed = int(data["completed"])
    except (ValueError, TypeError):
        return jsonify({
            "error": "workout_id and completed must be integers"
        }), 400

    workout_date = data["workout_date"]
    notes = data.get("notes", "")

    if workout_id <= 0:
        return jsonify({"error": "workout_id must be positive"}), 400

    if completed not in (0, 1):
        return jsonify({
            "error": "completed must be 0 or 1"
        }), 400

    if not isinstance(workout_date, str) or not workout_date.strip():
        return jsonify({"error": "workout_date is required"}), 400

    if not isinstance(notes, str):
        return jsonify({"error": "notes must be text"}), 400

    db = get_db()

    workout = db.execute(
        "SELECT id FROM workout_plans WHERE id = ?",
        (workout_id,)
    ).fetchone()

    if workout is None:
        return jsonify({"error": "Workout plan not found"}), 404

    cursor = db.execute("""
        INSERT INTO workout_progress
        (workout_id, workout_date, completed, notes)
        VALUES (?, ?, ?, ?)
    """, (
        workout_id,
        workout_date.strip(),
        completed,
        notes.strip()
    ))

    db.commit()

    return jsonify({
        "message": "Workout progress recorded successfully",
        "progress_id": cursor.lastrowid
    }), 201


# GET: View one progress record
@progress_bp.get("/workout-progress/<int:progress_id>")
def get_progress(progress_id):
    db = get_db()

    row = db.execute("""
        SELECT p.*, w.exercise_name, w.member_id,
               m.name AS member_name
        FROM workout_progress p
        JOIN workout_plans w ON p.workout_id = w.id
        JOIN members m ON w.member_id = m.id
        WHERE p.id = ?
    """, (progress_id,)).fetchone()

    if row is None:
        return jsonify({"error": "Progress record not found"}), 404

    return jsonify(dict(row)), 200


# PUT: Update a progress record
@progress_bp.put("/workout-progress/<int:progress_id>")
def update_progress(progress_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    required = ["workout_id", "workout_date", "completed"]
    missing = [field for field in required if field not in data]

    if missing:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing
        }), 400

    try:
        workout_id = int(data["workout_id"])
        completed = int(data["completed"])
    except (ValueError, TypeError):
        return jsonify({
            "error": "workout_id and completed must be integers"
        }), 400

    workout_date = data["workout_date"]
    notes = data.get("notes", "")

    if workout_id <= 0 or completed not in (0, 1):
        return jsonify({"error": "Invalid workout_id or completed value"}), 400

    if not isinstance(workout_date, str) or not workout_date.strip():
        return jsonify({"error": "workout_date is required"}), 400

    if not isinstance(notes, str):
        return jsonify({"error": "notes must be text"}), 400

    db = get_db()

    existing = db.execute(
        "SELECT id FROM workout_progress WHERE id = ?",
        (progress_id,)
    ).fetchone()

    if existing is None:
        return jsonify({"error": "Progress record not found"}), 404

    workout = db.execute(
        "SELECT id FROM workout_plans WHERE id = ?",
        (workout_id,)
    ).fetchone()

    if workout is None:
        return jsonify({"error": "Workout plan not found"}), 404

    db.execute("""
        UPDATE workout_progress
        SET workout_id = ?, workout_date = ?, completed = ?, notes = ?
        WHERE id = ?
    """, (
        workout_id,
        workout_date.strip(),
        completed,
        notes.strip(),
        progress_id
    ))

    db.commit()

    return jsonify({
        "message": "Workout progress updated successfully",
        "progress_id": progress_id
    }), 200


# DELETE: Remove a progress record
@progress_bp.delete("/workout-progress/<int:progress_id>")
def delete_progress(progress_id):
    db = get_db()

    existing = db.execute(
        "SELECT id FROM workout_progress WHERE id = ?",
        (progress_id,)
    ).fetchone()

    if existing is None:
        return jsonify({"error": "Progress record not found"}), 404

    db.execute(
        "DELETE FROM workout_progress WHERE id = ?",
        (progress_id,)
    )
    db.commit()

    return jsonify({
        "message": "Workout progress deleted successfully",
        "progress_id": progress_id
    }), 200
