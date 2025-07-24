from app.supabase_client import supabase
from datetime import datetime
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class User:
    @staticmethod
    def get_by_phone(phone: str) -> Optional[Dict[str, Any]]:
        """Get user by phone number"""
        try:
            if not phone:
                raise ValueError("Phone number is required")
                
            res = supabase.table("users").select("*").eq("phone", phone).execute()
            return res.data[0] if res.data else None
            
        except Exception as e:
            logger.error(f"User lookup error for {phone}: {str(e)}")
            return None

    @staticmethod
    def verify_pin(phone: str, pin: str) -> bool:
        """Verify user PIN"""
        try:
            user = User.get_by_phone(phone)
            if not user:
                return False
                
            # In a real app, use proper password hashing like bcrypt
            return user.get("pin") == pin
            
        except Exception as e:
            logger.error(f"PIN verification error for {phone}: {str(e)}")
            return False

    @staticmethod
    def get_pin_attempts(phone: str) -> int:
        """Get current PIN attempt count"""
        try:
            user = User.get_by_phone(phone)
            return user.get("pin_attempts", 0) if user else 0
        except Exception as e:
            logger.error(f"Error getting PIN attempts for {phone}: {str(e)}")
            return 0

    @staticmethod
    def update_pin_attempts(phone: str, attempts: int) -> bool:
        """Update PIN attempt count"""
        try:
            supabase.table("users").update({"pin_attempts": attempts}).eq("phone", phone).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating PIN attempts for {phone}: {str(e)}")
            return False

class Session:
    @staticmethod
    def create(session_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new session"""
        try:
            res = supabase.table("sessions").insert(session_data).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Session create error: {str(e)}")
            return None

    @staticmethod
    def update(session_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing session"""
        try:
            supabase.table("sessions").update(updates).eq("session_id", session_id).execute()
            return True
        except Exception as e:
            logger.error(f"Session update error for {session_id}: {str(e)}")
            return False

    @staticmethod
    def get(session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        try:
            res = supabase.table("sessions").select("*").eq("session_id", session_id).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Session get error for {session_id}: {str(e)}")
            return None

class Transaction:
    @staticmethod
    def create(tx_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new transaction"""
        try:
            res = supabase.table("transactions").insert(tx_data).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Transaction create error: {str(e)}")
            return None

    @staticmethod
    def get_for_user(phone_number: str, limit: int = 10) -> list:
        """Get transactions for a user"""
        try:
            res = supabase.table("transactions") \
                .select("*") \
                .eq("phone_number", phone_number) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            return res.data
        except Exception as e:
            logger.error(f"Error getting transactions for {phone_number}: {str(e)}")
            return []