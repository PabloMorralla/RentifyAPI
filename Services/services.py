import sqlite3

from fastapi import HTTPException, Body, APIRouter

from definitions import get_connection, get_properties_by_owner, get_properties_by_tenant, get_user_type_by_id, \
    get_user_by_id, execute_query

router = APIRouter()

#funcion que toma id propiedad y devuelve servicios de dicha propiedad
@router.get("/property/services/{property_id}")
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


@router.post("/services/create")
def create_services(
        body: dict = Body(...)
):
    required = ["property_fk", "included", "excluded"]
    for field in required:
        if field not in body:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")


    conn=None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
                INSERT INTO Services (property_fk, included, excluded)
                VALUES (?, ?, ?)
            """, [body["property_fk"],body["included"],body["excluded"]])

        conn.commit()
        service_id = cursor.lastrowid

        return {
            "message": "Service created successfully",
            "id": service_id
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




@router.delete("/services/{property_fk}")
def delete_services(property_fk: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM Services WHERE property_fk = ?",
        (property_fk,)
    )

    conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    return {
        "message": "Servicio eliminado correctamente",
        "property_fk": property_fk
    }



@router.put("/services/update")
def update_services(
        body: dict = Body(...)
):
    required = ["property_fk", "included", "excluded"]
    for field in required:
        if field not in body:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")


    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Services
            SET included = ?,
                excluded = ?
            WHERE property_fk = ?
        """, (
            body["included"],
            body["excluded"],
            body["property_fk"]
        ))

        conn.commit()

        if cursor.rowcount == 0:
            return {"message": "No se actualizó ningún service"}
        else:
            return {
                "message": "Servicio actualizado correctamente",
                "property_fk": body["property_fk"]
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

