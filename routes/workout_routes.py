
from flask import Blueprint, request, jsonify
from db import get_db

workout_bp = Blueprint("workouts", __name__)


# GET all workout plans
@workout_bp.get("/workouts")
def list_workouts():
    db = get_db()

    rows = db.execute("""
        SELECT w.*, m.name AS member_name
        FROM workout_plans w
        JOIN members m ON w.member_id = m.id
        ORDER BY w.id DESC
    """).fetchall()

    return jsonify([dict(row) for row in rows]), 200


# POST create a workout plan
@workout_bp.post("/workouts")
def add_workout():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    required = [
        "member_id", "exercise_name",
        "sets", "repetitions", "duration"
    ]

    missing = [field for field in required if field not in data]
    if missing:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing
        }), 400

    exercise_name = data["exercise_name"]
    if not isinstance(exercise_name, str) or not exercise_name.strip():
        return jsonify({"error": "Exercise name is required"}), 400

    try:
        member_id = int(data["member_id"])
        sets = int(data["sets"])
        repetitions = int(data["repetitions"])
        duration = int(data["duration"])
    except (ValueError, TypeError):
        return jsonify({
            "error": "Member ID, sets, repetitions and duration must be integers"
        }), 400

    if member_id <= 0 or sets <= 0 or repetitions <= 0 or duration <= 0:
        return jsonify({"error": "All numeric values must be positive"}), 400

    trainer_notes = data.get("trainer_notes", "")
    program_name = data.get("program_name", "General Fitness")

    if not isinstance(trainer_notes, str) or not isinstance(program_name, str):
        return jsonify({
            "error": "Trainer notes and program name must be text"
        }), 400

    db = get_db()

    member = db.execute(
        "SELECT id FROM members WHERE id = ?", (member_id,)
    ).fetchone()

    if member is None:
        return jsonify({"error": "Member not found"}), 404

    cursor = db.execute("""
        INSERT INTO workout_plans
        (member_id, exercise_name, sets, repetitions,
         duration, trainer_notes, program_name)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        member_id, exercise_name.strip(), sets, repetitions,
        duration, trainer_notes.strip(), program_name.strip()
    ))

    db.commit()

    return jsonify({
        "message": "Workout plan created successfully",
        "workout_id": cursor.lastrowid
    }), 201


# GET one workout plan
@workout_bp.get("/workouts/<int:workout_id>")
def get_workout(workout_id):
    db = get_db()

    row = db.execute("""
        SELECT w.*, m.name AS member_name
        FROM workout_plans w
        JOIN members m ON w.member_id = m.id
        WHERE w.id = ?
    """, (workout_id,)).fetchone()

    if row is None:
        return jsonify({"error": "Workout plan not found"}), 404

    return jsonify(dict(row)), 200


# PUT update a workout plan
@workout_bp.put("/workouts/<int:workout_id>")
def update_workout(workout_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    required = [
        "member_id", "exercise_name",
        "sets", "repetitions", "duration"
    ]

    missing = [field for field in required if field not in data]
    if missing:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing
        }), 400

    exercise_name = data["exercise_name"]
    if not isinstance(exercise_name, str) or not exercise_name.strip():
        return jsonify({"error": "Exercise name is required"}), 400

    try:
        member_id = int(data["member_id"])
        sets = int(data["sets"])
        repetitions = int(data["repetitions"])
        duration = int(data["duration"])
    except (ValueError, TypeError):
        return jsonify({"error": "Numeric fields must be integers"}), 400

    if member_id <= 0 or sets <= 0 or repetitions <= 0 or duration <= 0:
        return jsonify({"error": "All numeric values must be positive"}), 400

    trainer_notes = data.get("trainer_notes", "")
    program_name = data.get("program_name", "General Fitness")

    if not isinstance(trainer_notes, str) or not isinstance(program_name, str):
        return jsonify({"error": "Notes and program name must be text"}), 400

    db = get_db()

    existing = db.execute(
        "SELECT id FROM workout_plans WHERE id = ?", (workout_id,)
    ).fetchone()

    if existing is None:
        return jsonify({"error": "Workout plan not found"}), 404

    member = db.execute(
        "SELECT id FROM members WHERE id = ?", (member_id,)
    ).fetchone()

    if member is None:
        return jsonify({"error": "Member not found"}), 404

    db.execute("""
        UPDATE workout_plans
        SET member_id = ?, exercise_name = ?, sets = ?,
            repetitions = ?, duration = ?, trainer_notes = ?,
            program_name = ?
        WHERE id = ?
    """, (
        member_id, exercise_name.strip(), sets, repetitions,
        duration, trainer_notes.strip(), program_name.strip(),
        workout_id
    ))

    db.commit()

    return jsonify({
        "message": "Workout plan updated successfully",
        "workout_id": workout_id
    }), 200


# DELETE a workout plan
@workout_bp.delete("/workouts/<int:workout_id>")
def delete_workout(workout_id):
    db = get_db()

    existing = db.execute(
        "SELECT id FROM workout_plans WHERE id = ?", (workout_id,)
    ).fetchone()

    if existing is None:
        return jsonify({"error": "Workout plan not found"}), 404

    try:
        db.execute(
            "DELETE FROM workout_plans WHERE id = ?", (workout_id,)
        )
        db.commit()

        return jsonify({
            "message": "Workout plan deleted successfully",
            "workout_id": workout_id
        }), 200

    except Exception:
        db.rollback()
        return jsonify({
            "error": "Unable to delete workout plan; related progress records may exist"
        }), 409
