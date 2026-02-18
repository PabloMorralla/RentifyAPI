import sqlite3


from fastapi import FastAPI, HTTPException, Body, status, APIRouter

from definitions import execute_query, get_tenant_by_email

router = APIRouter()


#funcion que toma id propiedad y devuelve tenants en dicha propiedad
@router.get("/property/tenants/{property_id}")
def get_tenants_by_property(property_id: int):

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

# -----------------------
# POST /property/tenant/register
# -----------------------

@router.post("/property/tenant/register", status_code=201)
def add_tenant_into_property(
        body: dict = Body(...)
):
    required = ["property_fk", "email"]
    for field in required:
        if field not in body:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")

    tenant = get_tenant_by_email(body["email"])

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant no encontrado"
        )

    query = """SELECT id, property_fk, user_fk
                FROM Tenants
                WHERE user_fk = ?"""

    tenants = execute_query(query, [tenant["id"]])

    print(tenants)

    if tenants:
        raise HTTPException(
            status_code=404,
            detail="Tenant ya existe"
        )


    query = """
        INSERT INTO Tenants (property_fk, user_fk)
        VALUES (?, ?)
    """

    execute_query(query, (
        body["property_fk"],
        tenant["id"]
    ))