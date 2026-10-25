
from flask import Blueprint, request, jsonify
from datetime import date
from db import get_db

membership_bp = Blueprint("memberships", __name__)


@membership_bp.post("/memberships")
def add_membership():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    required = [
        "member_id", "plan", "start_date",
        "end_date", "amount"
    ]

    missing = [field for field in required if field not in data]
    if missing:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing
        }), 400

    try:
        member_id = int(data["member_id"])
        amount = float(data["amount"])
    except (ValueError, TypeError):
        return jsonify({
            "error": "member_id must be an integer and amount must be a number"
        }), 400

    if member_id <= 0 or amount < 0:
        return jsonify({"error": "Invalid member_id or amount"}), 400

    plan = data["plan"]
    if plan not in ["Monthly", "Quarterly", "Yearly"]:
        return jsonify({
            "error": "Plan must be Monthly, Quarterly, or Yearly"
        }), 400

    try:
        start_date = date.fromisoformat(data["start_date"])
        end_date = date.fromisoformat(data["end_date"])
    except (ValueError, TypeError):
        return jsonify({
            "error": "Dates must use YYYY-MM-DD format"
        }), 400

    if end_date < start_date:
        return jsonify({
            "error": "end_date cannot be before start_date"
        }), 400

    db = get_db()

    member = db.execute(
        "SELECT id FROM members WHERE id = ?",
        (member_id,)
    ).fetchone()

    if member is None:
        return jsonify({"error": "Member not found"}), 404

    try:
        cursor = db.execute(
            """
            INSERT INTO memberships
            (member_id, plan, start_date, end_date, amount)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                member_id,
                plan,
                start_date.isoformat(),
                end_date.isoformat(),
                amount
            )
        )
        db.commit()

        return jsonify({
            "message": "Membership created successfully",
            "membership_id": cursor.lastrowid
        }), 201

    except Exception:
        db.rollback()
        return jsonify({
            "error": "Unable to create membership"
        }), 500


@membership_bp.get("/memberships")
def list_memberships():
    db = get_db()

    rows = db.execute(
        """
        SELECT
            memberships.id,
            memberships.member_id,
            members.name AS member_name,
            memberships.plan,
            memberships.start_date,
            memberships.end_date,
            memberships.amount
        FROM memberships
        JOIN members ON memberships.member_id = members.id
        ORDER BY memberships.id DESC
        """
    ).fetchall()

    return jsonify([dict(row) for row in rows])


@membership_bp.get("/memberships/<int:membership_id>")
def get_membership(membership_id):
    db = get_db()

    row = db.execute(
        """
        SELECT
            memberships.id,
            memberships.member_id,
            members.name AS member_name,
            memberships.plan,
            memberships.start_date,
            memberships.end_date,
            memberships.amount
        FROM memberships
        JOIN members ON memberships.member_id = members.id
        WHERE memberships.id = ?
        """,
        (membership_id,)
    ).fetchone()

    if row is None:
        return jsonify({"error": "Membership not found"}), 404

    return jsonify(dict(row))
