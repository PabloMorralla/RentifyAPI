import sqlite3

from fastapi import HTTPException


DB_PATH = "rentify.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

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



def get_user_by_id(user_id: int):

    if not user_id:
        raise HTTPException(status_code=400, detail="ID obligatorio")

    query = """SELECT id, first_name, last_name, phone_number, email
            FROM Users
            WHERE id = ?"""

    user = execute_query(query, [user_id])[0]
    if user:
        return {
            "id": user[0],
            "first_name": user[1],
            "last_name": user[2],
            "phone_number": user[3],
            "email": user[4],

        }
    return None




def get_user_type_by_id(user_id: int):

    if not user_id:
        raise HTTPException(status_code=400, detail="ID obligatorio")

    query = """SELECT type
            FROM Users
            WHERE id = ?"""

    user = execute_query(query, [user_id])
    if user:
        return user[0]

    return None



def get_tenant_by_email(email: str):

    if not email:
        raise HTTPException(status_code=400, detail="email obligatorio")

    query = """SELECT id, first_name, last_name, phone_number, email, type
            FROM Users
            WHERE email = ?"""

    user = execute_query(query, [email])
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Tenant no encontrado"
        )
    print(user)
    if not user[0][5]== "tenant":
        raise HTTPException(status_code=400, detail="User tenant required")

    return {
            "id": user[0][0],
            "first_name": user[0][1],
            "last_name": user[0][2],
            "phone_number": user[0][3],
            "email": user[0][4],
        }





