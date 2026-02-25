import sqlite3

from fastapi import HTTPException, Body, APIRouter

from definitions import get_connection, execute_query

from pydantic import BaseModel

router = APIRouter()

class Property(BaseModel):
    address: str
    owner_fk: int
    ciudad: str
    pais: str
    alquiler: int






@router.get("/property/owner/{owner_id}")
def get_properties_by_owner(owner_id: int):

    if not owner_id:
        raise HTTPException(status_code=400, detail="Owner obligatorio")

    query = """
        SELECT *
        FROM Properties
        WHERE owner_fk = ?
    """

    rows = execute_query(query, [owner_id])

    properties = []

    if not rows:
        return properties

    for row in rows:

        properties.append({
            "id": row[0],
            "address": row[1],
            "owner_fk": row[2],
            "ciudad": row[3],
            "pais": row[4],
            "alquiler": row[5]
        })

    return properties


# -----------------------
# POST /property/register
# -----------------------

@router.post("/property/register", status_code=201)
def create_property(newProperty: Property):

    if not newProperty.address:
        raise HTTPException(status_code=400, detail="Address obligatorio")

    if not newProperty.owner_fk:
        raise HTTPException(status_code=400, detail="Owner obligatorio")

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
                    INSERT INTO Properties (address, owner_fk, ciudad, pais, alquiler)
                    VALUES (?, ?, ?, ?, ?)
                """, [
        newProperty.address,
        newProperty.owner_fk,
        newProperty.ciudad,
        newProperty.pais,
        newProperty.alquiler
    ])

        conn.commit()
        property_id = cursor.lastrowid

        return {
            "message": "Property created successfully",
            "id": property_id
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

@router.put("/property/update")
def update_property(
        body: dict = Body(...)
):
    required = ["id", "address", "ciudad", "pais", "alquiler"]
    for field in required:
        if field not in body:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")

    conn=None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""SELECT id, address, owner_fk, ciudad, pais, alquiler
                        FROM Properties
                        WHERE id = ?""", [body["id"]])

        property = cursor.fetchone()

        if not property:
            raise HTTPException(status_code=400, detail=f"Missing property: id {body["id"]}")

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

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Properties
            SET address = ?,
                ciudad = ?,
                pais = ?,
                alquiler = ?
            WHERE id = ?
        """, (
            body["address"],
            body["ciudad"],
            body["pais"],
            body["alquiler"],
            body["id"]
        ))

        conn.commit()

        if cursor.rowcount == 0:
            return {"message": "No se actualizó ningúna propiedad"}
        else:
            return {"message": "Propiedad actualizada correctamente"}



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


@router.delete("/property/{id}")
def delete_property(id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM Properties WHERE id = ?",
        (id,)
    )

    cursor.execute(
        "DELETE FROM Tenants WHERE property_fk = ?",
        (id,)
    )

    conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Propiedad no encontrada"
        )
    return {
        "message": "Propiedad eliminada correctamente",
        "user_id": id
    }
