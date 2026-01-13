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
    "password": "password1234"
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
    }
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
    "leasedProperty": null
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
    ]
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


