# AI Health Chatbot 🩺🤖

An AI-powered health assistant chatbot named **Tam**, built with Flask and the Groq API. Patients can register, chat about symptoms and health concerns, and receive caring, conversational guidance — with automatic escalation instructions for emergencies.

## Features

- **Patient registration** — captures name, age, sex, address, contact number, and medical history before starting a chat.
- **Conversational AI assistant ("Tam")** — powered by Groq's `llama-3.1-8b-instant` model, with a system prompt tuned for empathetic, context-aware health conversations.
- **Persistent chat history** — sessions and messages are stored in a database so the assistant remembers prior context within a conversation.
- **Emergency handling** — automatically instructs users to call the Philippines emergency hotline (911) when a message suggests a life-threatening situation (e.g. chest pain, difficulty breathing, suicidal thoughts).
- **Session management** — start a new chat session at any time, wiping prior context.
- **Patient lookup** — fetch stored patient records by ID.
- **Health check endpoint** — used to confirm the backend is ready (handy for loading screens).
- **Static frontend** — plain HTML/CSS/JS registration form and chat UI served directly by Flask.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, Flask-CORS |
| AI | Groq API (`llama-3.1-8b-instant`) |
| Database | PostgreSQL (`psycopg2-binary`), with MySQL connector also available |
| Frontend | HTML, CSS, JavaScript |
| Deployment | Render (`render.yaml`, `gunicorn`) |

## Project Structure

```
AI_Health_Chatbot/
├── app.py              # Flask application & API routes
├── database.py         # Database access layer (patients, sessions, messages)
├── init_db.py          # Database table initialization
├── form.html / form.css   # Patient registration form
├── index.html           # Chat interface
├── waiting.html         # Loading/waiting screen
├── script.js            # Frontend chat logic
├── style.css             # Chat UI styling
├── test_db.py            # Database connectivity test script
├── test_groq.py           # Groq API test script
├── requirements.txt        # Python dependencies
├── runtime.txt              # Python runtime version (for deployment)
└── render.yaml                # Render deployment configuration
```

## Getting Started

### Prerequisites

- Python 3.x
- A PostgreSQL (or MySQL) database
- A [Groq API key](https://console.groq.com/)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AndreNathanielBarbasa/AI_Health_Chatbot.git
   cd AI_Health_Chatbot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your credentials:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   DATABASE_URL=your_database_connection_string_here
   ```

5. Run the app:
   ```bash
   python app.py
   ```

   The server starts on `http://localhost:5000` by default (or the port set via the `PORT` environment variable).

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the patient registration form |
| `POST` | `/register-patient` | Registers a new patient |
| `POST` | `/chat` | Sends a message to the AI assistant and gets a reply |
| `POST` | `/new-chat` | Starts a new chat session (clears history) |
| `GET` | `/patient/<patient_id>` | Retrieves patient information by ID |
| `GET` | `/health-check` | Returns server readiness status |

## Deployment

This project is configured for deployment on [Render](https://render.com/) via `render.yaml`, using `gunicorn` as the production WSGI server.

## Disclaimer

This chatbot provides general health information and is **not a substitute for professional medical advice, diagnosis, or treatment**. Always seek the advice of a qualified healthcare provider. In an emergency, contact your local emergency services immediately.

## Author

**Andre Nathaniel Barbasa**
- Portfolio: [andrenathanielbarbasa.github.io/andre-portfolio](https://andrenathanielbarbasa.github.io/andre-portfolio/)
- GitHub: [@AndreNathanielBarbasa](https://github.com/AndreNathanielBarbasa)
- LinkedIn: [andrenathanielbarbasa](https://linkedin.com/in/andrenathanielbarbasa)
- Email: dreisbetter@gmail.com
