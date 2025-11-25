"""Admin endpoints for database management."""
from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep
from app.seed import seed_sample_data

router = APIRouter()


@router.post("/seed", status_code=status.HTTP_200_OK)
def seed_database(session: SessionDep) -> dict:
    """Seed the database with sample data.
    
    This endpoint runs the seed script to populate the database with:
    - Demo Factory
    - 3 Machines (Machine 0, Machine 1, Machine 2)
    - 3 Task Templates (Cutting, Assembly, Painting)
    - 3 Sample Job Orders
    
    The seed script is idempotent - it won't create duplicates if data already exists.
    """
    try:
        # The seed function uses its own session_scope, so we don't need the session parameter
        # but we keep it for consistency with other endpoints
        seed_sample_data()
        return {
            "status": "success",
            "message": "Sample data seeded successfully. Check /api/factories to see the demo factory."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to seed database: {str(e)}"
        )

