PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL CHECK(age BETWEEN 1 AND 120),
    gender TEXT NOT NULL,
    weight REAL NOT NULL CHECK(weight > 0),
    fitness_goal TEXT NOT NULL,
    join_date TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memberships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    plan TEXT NOT NULL
        CHECK(plan IN ('Monthly', 'Quarterly', 'Yearly')),
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount >= 0),
    FOREIGN KEY(member_id) REFERENCES members(id)
);

CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    check_in TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(member_id) REFERENCES members(id),
    UNIQUE(member_id, check_in)
);

CREATE TABLE IF NOT EXISTS workout_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    exercise_name TEXT NOT NULL,
    sets INTEGER NOT NULL CHECK(sets > 0),
    repetitions INTEGER NOT NULL CHECK(repetitions > 0),
    duration INTEGER NOT NULL CHECK(duration > 0),
    trainer_notes TEXT DEFAULT '',
    program_name TEXT NOT NULL DEFAULT 'General Fitness',
    FOREIGN KEY(member_id) REFERENCES members(id)
);

CREATE TABLE IF NOT EXISTS workout_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER NOT NULL,
    workout_date TEXT NOT NULL,
    completed INTEGER NOT NULL DEFAULT 0
        CHECK(completed IN (0, 1)),
    notes TEXT DEFAULT '',
    FOREIGN KEY(workout_id) REFERENCES workout_plans(id)
);