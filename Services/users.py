import sqlite3


from fastapi import HTTPException, Body, APIRouter

from definitions import get_connection, get_properties_by_owner, get_properties_by_tenant, get_user_type_by_id, \
    get_user_by_id, execute_query

router = APIRouter()



# -----------------------
# POST /register
# -----------------------

@router.post("/register")
def create_user(
    user: dict = Body(...)
):
    required = ["first_name", "last_name", "email", "phone_number", "password", "type"]
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
        INSERT INTO Users (first_name, last_name, email, phone_number, password, type)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user["first_name"],
        user["last_name"],
        user["email"],
        user["phone_number"],
        user["password"],
        user["type"]
    ))

    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return {
        "id": user_id,
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "phone_number": user["phone_number"],
        "type": user["type"]
    }





# -------------
# POST /login
# -------------

@router.post("/login")
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
        SELECT id, first_name, last_name, email, phone_number, password ,type
        FROM Users WHERE email = ?
    """, (body["email"],))

    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if (body["password"] == user[5]) and (body["type"] == user[6]):
        if body["type"]== "owner":
            return {
                "id": user[0],
                "first_name": user[1],
                "last_name": user[2],
                "email": user[3],
                "phone_number": user[4],
                "ownedProperty": get_properties_by_owner(user[0]),
                "type": user[6]
            }
        elif body["type"] == "tenant":
            return {
                "id": user[0],
                "first_name": user[1],
                "last_name": user[2],
                "email": user[3],
                "phone_number": user[4],
                "leasedProperty": get_properties_by_tenant(user[0]),
                "type": user[6]
            }
        else:
            return {
                "id": user[0],
                "first_name": user[1],
                "last_name": user[2],
                "email": user[3],
                "phone_number": user[4],
                "type": user[6]
            }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")



@router.delete("/users/{user_id}")
def delete_user(user_id: int):

    user_type = get_user_type_by_id(user_id)[0]
    if user_type == "owner":

        ##Eliminar relaciones tenants por propedad tambien
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM Properties WHERE owner_fk = ?",
            (user_id,)
        )
        conn.commit()

    elif user_type == "tenant":
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM Tenants WHERE user_fk = ?",
            (user_id,)
        )
        conn.commit()

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
# PUT /update/user
# -------------

@router.put("/update/user")
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



# -----------------------
# GET /owner/{owner_fk}
# -----------------------

#endpoint que toma id ownerfk de una propiedad y devuelve el user owner de dicha propiedad
@router.get("/owner/{owner_fk}")
def get_user_by_owner(owner_fk: int):

    if not owner_fk:
        raise HTTPException(status_code=400, detail="ID obligatorio")

    query = """SELECT id, first_name, last_name, phone_number, email, type
            FROM Users
            WHERE id = ?"""

    user = execute_query(query, [owner_fk])[0]
    print(user)

    if not user[5]== "owner":
        raise HTTPException(status_code=400, detail="User owner required")

    return {
            "id": user[0],
            "first_name": user[1],
            "last_name": user[2],
            "phone_number": user[3],
            "email": user[4],
            "type": user[5]

    }