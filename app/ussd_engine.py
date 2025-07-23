import time
from typing import Dict
from app.config import settings

class USSDSessionManager:
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        self.menu_tree = {
            "main": {
                "text": "Welcome to MyUSSD\n1. Account\n2. Airtime\n3. Data\n4. Payments",
                "options": {
                    "1": "account",
                    "2": "airtime",
                    "3": "data",
                    "4": "payments"
                }
            },
            "account": {
                "text": "Account Services\n1. Balance\n2. Mini Statement\n0. Back",
                "options": {
                    "1": "account_balance",
                    "2": "account_statement",
                    "0": "main"
                }
            },
            "airtime": {
                "text": "Airtime Services\n1. Buy Airtime\n2. Airtime Transfer\n0. Back",
                "options": {
                    "1": "buy_airtime",
                    "2": "transfer_airtime",
                    "0": "main"
                }
            },
            "buy_airtime": {
                "text": "Enter amount:",
                "options": {},
                "handler": self._handle_airtime_purchase
            }
        }

    def _clean_expired_sessions(self):
        now = time.time()
        expired = [sid for sid, session in self.sessions.items() 
                  if now - session['last_active'] > settings.SESSION_TIMEOUT]
        for sid in expired:
            del self.sessions[sid]

    def _handle_airtime_purchase(self, session: dict, amount: str):
        try:
            amount = float(amount)
            return f"END You have successfully purchased ${amount:.2f} airtime"
        except ValueError:
            return "CON Invalid amount. Please enter a valid number:"

    def handle_request(self, session_id: str, user_input: str, phone_number: str = None):
        self._clean_expired_sessions()
        
        # Initialize new session if needed
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'current_menu': 'main',
                'data': {},
                'phone_number': phone_number,
                'last_active': time.time()
            }
        
        session = self.sessions[session_id]
        session['last_active'] = time.time()
        
        current_menu = session['current_menu']
        menu = self.menu_tree.get(current_menu, {})
        
        # Handle initial request
        if user_input == "":
            return "CON " + menu.get('text', 'Invalid menu')
        
        # Handle back command
        if user_input == "0" and current_menu != "main":
            session['current_menu'] = "main"
            return "CON " + self.menu_tree['main']['text']
        
        # Check if current menu has a custom handler
        if 'handler' in menu:
            return menu['handler'](session, user_input)
        
        # Normal menu navigation
        next_menu = menu.get('options', {}).get(user_input)
        if next_menu:
            session['current_menu'] = next_menu
            return "CON " + self.menu_tree[next_menu]['text']
        
        return "END Invalid option selected"

    def end_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]