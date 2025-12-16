import sqlite3
from fastapi import FastAPI, HTTPException, Body, status
from pydantic import BaseModel





DB_PATH = "rentify.db"

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
# POST /property/register
# -----------------------

class Property(BaseModel):
    address: str
    owner_fk: int
    ciudad: str
    pais: str
    alquiler: int

@app.post("/property/register", status_code=201)
def create_property(newProperty: Property):

    if not newProperty.address:
        raise HTTPException(status_code=400, detail="Address obligatorio")

    if not newProperty.owner_fk:
        raise HTTPException(status_code=400, detail="Owner obligatorio")

    query = """
        INSERT INTO Properties (address, owner_fk, ciudad, pais, alquiler)
        VALUES (?, ?, ?, ?, ?)
    """

    execute_query(query, [
        newProperty.address,
        newProperty.owner_fk,
        newProperty.ciudad,
        newProperty.pais,
        newProperty.alquiler
    ])

    return {"message": "Propiedad creada correctamente"}



def execute_query(query: str, params=None):
    if params is None:
        params = []

    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.fetchall()

    except sqlite3.IntegrityError as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=409, detail=f"Violación de integridad: {str(e)}")

    except sqlite3.OperationalError as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error SQL: {str(e)}")

    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

    finally:
        if conn:
            conn.close()


