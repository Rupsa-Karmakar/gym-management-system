
from flask import Blueprint, request, jsonify
from datetime import date
from db import get_db
from zoneinfo import ZoneInfo

today = datetime.now(ZoneInfo("Asia/Kolkata")).date()

member_bp = Blueprint("members", __name__)


@member_bp.post("/members")
def add_member():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    required = [
        "name", "age", "gender",
        "weight", "fitness_goal", "join_date"
    ]

    missing = [field for field in required if field not in data]
    if missing:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing
        }), 400

    name = data["name"]

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Name is required"}), 400

    try:
        age = int(data["age"])
        weight = float(data["weight"])
    except (ValueError, TypeError):
        return jsonify({
            "error": "Age must be an integer and weight a number"
        }), 400

    if not 1 <= age <= 120 or weight <= 0:
        return jsonify({"error": "Invalid age or weight"}), 400

    if not isinstance(data["gender"], str) or not data["gender"].strip():
        return jsonify({"error": "Gender is required"}), 400

    if not isinstance(data["fitness_goal"], str) or not data["fitness_goal"].strip():
        return jsonify({"error": "Fitness goal is required"}), 400

    try:
        join_date = date.fromisoformat(data["join_date"])
    except (ValueError, TypeError):
        return jsonify({
            "error": "join_date must use YYYY-MM-DD"
        }), 400

    if join_date > date.today():
        return jsonify({
            "error": "Join date cannot be in the future"
        }), 400

    db = get_db()

    try:
        cursor = db.execute(
            """
            INSERT INTO members
            (name, age, gender, weight, fitness_goal, join_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name.strip(),
                age,
                data["gender"].strip(),
                weight,
                data["fitness_goal"].strip(),
                join_date.isoformat()
            )
        )

        db.commit()

        return jsonify({
            "message": "Member registered successfully",
            "member_id": cursor.lastrowid
        }), 201

    except Exception:
        db.rollback()
        return jsonify({
            "error": "Unable to register member"
        }), 500


@member_bp.get("/members")
def list_members():
    db = get_db()
    search = request.args.get("search", "").strip()

    rows = db.execute(
        """
        SELECT * FROM members
        WHERE name LIKE ?
        ORDER BY id DESC
        """,
        (f"%{search}%",)
    ).fetchall()

    return jsonify([dict(row) for row in rows])


@member_bp.put("/members/<int:member_id>")
def update_member(member_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    required = [
        "name", "age", "gender",
        "weight", "fitness_goal", "join_date"
    ]

    missing = [field for field in required if field not in data]
    if missing:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing
        }), 400

    name = data["name"]
    gender = data["gender"]
    fitness_goal = data["fitness_goal"]

    if not all(
        isinstance(value, str) and value.strip()
        for value in [name, gender, fitness_goal]
    ):
        return jsonify({"error": "Name, gender and fitness goal are required"}), 400

    try:
        age = int(data["age"])
        weight = float(data["weight"])
        join_date = date.fromisoformat(data["join_date"])
    except (ValueError, TypeError):
        return jsonify({
            "error": "Invalid age, weight or join_date; use YYYY-MM-DD"
        }), 400

    if not 1 <= age <= 120 or weight <= 0:
        return jsonify({"error": "Invalid age or weight"}), 400

    if join_date > date.today():
        return jsonify({"error": "Join date cannot be in the future"}), 400

    db = get_db()

    existing = db.execute(
        "SELECT id FROM members WHERE id = ?", (member_id,)
    ).fetchone()

    if existing is None:
        return jsonify({"error": "Member not found"}), 404

    db.execute(
        """
        UPDATE members
        SET name = ?, age = ?, gender = ?, weight = ?,
            fitness_goal = ?, join_date = ?
        WHERE id = ?
        """,
        (
            name.strip(), age, gender.strip(), weight,
            fitness_goal.strip(), join_date.isoformat(), member_id
        )
    )
    db.commit()

    return jsonify({
        "message": "Member updated successfully",
        "member_id": member_id
    }), 200


@member_bp.delete("/members/<int:member_id>")
def delete_member(member_id):
    db = get_db()

    existing = db.execute(
        "SELECT id FROM members WHERE id = ?", (member_id,)
    ).fetchone()

    if existing is None:
        return jsonify({"error": "Member not found"}), 404

    try:
        db.execute("DELETE FROM members WHERE id = ?", (member_id,))
        db.commit()

        return jsonify({
            "message": "Member deleted successfully",
            "member_id": member_id
        }), 200

    except Exception:
        db.rollback()
        return jsonify({
            "error": "Unable to delete member. Check whether related records prevent deletion."
        }), 409

