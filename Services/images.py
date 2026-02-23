import sqlite3
from enum import nonmember

from fastapi import FastAPI, HTTPException, Body, status, APIRouter

from definitions import get_connection, execute_query

router = APIRouter()


@router.get("/images/property/{property_id}")
def get_image_by_property(property_id: int):

    if not property_id:
        raise HTTPException(status_code=400, detail="Propiedad obligatoria")

    query = """
        SELECT url_address
        FROM PropertiesImages
        WHERE property_fk = ?
    """

    row = execute_query(query, [property_id])[0][0]


    if not row:
        raise HTTPException(status_code=400, detail="url no existe")

    return row


@router.get("/images/owner/{owner_id}")
def get_images_by_owner(owner_id: int):

    if not owner_id:
        raise HTTPException(status_code=400, detail="Owner obligatorio")

    query = """
        SELECT url_address
        FROM PropertiesImages
        WHERE owner_fk = ?
    """

    rows = execute_query(query, [owner_id])

    images = []

    if not rows:
        return images

    for row in rows:


        images.append(row[0])

    return images


@router.get("/images")
def get_images():



    query = """
        SELECT url_address
        FROM PropertiesImages
    """

    rows = execute_query(query, )

    images = []

    if not rows:
        return images

    for row in rows:


        images.append(row[0])

    return images