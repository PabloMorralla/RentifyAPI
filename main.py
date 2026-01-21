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
        if not user[field].strip():
            raise HTTPException(status_code=400, detail=f"Void field: {field}")
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


#funcion que toma id owner y devuelve propiedades del owner
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



#funcion que toma id inquilino y devuelve propiedad donde eat
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
@app.get("/property/tenants/{property_id}")
def get_users_by_property(property_id: int):

    if not property_id:
        raise HTTPException(status_code=400, detail="Propiedad obligatorio")

    query = """
        SELECT user_fk
        FROM Tenants
        WHERE property_fk = ?
    """

    rows = execute_query(query, [property_id])

    users = []

    if not rows:
        return users

    for row in rows:
        query = """
                SELECT id, first_name, last_name, email, phone_number
                FROM Users
                WHERE id = ?
            """

        user = execute_query(query, [row[0]])[0]
        users.append({
            "id": user[0],
            "first_name": user[1],
            "last_name": user[2],
            "email": user[3],
            "phone_number": user[4],
        })

    return users


#funcion que toma id propiedad y devuelve servicios de dicha propiedad
@app.get("/property/services/{property_id}")
def get_services_by_property(property_id: int):

    if not property_id:
        raise HTTPException(status_code=400, detail="Propiedad obligatorio")

    query = """
        SELECT included, excluded
        FROM Services
        WHERE property_fk = ?
    """

    rows = execute_query(query, [property_id])

    if not rows:
        return {
            "included": None,
            "excluded": None
        }

    service = rows[0]

    return {
        "included": service[0],
        "excluded": service[1],
    }


# -----------------------
# GET /owner/{owner_fk}
# -----------------------

#endpoint que toma id ownerfk de una propiedad y devuelve el user owner de dicha propiedad
@app.get("/owner/{owner_fk}")
def get_user_by_owner(owner_fk: int):

    if not owner_fk:
        raise HTTPException(status_code=400, detail="ID obligatorio")

    query = """SELECT id, first_name, last_name, phone_number, email
            FROM Users
            WHERE id = ?"""

    user = execute_query(query, [owner_fk])[0]
    print(user)
    return {
            "id": user[0],
            "first_name": user[1],
            "last_name": user[2],
            "phone_number": user[3],
            "email": user[4],

        }




def get_user_by_id(user_id: int):

    if not user_id:
        raise HTTPException(status_code=400, detail="ID obligatorio")

    query = """SELECT id, first_name, last_name, phone_number, email
            FROM Users
            WHERE id = ?"""

    user = execute_query(query, [user_id])[0]
    return {
            "id": user[0],
            "first_name": user[1],
            "last_name": user[2],
            "phone_number": user[3],
            "email": user[4],

        }



# -------------
# PUT /update/user
# -------------

@app.put("/update/user")
def update_user(
        body: dict = Body(...)
):
    required = ["id", "first_name", "last_name", "email", "phone_number", "actualpassword", "newpassword"]
    for field in required:
        if field not in body:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")


    print(body["first_name"], body["last_name"], body["email"] , body["phone_number"] , body["actualpassword"] )

    conn=None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""SELECT id, first_name, last_name, email, phone_number, password
                        FROM Users
                        WHERE id = ?""", [body["id"]])

        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=400, detail=f"Missing user: id {body["id"]}")
        if not body["actualpassword"] == user[5]:
            raise HTTPException(status_code=401, detail="Invalid password")
    except HTTPException:
        raise
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

    first_name = body["first_name"]
    last_name = body["last_name"]
    email = body["email"]
    phone_number = body["phone_number"]
    password = body["actualpassword"]

    #no puedo iterar sobre body
    if body["first_name"] =="":
        first_name = user[1]
    if body["last_name"] =="":
        last_name = user[2]
    if body["email"] =="":
        email = user[3]
    if body["phone_number"] =="":
        phone_number = user[4]

    if body["newpassword"] !="":
        password = body["newpassword"]


    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Users
            SET first_name = ?,
                last_name = ?,
                email = ?,
                phone_number = ?,
                password = ?
            WHERE id = ?
        """, (
            first_name,
            last_name,
            email,
            phone_number,
            password,
            body["id"]
        ))

        conn.commit()

        if cursor.rowcount == 0:
            return {"message": "No se actualizó ningún usuario"}
        else:
            return get_user_by_id(body["id"])


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



@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM Users WHERE id = ?",
        (user_id,)
    )

    conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    return {
        "message": "Usuario eliminado correctamente",
        "user_id": user_id
    }




# -------------
# POST /incidents/create
# -------------

@app.post("/incidents/create")
def create_incident(
        body: dict = Body(...)
):
    required = ["asunto", "descrip", "id_owner", "id_tenant", "id_property"]
    for field in required:
        if field not in body:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")


    conn=None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
                INSERT INTO Incidents (asunto, descrip, id_owner, id_tenant, id_property)
                VALUES (?, ?, ?, ?, ?)
            """, [body["asunto"],body["descrip"],body["id_owner"],body["id_tenant"],body["id_property"]])

        conn.commit()
        incident_id = cursor.lastrowid

        return {
            "message": "Incident created successfully",
            "id": incident_id
        }

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



#funcion que toma id propiedad y devuelve incidentes en dicha propiedad
@app.get("/property/incidents/{property_id}")
def get_users_by_property(property_id: int):

    if not property_id:
        raise HTTPException(status_code=400, detail="Propiedad obligatorio")

    query = """
        SELECT id, asunto, descrip, id_owner, id_tenant, id_property
        FROM Incidents
        WHERE id_property = ?
    """

    rows = execute_query(query, [property_id])
    incidents = [
        {
            "id": row[0],
            "issue": row[1],
            "description": row[2],
            "property_id": row[3],
            "tenant": get_user_by_id(row[4]),
            "owner_id": row[5]
        }
        for row in rows
    ]

    return incidents