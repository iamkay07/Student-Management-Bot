import sqlite3

def init_db():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        student_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL, phone TEXT,address TEXT,
                        email TEXT UNIQUE NOT NULL
                    )''')
    conn.commit()
    conn.close()
    print("Database initialized successfully.")


def add_student(student_id, name, phone, address, email):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO students (student_id, name, phone, address, email) VALUES (?, ?, ?, ?, ?)',
                       (student_id, name, phone, address, email))
        conn.commit()
        print("Student added successfully.")
        return True
    except sqlite3.IntegrityError as e:
        print(f"Error adding student: {e}")
    finally:
        conn.close()


def search_students_by_name(search_query):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE name LIKE ?', ('%' + search_query + '%',))
    results = cursor.fetchall()
    conn.close()
    return results


if __name__ == "__main__":
    init_db()
    