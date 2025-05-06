# 🤖 AI-Powered Task Manager with Verification System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57)
![NLP](https://img.shields.io/badge/AI-spaCy%20%2B%20Transformers-09A3D5)

**Developed by:** [Your Name]  
**Organization:** [Your Company/University]  
**Project Duration:** [Month/Year - Present]  

<div align="center">
  <img src="assets/demo.gif" alt="Application Demo" width="800">
</div>

## ✨ Key Features I Implemented

### 🧠 AI-Powered Task Management
- **NLP Processing**: Integrated spaCy for intelligent task analysis and categorization
- **Smart Clustering**: Developed sentence embedding system using Sentence Transformers
- **Future AI Integration**: Designed architecture for OpenAI API expansion

### 🔍 Robust Verification Workflow
- **Three-State System**: Engineered approval workflow (Approved/Needs Revision/Rejected)
- **Evidence Handling**: Implemented secure document upload system with UUID file naming
- **Audit Trail**: Created timestamped verification records with comments

### 📊 Interactive Analytics
- **Data Visualization**: Built real-time dashboard with Streamlit components
- **Performance Metrics**: Developed completion rate and verification analytics
- **User-Friendly UI**: Designed responsive task cards with status indicators

## 🛠️ Technical Implementation

### Core Technologies
| Component | Technology | My Contribution |
|-----------|------------|-----------------|
| Frontend | Streamlit | Custom UI components with CSS styling |
| Backend | Python 3.8+ | Business logic and state management |
| Database | SQLite | Schema design and migration system |
| AI | spaCy + Transformers | NLP pipeline integration |

### Key Code Features
```python
# Example of verification system I implemented
def verify_task(self, task_id: int) -> None:
    """Handles the complete verification workflow"""
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
