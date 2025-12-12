from fastapi import FastAPI
from src.config.database import DatabaseConfig
from src.routes.organization_routes import router as organization_router
from src.routes.admin_routes import router as admin_router

app = FastAPI(
    title="Organization Management Service",
    description="Multi-tenant organization management system",
    version="1.0.0",
)

# Include routers
app.include_router(organization_router)
app.include_router(admin_router)

@app.on_event("startup")
async def startup_event():
    """Initialize database indexes on startup."""
    DatabaseConfig.initialize_indexes()
    print("Database indexes initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    DatabaseConfig.close_connection()
    print("Database connection closed")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Organization Management Service",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
