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




