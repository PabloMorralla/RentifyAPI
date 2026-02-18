# Table of Contents

- [Users](#users)
  - [Create a User](#create-a-user)
  - [Update a User](#update-a-user)
  - [Delete a User](#delete-a-user)
  - [Login](#login)

- [Property](#property)
  - [Create a Property](#create-a-property)
  - [Update a Property](#update-a-property)
  - [Delete a Property](#delete-a-property)

- [Tenants](#tenants)
  - [Get tenants by property](#get-tenants-by-property)
  - [Register a tenant in a Property](#register-a-tenat-in-a-property)

- [Services](#services)
  - [Get services by property](#get-services-by-property)

- [Incidents](#incidents)
  - [Create an Incident](#create-an-incident)
  - [Obtain Incidents](#obtain-incidents)
  - [Update an Incident](#update-an-incident)
  - [Delete an Incident](#delete-an-incident)

- [Changes](#changes)
  - [User now has field "type"](#user-now-has-field-type)

# Users

## Create a User

Create a user with all the information.

### Route
`POST /user`

### Body:

All fields are required but none is checked for format.
Email must be unique.

```
{
    "first_name": "Marc",
    "last_name": "Gonzalez",
    "email": "marcg@example.com",
    "phone_number": "+34 612 532 457",
    "password": "password1234",
    "type": "owner"
}
```

### Error Codes

- 400: Missing field
- 401: Email already registered

### Returns 

(Only on success)

```
{
    "id": 20,
    "first_name": "Marc",
    "last_name": "Gonzalez",
    "email": "marcg@example.com",
    "phone_number": "+34 612 532 457",
    "type": "owner"

}
```


## Update a User

Update a User with all the information.

### Route
`PUT /update/user`

### Body:

All fields are required.
Password must be correct in field actualpassword.

```
{
    "id": 100,
    "first_name": "",
    "last_name": "",
    "email": "",
    "phone_number": "",
    "actualpassword": "test",
    "newpassword": ""
}
```

### Error Codes

- 400: Missing field
- 401: Invalid password

### Example of response 

```
{
    "id": 100,
    "first_name": "ownertest",
    "last_name": "test",
    "phone_number": "1111111111",
    "email": "ownertest@example.com"
}
```

## Delete a User

Delete an existent User.

### Route
`DELETE /users/{user_id}`

### Body:

User id is required.

### Error Codes

- 404: User not found

### Example of response 

```
{
    "message": "Usuario eliminado correctamente",
    "user_id": 12
}
```

## Login

### Route

`POST /login`

### Body

All required, none checked, email unique.

Type can be owner or tenant.

```
{
    "email": "pablo@example.com",
    "password": "1234",
    "type": "tenant"
}
```

### Error Codes

- 400: Missing field
- 401: Invalid credentials
- 404: User not found

### Returns

(Only on success)   

Type owner return an array of json objects in field ownedProperty -> [{}].

Type tenant return a json object in field leasedProperty -> {}.

Si el usuario no es inquilino o no tiene propiedades se devuelve el usuario con el campo ownedProperty o leasedProperty en null.

(user con alquiler)
```
{
    "id": 2,
    "first_name": "Pablo",
    "last_name": "Morralla",
    "email": "pablo@example.com",
    "phone_number": "611620552",
    "leasedProperty": {
        "id": 2,
        "address": "Calle Sol 9",
        "owner_fk": 1,
        "ciudad": "Sevilla",
        "pais": "España",
        "alquiler": 450
    },
    "type": "tenant"
    
}
```
(user sin alquiler)
```
{
    "id": 13,
    "first_name": "Valentina",
    "last_name": "Cruz",
    "email": "valentina.cruz@example.com",
    "phone_number": "5551000010",
    "leasedProperty": null,
    "type": "tenant"

}
```

(user con propiedades)
```
{
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone_number": "123456789",
    "ownedProperty": [
        {
            "id": 2,
            "address": "Calle Sol 9",
            "owner_fk": 1,
            "ciudad": "Sevilla",
            "pais": "España",
            "alquiler": 450
        },
        {
            "id": 3,
            "address": "Calle Mayor 123",
            "owner_fk": 1,
            "ciudad": "Madrid",
            "pais": "España",
            "alquiler": 750
        }
    ],
    "type": "owner"
}
```

# Property

## Create a Property

Create a property with all the information.

### Route
`POST /property/register`

### Body:

All fields are required, they will gol to be checked his format(String/Int/Double) because a basemodel is used.

```
{
    "address": "Calle Sol 9",
    "owner_fk": 1,
    "ciudad": "Sevilla",
    "pais": "España",
    "alquiler": 450
}
```

### Error Codes

- 400: Missing field (address or owner_fk)
- 409: Integrity violation (owner_fk does not exist or duplicate constraints)

### Example of use 


```
curl -X POST http://localhost:8000/property/register \
  -H "Content-Type: application/json" \
  -d '{
    "address": "Calle Sol 9",
    "owner_fk": 1,
    "ciudad": "Sevilla",
    "pais": "España",
    "alquiler": 450
  }' -v
```

## Update a Property

Update a Property with all the information.

### Route
`PUT /property/update`

### Body:

All fields are required.

```
{
    "id": 2
    "address": "Calle Sol 9",
    "ciudad": "Sevilla",
    "pais": "España",
    "alquiler": 450
}
```

### Error Codes

- 400: Missing field
### Example of response 

```
{
    "message": "Propiedad actualizada correctamente"
}
```

## Delete a Property

Delete an existent Property.

### Route
`DELETE /property/{id}`

### Body:

Property id is required.

### Error Codes

- 404: Property not found

### Example of response 

```
{
    "message": "Propiedad eliminada correctamente",
    "id": 2
}
```

# Tenants

## Get tenants by property

Devuelve todos los usuarios (inquilinos) asociados a una propiedad.
### Route
`GET /property/tenants/{property_id}`

### Params

| Name        | Type | Description        |
| ----------- | ---- | ------------------ |
| property_id | int  | ID de la propiedad |


### Error Codes

- 400: Missing field (id property)

### Example Request:

```
curl -X GET "http://localhost:8000/tenants/property/2"

```


### Example of Response 


```
[
    {
        "id": 2,
        "first_name": "Pablo",
        "last_name": "Morralla",
        "email": "pablo@example.com",
        "phone_number": "611620552"
    },
    {
        "id": 3,
        "first_name": "Guille",
        "last_name": "Campos",
        "email": "guille@gmail.com",
        "phone_number": "123424434"
    },
    {
        "id": 4,
        "first_name": "Juan",
        "last_name": "Pérez",
        "email": "juan.perez@example.com",
        "phone_number": "5551000001"
    }
]

```

## Register a tenat in a Property

Register an existent tenat in a Property

### Route
`POST /property/tenant/register`

### Body:

All fields are required.

```
{
    "property_fk": 7,
    "email": "paquitaflores@example.com"
}
```

### Error Codes

- 400: Missing field.
- 404: Tenant in an existent property or missing

### Response:

```
{
    "detail": "Tenant ya existe"
}
```

# Services

## Get services by property

Devuelve los servicios incluidos y excluidos asociados a una propiedad.

### Route
`GET /property/services/{property_id}`

### Params

| Name        | Type | Description        |
| ----------- | ---- | ------------------ |
| property_id | int  | ID de la propiedad |

### Error Codes

- 400: Missing field (id property)

### Example Request

```
curl -X GET "http://localhost:8000/property/services/1"
```

### Example of Response
(si tiene servicios)
```
{
    "included": "agua luz",
    "excluded": "ascensor"
}
```
(si no llegase a tener sercvicios)
```
{
    "included": null,
    "excluded": null
}
```


### Notes

- El endpoint devuelve un único objeto con los servicios asociados a la propiedad.
- Los campos `included` y `excluded` indican los servicios incluidos y no incluidos en el alquiler.



# Incidents

## Create an Incident

Create an incident with all the information.

### Route
`POST /incidents/create`

### Body:

All fields are required.

```
{
    "asunto": "asuntotest",
    "descrip": "descripciontest",
    "id_owner": 1,
    "id_tenant": 1,
    "id_property": 1
}
```

### Error Codes

- 400: Missing field.


## Obtain Incidents

Obtain incidents by property id.
### Route
`GET /property/incidents/{property_id}`

### Request:

Property id is required

```
curl -X GET "http://localhost:8000/property/incidents/7"
```

### Error Codes

- 400: Missing Property.

### Response:

```
[
    {
        "id": 1,
        "issue": "asuntotest",
        "description": "descripciontest",
        "owner_id": 100,
        "tenant": {
            "id": 101,
            "first_name": "tenanttest",
            "last_name": "test",
            "phone_number": "22222222222",
            "email": "tenanttest@example.com"
        },
        "property_id": 7
    },
    {
        "id": 7,
        "issue": "asunto prueba",
        "description": "descripcion test",
        "owner_id": 100,
        "tenant": {
            "id": 101,
            "first_name": "tenanttest",
            "last_name": "test",
            "phone_number": "22222222222",
            "email": "tenanttest@example.com"
        },
        "property_id": 7
    }
]
```

## Update an Incident

Update an Incident with all the information.

### Route
`PUT /update/incident`

### Body:

All fields are required.

```
{
    "id": 2
    "asunto": "asunto test",
    "descrip": "descripcion test"
}
```

### Error Codes

- 400: Missing field
### Example of response 

```
{
    "message": "Incidente actualizado correctamente"
}
```

## Delete an Incident

Delete an existent Incident.

### Route
`DELETE /incidents/{id}`

### Body:

Incident id is required.

### Error Codes

- 404: Incident not found

### Example of response 

```
{
    "message": "Incidente eliminado correctamente",
    "id": id
}
```



# Changes 

## User now has field "type"

Important: the following endpoints are the only ones affected by the addition of the field type in User; all others continue to function as before. 

Changelog:

- In create user (`POST /register`), you need to add field type in the body of the request and on successfully create response with a Json body of user with the field type now.
```
{
    "first_name": "Marc",
    "last_name": "Gonzalez",
    "email": "marcg@example.com",
    "phone_number": "+34 612 532 457",
    "type": "owner"
}
```
- In login (`POST /login`), now field type is necessary for login.

(tenant)
```
{
    "id": 2,
    "first_name": "Pablo",
    "last_name": "Morralla",
    "email": "pablo@example.com",
    "phone_number": "611620552",
    "leasedProperty": {
        "id": 2,
        "address": "Calle Sol 9",
        "owner_fk": 1,
        "ciudad": "Sevilla",
        "pais": "España",
        "alquiler": 450
    },
    "type": "tenant"
    
}
```
(owner)
```
{
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone_number": "123456789",
    "ownedProperty": [
        {
            "id": 2,
            "address": "Calle Sol 9",
            "owner_fk": 1,
            "ciudad": "Sevilla",
            "pais": "España",
            "alquiler": 450
        },
        {
            "id": 3,
            "address": "Calle Mayor 123",
            "owner_fk": 1,
            "ciudad": "Madrid",
            "pais": "España",
            "alquiler": 750
        }
    ],
    "type": "owner"
}
```



