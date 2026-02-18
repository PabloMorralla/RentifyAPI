
from fastapi import FastAPI

from Services.users import router as users_router
from Services.services import router as services_router
from Services.properties import router as properties_router
from Services.tenants import router as tenants_router
from Services.incidents import router as incidents_router


app = FastAPI()

app.include_router(users_router)
app.include_router(services_router)
app.include_router(properties_router)
app.include_router(tenants_router)
app.include_router(incidents_router)


