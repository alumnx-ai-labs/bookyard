"""
Security dependencies for the API.
"""

import os
from fastapi import Header, HTTPException, status
from dotenv import load_dotenv

load_dotenv()

ADMIN_SECRET = os.getenv("ADMIN_SECRET")

async def get_admin_token(x_admin_secret: str = Header(..., alias="x-admin-secret")):
    """
    Validate the admin secret header.
    """
    if not ADMIN_SECRET:
        # If no secret is set in env, fail secure (or warn). 
        # Ideally, we should require it.
        # For this MVP dev setup, if not set, we might default to something or block.
        # Let's fail if not set to ensure they configure it.
        logger.error("ADMIN_SECRET not set in environment")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: Admin secret not set"
        )
        
    if x_admin_secret != ADMIN_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin secret"
        )
    
    return x_admin_secret

import logging
logger = logging.getLogger(__name__)
