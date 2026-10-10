import sqlite3

db = sqlite3.connect("instance/studyplanner.db")

db.execute(
    "ALTER TABLE task ADD COLUMN subject VARCHAR(200) DEFAULT 'General'"
)

db.commit()
db.close()

print("Subject column added successfully")