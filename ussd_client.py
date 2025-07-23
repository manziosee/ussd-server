import requests
import random
import time
from datetime import datetime

class USSDSimulator:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = f"{base_url}/ussd"
        self.session_id = f"sim_{random.randint(100000, 999999)}"
        self.phone_number = f"+25078{random.randint(1000000, 9999999)}"
        self.start_time = datetime.now()
    
    def display_response(self, response):
        if response.startswith("CON "):
            print("\n" + response[4:])
        elif response.startswith("END "):
            print("\n" + response[4:])
            print("-" * 40)
            print("Session ended")
            return False
        else:
            print("\n" + response)
        return True
    
    def start(self):
        print("\n" + "=" * 40)
        print("USSD SIMULATOR")
        print(f"Started at: {self.start_time}")
        print(f"Session ID: {self.session_id}")
        print(f"Phone: {self.phone_number}")
        print("=" * 40 + "\n")
        
        # Initial request with empty input
        response = self._send_request("")
        if not self.display_response(response):
            return
        
        while True:
            try:
                user_input = input("> ").strip()
                response = self._send_request(user_input)
                if not self.display_response(response):
                    break
            except KeyboardInterrupt:
                print("\nSession terminated by user")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
                break
    
    def _send_request(self, user_input: str):
        try:
            resp = requests.post(
                self.base_url,
                data={
                    "session_id": self.session_id,
                    "phone_number": self.phone_number,
                    "user_input": user_input
                }
            )
            return resp.json()["response"]
        except requests.exceptions.RequestException as e:
            return f"END Network error: {str(e)}"

if __name__ == "__main__":
    simulator = USSDSimulator()
    simulator.start()