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