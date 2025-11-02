# Lexsy Document Assistant

Lexsy Document Assistant is a full-stack web app built for the Lexsy software engineering assignment. It helps founders and legal teams upload legal document templates, identify dynamic placeholders, collect the missing information through a guided chat workflow, and download the completed document with the original formatting preserved.

- **Live app:** https://main.d2dczcrek6651z.amplifyapp.com/
- **Tech stack:** React (Vite) + Tailwind CSS frontend, FastAPI backend, python-docx + Mammoth for document processing, AWS Amplify & App Runner for hosting.

## Key features

- **Smart placeholder detection** – Scans uploaded `.docx` templates for bracketed placeholders (e.g., `[Company Name]`) across paragraphs, tables, headers, and footers, and normalizes underscore-based currency blanks into descriptive fields.
- **Guided conversational intake** – Presents each placeholder as a natural-language question inside a chat UI, tracks conversation history, and keeps focus in the input box for fast data entry.
- **Real-time progress tracking** – Displays the number of remaining fields, shows typing indicators while the backend is processing, and promotes preview/download once everything is filled.
- **Preview & download** – Generates an HTML preview (via Mammoth) for quick validation, and streams the finalized `.docx` with the original styles, tables, and headers intact.
- **Stateless hosting** – Frontend served via AWS Amplify, backend containerized on AWS App Runner with simple in-memory storage for the active session.

## Project structure

```
Lexsy-Doc-App/
├── backend/            # FastAPI service for upload, chat logic, preview, and generation
│   ├── api/            # HTTP routes & request models
│   ├── core/           # Document utilities and Pydantic models
│   ├── storage/        # In-memory storage of the latest upload/session
│   └── requirements.txt
├── frontend/           # React + Vite single-page application
│   ├── src/App.jsx     # Main UI with upload, chat, preview, and download flows
│   └── ...
└── README.md           # Project overview (this file)
```

## Getting started locally

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm 9+

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/Lexsy-Doc-App.git
cd Lexsy-Doc-App
```

### 2. Run the backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
python -m backend.main
```

The server exposes the API at `http://localhost:8000` with automatic docs at `http://localhost:8000/docs`.

### 3. Run the frontend (React + Vite)

```bash
cd ../frontend
cp .env.local.example .env.local  # see below if this file is missing
npm install
npm run dev
```

If the sample env file is not present, create `frontend/.env.local` with the API base URL:

```
VITE_API_BASE_URL=http://localhost:8000
```

Then open `http://localhost:5173` to use the app.

## API overview

| Method | Endpoint          | Description |
| ------ | ----------------- | ----------- |
| POST   | `/upload`         | Accepts a `.docx` file, extracts placeholders, and stores the document in memory. |
| POST   | `/chat`           | Processes conversation history, determines the next placeholder question, and tracks completion status. |
| POST   | `/preview_html`   | Returns an HTML rendering of the filled document for in-app preview. |
| POST   | `/generate`       | Streams the completed `.docx` file for download. |
| GET    | `/healthz`        | Lightweight health check used by App Runner. |

All endpoints live under the FastAPI application served at `VITE_API_BASE_URL`.

## Deployment notes

- **Frontend (AWS Amplify):** Builds the Vite app on every push to `main`, injects the production `VITE_API_BASE_URL`, and serves the static bundle globally over HTTPS.
- **Backend (AWS App Runner):** Containerized FastAPI service with auto-scaling and built-in health checks. CORS is restricted to the Amplify domain for security.
- **Storage considerations:** The current build stores the uploaded document and placeholder metadata in memory for simplicity. A shared store (S3/DynamoDB/Redis) would be necessary to support multi-user sessions at scale.

## Sample template

The assignment includes a SAFE financing template with bracketed placeholders. Uploading that document demonstrates the full flow from placeholder detection through preview and download.

## Future enhancements

- Persist sessions per user (e.g., via Cognito + DynamoDB) so multiple founders can collaborate simultaneously.
- Replace the rule-based question flow with an LLM-powered assistant that can clarify ambiguous responses and surface risks.
- Add inline editing of detected placeholders before starting the chat and support additional template formats (PDF, Google Docs).

---

This project was built within the two-day Lexsy assignment window to highlight pragmatic full-stack execution, attention to UX, and clear documentation.
