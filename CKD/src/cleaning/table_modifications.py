import sqlite3
import re

# Define custom regex extraction function with error handling
def regex_extract(pattern, text):
    try:
        if text is None:  # Handle NULL values
            return None
        match = re.search(pattern, text)
        return match.group(0) if match else None  # Return first match or None
    except Exception as e:
        print(f"Error processing text: {text} | Error: {e}")
        return None  # Prevent crashing

# Define REGEXP function for use in SQLite queries
def regexp(expr, item):
    try:
        return bool(re.search(expr, item)) if item is not None else False
    except Exception as e:
        print(f"Error in REGEXP function: {item} | Error: {e}")
        return False

# Connect to SQLite database
db_path = "../../data/CKD_train.db"
conn = sqlite3.connect(db_path)
conn.create_function("REGEX_EXTRACT", 2, regex_extract)
conn.create_function("REGEXP", 2, regexp)

# Ensure column 'dg_code' exists
try:
    conn.execute("ALTER TABLE diagnoses ADD COLUMN dg_code TEXT;")
    print("Added column 'dg_code'.")
except sqlite3.OperationalError:
    print("Column 'dg_code' already exists, skipping...")

# Run the UPDATE query safely
try:
    conn.execute("""
        UPDATE diagnoses
        SET dg_code = REGEX_EXTRACT('^[A-Z]+[ 0-9.]+', Dg)
        WHERE Dg IS NOT NULL;
    """)
    conn.commit()
    print("Update completed successfully!")
except sqlite3.OperationalError as e:
    print(f"SQL error: {e}")

# Close the connection
conn.close()
print("Database connection closed.")
