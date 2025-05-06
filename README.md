
## 🤖 AI-Powered Task Manager with Verification System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)  
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B)  
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57)  
![NLP](https://img.shields.io/badge/AI-spaCy%20%2B%20Transformers-09A3D5)  
![License](https://img.shields.io/badge/License-MIT-green)

**Developed by:** [Your Name]  
**Organization:** [Your Company/University]  
**Project Duration:** [Month/Year - Present]  

<div align="center">
  <img src="assets/demo.gif" alt="Application Demo" width="800">
</div>

---

## ✨ Key Features I Implemented

### 🧠 AI-Powered Task Management
- **NLP Processing:** Integrated **spaCy** for intelligent task analysis and categorization
- **Smart Clustering:** Developed sentence embedding system using **Sentence Transformers**
- **Future AI Integration:** Designed architecture for **OpenAI API** expansion

### 🔍 Robust Verification Workflow
- **Three-State System:** Engineered approval workflow (Approved / Needs Revision / Rejected)
- **Evidence Handling:** Implemented secure document upload system with **UUID** file naming
- **Audit Trail:** Created timestamped verification records with comments

### 📊 Interactive Analytics
- **Data Visualization:** Built real-time dashboard with **Streamlit** components
- **Performance Metrics:** Developed completion rate and verification analytics
- **User-Friendly UI:** Designed responsive task cards with status indicators

---

## 🛠️ Technical Implementation

### Core Technologies

| Component  | Technology            | My Contribution                              |
|------------|----------------------|---------------------------------------------|
| Frontend   | Streamlit             | Custom UI components with CSS styling        |
| Backend    | Python 3.8+           | Business logic and state management          |
| Database   | SQLite                | Schema design and migration system           |
| AI         | spaCy + Transformers  | NLP pipeline integration                     |

---

## 📝 Key Code Example

```python
# Example: Verification system I implemented
def verify_task(self, task_id: int) -> None:
    """Handles the complete verification workflow."""
    with self.create_connection() as conn:
        task = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    
    # Verification UI components
    with st.expander(f"🔍 Verify Task: {task['title']}", expanded=True):
        verification_status = st.selectbox("Outcome", ["Approved", "Needs Revision", "Rejected"])
        verification_comments = st.text_area("Comments")
        
        if st.button("Submit Verification"):
            self._update_verification_status(
                task_id,
                verification_status,
                verification_comments
            )
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- 4GB RAM (8GB recommended)
- 500MB disk space

### How to Run (Development Setup)

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/ai-task-manager.git
cd ai-task-manager
```

2. **Set up the environment:**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

4. **Launch the application:**

```bash
streamlit run ai_task_manager.py
```

---

## 📌 What I Worked On

### Major Contributions
✅ Designed and implemented the complete verification workflow system  
✅ Developed the database schema with automatic migration capabilities  
✅ Created the analytics dashboard with interactive visualizations  
✅ Integrated NLP models for task processing  
✅ Implemented file attachment handling with secure storage

### Challenges Overcome
- **Database Migrations:** Solved schema evolution while preserving existing data
- **State Management:** Implemented session persistence in Streamlit
- **File Handling:** Developed secure document management system
- **UI/UX:** Created responsive design with custom CSS components

---

## 🔮 Future Enhancements

Planned improvements I would like to implement:

- 👥 **Team Collaboration:** Multi-user support with roles
- 📱 **Mobile App:** React Native wrapper for mobile access
- 🤖 **Advanced AI:** GPT integration for automatic task suggestions
- 📝 **Reporting:** PDF export for verification audits

---

## 🤝 How to Contribute

I welcome contributions to this project. Here's how you can help:

- Report bugs or suggest features via **Issues**
- Submit **Pull Requests** for improvements
- Share your use cases and feedback

---

## 📜 License

This project is licensed under the **MIT License** – see the `LICENSE` file for details.

---

✅ **Fully GitHub markdown-compatible!** Supports code syntax highlighting, tables, images, collapsible sections, and badges.
