from app.models import User
from app.config import settings
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class AuthManager:
    @staticmethod
    def authenticate(phone_number: str, pin: str) -> Tuple[bool, str]:
        """
        Authenticate user with phone number and PIN
        
        Args:
            phone_number: User's phone number
            pin: User's PIN
            
        Returns:
            Tuple of (success, message)
        """
        if not phone_number or not pin:
            return False, "Phone number and PIN are required"
            
        try:
            attempts = User.get_pin_attempts(phone_number)
            
            if attempts >= settings.PIN_ATTEMPTS_LIMIT:
                logger.warning(f"Account locked for {phone_number} - too many failed attempts")
                return False, "Account locked. Too many failed attempts."
            
            if User.verify_pin(phone_number, pin):
                User.update_pin_attempts(phone_number, 0)
                logger.info(f"Successful authentication for {phone_number}")
                return True, "Authentication successful"
            else:
                User.update_pin_attempts(phone_number, attempts + 1)
                remaining = settings.PIN_ATTEMPTS_LIMIT - (attempts + 1)
                logger.warning(f"Failed authentication attempt for {phone_number}")
                return False, f"Invalid PIN. {remaining} attempts remaining."
                
        except Exception as e:
            logger.error(f"Authentication error for {phone_number}: {str(e)}")
            return False, "System error during authentication"

    @staticmethod
    def check_auth_required(menu: str) -> bool:
        """
        Check if a menu requires authentication
        
        Args:
            menu: Menu identifier
            
        Returns:
            bool: True if authentication required
        """
        auth_required_menus = {
            'account_balance',
            'account_statement',
            'buy_airtime',
            'transfer_airtime',
            'make_payment',
            'change_pin'
        }
        return menu in auth_required_menus