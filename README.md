```markdown
# Python USSD Server

A custom USSD server implementation built with Python and FastAPI, simulating telecom USSD functionality without external APIs.

## Features

- 🚀 Full USSD session management
- 📱 Simulated phone interface
- ⏱️ Session timeout handling
- 🌐 REST API interface
- 🧩 Modular menu system
- 📊 Session tracking

## Prerequisites

- Python 3.8+
- pip

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/manziosee/ussd-server.git
   cd ussd-server
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Project

### Start the USSD Server
```bash
uvicorn app.main:app --reload
```

### Run the USSD Simulator (in another terminal)
```bash
python ussd_client.py
```

## Project Structure

```
ussd-server/
├── .env                    # Environment variables
├── .gitignore              # Git ignore rules
├── app/                    # Main application code
│   ├── __init__.py
│   ├── config.py           # Configuration settings
│   ├── main.py             # FastAPI application
│   └── ussd_engine.py      # USSD logic and session management
├── tests/                  # Test cases
├── ussd_client.py          # USSD simulator client
├── requirements.txt        # Dependencies
└── README.md               # This file
```

## API Endpoints

- `POST /ussd` - Handle USSD requests
  - Parameters:
    - `session_id` (string)
    - `phone_number` (string, optional)
    - `user_input` (string)
- `GET /sessions` - View active sessions (debug)

## USSD Flow Example

1. Start the client (`python ussd_client.py`)
2. Server responds with main menu:
   ```
   Welcome to MyUSSD
   1. Account
   2. Airtime
   3. Data
   4. Payments
   ```
3. Select option 2 (Airtime)
4. Then option 1 (Buy Airtime)
5. Enter amount when prompted

## Configuration

Edit `.env` file:
```ini
SESSION_TIMEOUT=300  # Session timeout in seconds
DEBUG=True          # Debug mode
```

## Testing

Run tests (after implementing them):
```bash
python -m pytest tests/
```

## Deployment

For production deployment:
1. Set `DEBUG=False` in `.env`
2. Use a production WSGI server like Gunicorn:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```

## Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
