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
    required = ["email", "password", "type"]
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
        if(body["type"]=="owner"):
            return {
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "phone_number": row[4],
                "ownedProperty": get_properties_by_owner(row[0]),
            }
        elif (body["type"] == "tenant"):
            return {
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "phone_number": row[4],
                "leasedProperty": get_properties_by_tenant(row[0]),
            }
        else:
            return {
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "phone_number": row[4]
            }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")






class Property(BaseModel):
    address: str
    owner_fk: int
    ciudad: str
    pais: str
    alquiler: int


# -----------------------
# POST /property/register
# -----------------------

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



def get_properties_by_owner(owner_id: int):

    if not owner_id:
        raise HTTPException(status_code=400, detail="Owner obligatorio")

    query = """
        SELECT id, address, owner_fk, ciudad, pais, alquiler
        FROM Properties
        WHERE owner_fk = ?
    """

    rows = execute_query(query, [owner_id])

    if not rows:
        return None

    properties = []
    for row in rows:
        properties.append({
            "id": row[0],
            "address": row[1],
            "owner_fk": row[2],
            "ciudad": row[3],
            "pais": row[4],
            "alquiler": row[5],
        })

    return properties




def get_properties_by_tenant(tenant_id: int):

    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant obligatorio")

    query = """
        SELECT property_fk
        FROM Tenants
        WHERE user_fk = ?
    """


    exeq = execute_query(query, [tenant_id])

    if not exeq:
        return None

    id_property = exeq[0][0]

    query = """
                SELECT id, address, owner_fk, ciudad, pais, alquiler
                FROM Properties
                WHERE id = ?
            """

    rows = execute_query(query, [id_property])

    properties = []
    for row in rows:
        properties.append({
            "id": row[0],
            "address": row[1],
            "owner_fk": row[2],
            "ciudad": row[3],
            "pais": row[4],
            "alquiler": row[5],
        })
    return properties[0]

#funcion que toma id propiedad y devuelve users en dicha propiedad
#def get_properties_by_tenant()



