
![Task Manager Interface](https://img.shields.io/badge/Status-Production_Ready-brightgreen)
![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-orange)

<div align="center">
  <img src="demo.gif" alt="App Demo" width="800">
</div>

## 📌 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [Database Schema](#-database-schema)
- [API Integration](#-api-integration)
- [Screenshots](#-screenshots)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🧠 AI-Powered Core
- NLP-based task analysis using spaCy
- Sentence embeddings for smart clustering
- OpenAI integration points (future-ready)

### 🔍 Verification Workflow
- Three-tier verification system:
  - ✅ Approved
  - 🔄 Needs Revision
  - ❌ Rejected
- Evidence uploads (PDF, images, docs)
- Timestamped audit trail

### 📊 Dashboard & Analytics
- Real-time completion statistics
- Verification success rates
- Document attachment metrics
- Interactive visualization

### ⚙️ Technical Highlights
- Automatic SQLite schema migration
- File management with UUID hashing
- Session-based state management
- Responsive Streamlit UI

## 🛠️ Tech Stack

**Frontend**:
- Streamlit (Python web framework)

**Backend**:
- SQLite (Embedded database)
- spaCy (NLP processing)
- Sentence Transformers (AI embeddings)

**Dependencies**:
```python
streamlit==1.22.0
spacy==3.5.0
sentence-transformers==2.2.2
scikit-learn==1.2.0
python-dateutil==2.8.2
dateparser==1.1.8
🚀 Installation
Prerequisites
Python 3.8+

4GB RAM (8GB recommended)

500MB disk space

Setup Guide
Clone the repository:

bash
git clone https://github.com/yourusername/ai-task-manager.git
cd ai-task-manager
Create virtual environment:

bash
python -m venv venv
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
Install dependencies:

bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
💻 Usage
Start the application:

bash
streamlit run ai_task_manager.py
Key workflows:

Create tasks with attachments

Mark tasks as complete

Verify completed tasks

View analytics dashboard

Automatic setup:

Creates tasks.db on first run

Makes task_documents/ folder

Handles database migrations

🗃️ Database Schema
sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    status TEXT DEFAULT 'Pending',
    start_date TEXT,
    due_date TEXT,
    priority TEXT DEFAULT 'Normal',
    document_path TEXT,
    verification_status TEXT,
    verification_comments TEXT,
    verification_evidence_path TEXT,
    verified_at TEXT,
    reminder_sent INTEGER DEFAULT 0
);
🔌 API Integration
Future Integration Points
python
# OpenAI API (Example)
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

# Potential usage for task suggestions
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Suggest task categories"}]
)
📸 Screenshots
Task Creation	Verification	Analytics
<img src="screenshots/create.png" width="300">	<img src="screenshots/verify.png" width="300">	<img src="screenshots/analytics.png" width="300">
🗺️ Roadmap
Core task management

Verification workflow

Basic analytics

Email notifications

Calendar integration

Advanced AI suggestions

Mobile responsive UI

🤝 Contributing
Fork the repository

Create your feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some amazing feature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request

📜 License
Distributed under the MIT License. See LICENSE for more information.

<div align="center"> Made with ❤️ by <Your Name> | <a href="https://yourcompany.com">Your Company</a> | © 2025 </div> ``
