
from flask import Blueprint, request, jsonify
from db import get_db

attendance_bp = Blueprint("attendance", __name__)


# GET all attendance records
@attendance_bp.get("/attendance")
def list_attendance():
    db = get_db()

    rows = db.execute("""
        SELECT a.id, a.member_id, m.name AS member_name, a.check_in
        FROM attendance a
        JOIN members m ON a.member_id = m.id
        ORDER BY a.id DESC
    """).fetchall()

    return jsonify([dict(row) for row in rows]), 200


# POST: record attendance for a member
@attendance_bp.post("/attendance")
def record_attendance():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be valid JSON"
        }), 400

    if "member_id" not in data:
        return jsonify({
            "error": "member_id is required"
        }), 400

    try:
        member_id = int(data["member_id"])
    except (ValueError, TypeError):
        return jsonify({
            "error": "member_id must be an integer"
        }), 400

    if member_id <= 0:
        return jsonify({
            "error": "member_id must be positive"
        }), 400

    db = get_db()

    member = db.execute(
        "SELECT id FROM members WHERE id = ?",
        (member_id,)
    ).fetchone()

    if member is None:
        return jsonify({
            "error": "Member not found"
        }), 404

    try:
        cursor = db.execute(
            "INSERT INTO attendance (member_id) VALUES (?)",
            (member_id,)
        )
        db.commit()

        row = db.execute("""
            SELECT a.id, a.member_id,
                   m.name AS member_name, a.check_in
            FROM attendance a
            JOIN members m ON a.member_id = m.id
            WHERE a.id = ?
        """, (cursor.lastrowid,)).fetchone()

        return jsonify({
            "message": "Attendance recorded successfully",
            "attendance": dict(row)
        }), 201

    except Exception:
        db.rollback()
        return jsonify({
            "error": "Unable to record attendance"
        }), 409
