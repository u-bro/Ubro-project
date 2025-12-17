from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse

from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import ResponseValidationError

from app.backend.middlewares.exception import setup_error_middleware
from app.backend.openapi_schema import custom_openapi
from app.backend.middlewares import install_db_middleware
from app.backend.routers import user_router
from app.backend.routers.ride import ride_router
from app.backend.routers.role import role_router
from app.backend.routers.driver_profile import driver_profile_router
from app.backend.routers.driver_document import driver_document_router
from app.backend.routers.phone_verification import phone_verification_router
from app.backend.routers.commission import commission_router
from app.backend.routers.driver_location import driver_location_router
from app.backend.routers.chat_message import chat_message_router
from app.backend.routers.transaction import transaction_router
from app.backend.routers.websocket import websocket_router
from app.backend.routers.documents import documents_router
# Optional debug router is disabled for smoke run

app = FastAPI()
app.openapi = lambda: custom_openapi(app)
install_db_middleware(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
setup_error_middleware(app)

API_PREFIX = "/api/v1"

app.include_router(user_router, tags=['Users'], prefix=API_PREFIX)
app.include_router(ride_router, tags=['Rides'], prefix=API_PREFIX)
app.include_router(role_router, tags=['Roles'], prefix=API_PREFIX)
app.include_router(driver_profile_router, tags=['DriverProfiles'], prefix=API_PREFIX)
app.include_router(driver_document_router, tags=['DriverDocuments'], prefix=API_PREFIX)
app.include_router(phone_verification_router, tags=['PhoneVerifications'], prefix=API_PREFIX)
app.include_router(commission_router, tags=['Commissions'], prefix=API_PREFIX)
app.include_router(driver_location_router, tags=['DriverLocations'], prefix=API_PREFIX)
app.include_router(chat_message_router, tags=['ChatMessages'], prefix=API_PREFIX)
app.include_router(transaction_router, tags=['Transactions'], prefix=API_PREFIX)
app.include_router(websocket_router, tags=['WebSocket'], prefix=API_PREFIX)
app.include_router(documents_router, tags=['Documents'], prefix=API_PREFIX)
# app.include_router(pg_errs_router, tags=["Debug"])


@app.exception_handler(ResponseValidationError)
async def validation_exception_handler(request: Request, exc: ResponseValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error occurred",
            # "errors": exc.errors(),
            "body": exc.body,
        },
    )


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


@app.get(f"{API_PREFIX}/health", tags=["General"]) 
async def health():
    return {"status": "ok"}
