import time
from datetime import datetime, timedelta
from app.config import settings
from app.models import User, Session, Transaction
from app.auth import AuthManager
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class USSDSessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.menu_tree = self._build_menu_tree()

    def _build_menu_tree(self) -> Dict:
        """Build the USSD menu structure"""
        return {
            "main": {
                "text": "Welcome to MyUSSD\n1. Account\n2. Airtime\n3. Data\n4. Payments\n5. Help",
                "options": {
                    "1": "account",
                    "2": "airtime",
                    "3": "data",
                    "4": "payments",
                    "5": "help"
                }
            },
            "account": {
                "text": "Account Services\n1. Balance\n2. Mini Statement\n3. Change PIN\n0. Back",
                "options": {
                    "1": "account_balance",
                    "2": "account_statement",
                    "3": "change_pin",
                    "0": "main"
                },
                "auth_required": True
            },
            "account_balance": {
                "text": "Your account balance is: {balance}\n0. Back",
                "action": self._get_account_balance,
                "auth_required": True,
                "options": {
                    "0": "account"
                }
            },
            "help": {
                "text": "Help Center\n1. Contact Support\n2. FAQs\n0. Back",
                "options": {
                    "1": "contact_support",
                    "2": "faqs",
                    "0": "main"
                }
            }
        }

    def handle_request(
        self,
        session_id: str,
        phone_number: str,
        user_input: str = "",
        network_code: Optional[str] = None,
        service_code: Optional[str] = None
    ) -> str:
        """
        Handle USSD request
        
        Args:
            session_id: Unique session ID
            phone_number: User's phone number
            user_input: User input
            network_code: Mobile network code
            service_code: USSD service code
            
        Returns:
            USSD response string (CON or END)
        """
        try:
            # Initialize or get existing session
            session = self._get_or_create_session(session_id, phone_number)
            
            # Check for session timeout
            if self._is_session_expired(session):
                self._end_session(session_id)
                return "END Session timed out. Please start again."
            
            # Process user input
            return self._process_input(session, user_input)
            
        except Exception as e:
            logger.error(f"Error handling USSD request: {str(e)}", exc_info=True)
            return "END System error occurred. Please try again later."

    def _get_or_create_session(self, session_id: str, phone_number: str) -> Dict:
        """Get existing session or create new one"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session["last_active"] = time.time()
            return session
            
        # Create new session
        session = {
            "session_id": session_id,
            "phone": phone_number,
            "current_menu": "main",
            "data": {},
            "created_at": time.time(),
            "last_active": time.time(),
            "authenticated": False
        }
        
        # Save to database
        Session.create({
            "session_id": session_id,
            "phone": phone_number,
            "status": "active",
            "created_at": datetime.now().isoformat()
        })
        
        self.sessions[session_id] = session
        return session

    def _is_session_expired(self, session: Dict) -> bool:
        """Check if session has expired"""
        last_active = session.get("last_active", 0)
        return (time.time() - last_active) > settings.SESSION_TIMEOUT

    def _process_input(self, session: Dict, user_input: str) -> str:
        """Process user input and navigate menus"""
        current_menu = session.get("current_menu", "main")
        menu = self.menu_tree.get(current_menu, {})
        
        # Handle empty input (initial request)
        if not user_input:
            return self._format_response(menu.get("text", "Invalid menu"))
            
        # Handle back command
        if user_input == "0":
            session["current_menu"] = menu.get("options", {}).get("0", "main")
            return self._process_input(session, "")
            
        # Handle menu options
        next_menu = menu.get("options", {}).get(user_input)
        
        if next_menu:
            # Check if authentication is required
            if self.menu_tree.get(next_menu, {}).get("auth_required"):
                if not session.get("authenticated"):
                    session["next_menu"] = next_menu
                    session["current_menu"] = "auth_prompt"
                    return "CON Please enter your PIN:"
                    
            session["current_menu"] = next_menu
            
            # Execute menu action if defined
            menu_action = self.menu_tree.get(next_menu, {}).get("action")
            if menu_action:
                return menu_action(session)
                
            return self._process_input(session, "")
            
        # Handle PIN input for authentication
        if current_menu == "auth_prompt":
            authenticated, message = AuthManager.authenticate(
                session["phone"],
                user_input
            )
            
            if authenticated:
                session["authenticated"] = True
                next_menu = session.get("next_menu", "main")
                session["current_menu"] = next_menu
                return self._process_input(session, "")
            else:
                return f"END {message}"
                
        # Handle invalid input
        return "END Invalid selection. Please try again."

    def _format_response(self, text: str, session: Optional[Dict] = None) -> str:
        """Format USSD response (CON or END)"""
        if not text:
            return "END Thank you for using our service"
            
        if "\n" in text or len(text) > 160:
            return f"CON {text}"
        return f"END {text}"

    def _get_account_balance(self, session: Dict) -> str:
        """Get account balance (example action)"""
        # In a real app, fetch from database or external service
        balance = "1000.00"  # Example balance
        text = self.menu_tree["account_balance"]["text"].format(balance=balance)
        return self._format_response(text)

    def get_active_sessions(self) -> List[Dict]:
        """Get all active sessions"""
        try:
            return list(self.sessions.values())
        except Exception as e:
            logger.error(f"Error getting active sessions: {str(e)}")
            return []

    def cleanup_sessions(self) -> int:
        """Cleanup expired sessions"""
        count = 0
        current_time = time.time()
        
        for session_id, session in list(self.sessions.items()):
            if (current_time - session.get("last_active", 0)) > settings.SESSION_TIMEOUT:
                self._end_session(session_id)
                count += 1
                
        return count

    def _end_session(self, session_id: str):
        """End a session"""
        if session_id in self.sessions:
            session = self.sessions.pop(session_id)
            Session.update(session_id, {
                "status": "ended",
                "ended_at": datetime.now().isoformat()
            })
            logger.info(f"Ended session {session_id}")