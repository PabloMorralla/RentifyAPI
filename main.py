import sqlite3
from fastapi import FastAPI, HTTPException, Body





DB_PATH = "./rentify.sqlite"

app = FastAPI()

def get_connection():
	return sqlite3.connect(DB_PATH)





# -----------------------
# POST /register
# -----------------------

@app.post("/register")
def create_user(
    user: dict = Body(...)
):
    required = ["first_name", "last_name", "email", "phone_number", "password"]
    for field in required:
        if field not in user:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")

    conn = get_connection()
    cursor = conn.cursor()

    # Check for existing email
    cursor.execute("SELECT id FROM Users WHERE email = ?", (user["email"],))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=401, detail="Email already registered")

    cursor.execute("""
        INSERT INTO Users (first_name, last_name, email, phone_number, password)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user["first_name"],
        user["last_name"],
        user["email"],
        user["phone_number"],
        user["password"]
    ))

    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return {
        "id": user_id,
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "phone_number": user["phone_number"]
    }





# -------------
# POST /login
# -------------

@app.post("/login")
def login(
    body: dict = Body(...)
):
    required = ["email", "password"]
    for field in required:
        if field not in body:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, first_name, last_name, email, phone_number, password
        FROM Users WHERE email = ?
    """, (body["email"],))

    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if (body["password"] == row[5]):
        return {
            "id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "email": row[3],
            "phone_number": row[4]
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")




# -----------------------
# POST /register
# -----------------------

@app.post("/register/property")
def create_property(
    user: dict = Body(...)
):
    required = ["address", "owner_fk", "ciudad", "pais", "alquiler"]
    for field in required:
        if field not in user:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")

    conn = get_connection()
    cursor = conn.cursor()

    # Check for existing email
    cursor.execute("SELECT id FROM Users WHERE email = ?", (user["email"],))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=401, detail="Email already registered")

    cursor.execute("""
        INSERT INTO Users (first_name, last_name, email, phone_number, password)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user["first_name"],
        user["last_name"],
        user["email"],
        user["phone_number"],
        user["password"]
    ))

    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return {
        "id": user_id,
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "phone_number": user["phone_number"]
    }

