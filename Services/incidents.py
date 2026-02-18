import sqlite3


from fastapi import FastAPI, HTTPException, Body, status, APIRouter

from definitions import get_connection, get_user_by_id, execute_query

router = APIRouter()

# -------------
# POST /incidents/create
# -------------

@router.post("/incidents/create")
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
@router.get("/property/incidents/{property_id}")
def get_incidents_by_property(property_id: int):

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
            "owner_id": row[3],
            "tenant": get_user_by_id(row[4]),
            "property_id": row[5]
        }
        for row in rows
    ]

    return incidents



@router.delete("/incidents/{id}")
def delete_incident(id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM Incidents WHERE id = ?",
        (id,)
    )

    conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Incidente no encontrado"
        )

    return {
        "message": "Incidente eliminado correctamente",
        "id": id
    }

# -------------
# PUT /update/incident
# -------------

@router.put("/update/incident")
def update_incident(
        body: dict = Body(...)
):
    required = ["id", "issue", "description"]
    for field in required:
        if field not in body:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")


    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Incidents
            SET asunto = ?,
                descrip = ?
            WHERE id = ?
        """, (
            body["issue"],
            body["description"],
            body["id"]
        ))

        conn.commit()

        if cursor.rowcount == 0:
            return {"message": "No se actualizó ningún incident"}
        else:
            return {
                "message": "Incidente actualizado correctamente",
                "id": body["id"]
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

