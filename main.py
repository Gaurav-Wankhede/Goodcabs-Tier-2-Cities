from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import routers

app = FastAPI(title="City Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routers.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Welcome to City Analysis API",
        "endpoints": {
            "city-performance": "/api/v1/analysis/city-performance",
            "city-fares": "/api/v1/analysis/city-fares",
            "city-ratings": "/api/v1/analysis/city-ratings",
            "city-demand": "/api/v1/analysis/city-demand",
            "city-daytype": "/api/v1/analysis/city-daytype",
            "city-repeat-passengers": "/api/v1/analysis/city-repeat-passengers",
            "target-achievement": "/api/v1/analysis/target-achievement",
            "rpr-metrics": "/api/v1/analysis/rpr-metrics",
            "rpr-factors": "/api/v1/analysis/rpr-factors",
            "tourism-business": "/api/v1/analysis/tourism-business",
            "mobility-trends": "/api/v1/analysis/mobility-trends",
            "partnerships": "/api/v1/analysis/partnerships",
            "data-collection": "/api/v1/analysis/data-collection"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)