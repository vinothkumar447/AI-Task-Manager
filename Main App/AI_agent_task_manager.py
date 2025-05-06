# st.set_page_config(page_title="AI Task Manager", layout="wide")
import streamlit as st
import sqlite3
import datetime
import spacy
from dateparser import parse as date_parse
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.cluster import KMeans
import os
from typing import Dict, List, Optional
import json
import uuid
import time
import random

# Load models
nlp = spacy.load("en_core_web_sm")
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

# Database setup
DB_NAME = 'tasks.db'
UPLOAD_FOLDER = 'task_documents'

quotes = [
    "“The secret of getting ahead is getting started.” – Mark Twain",
    "“Quality means doing it right when no one is looking.” – Henry Ford",
    "“Success is not the key to happiness. Happiness is the key to success.” – Albert Schweitzer",
    "“AI is not a threat, but a tool for productivity.”",
    "“Great things are done by a series of small things brought together.” – Vincent Van Gogh"
]
st.info(random.choice(quotes))

st.markdown(
    """
    <style>
    body, .stApp {
        background: linear-gradient(120deg, #e0eafc 0%, #cfdef3 100%) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

class AITaskManager:
    """Enhanced AI-powered task management system with Streamlit UI"""
    
    def __init__(self):
        self.setup_streamlit()
        self.setup_upload_folder()
        self.migrate_database()
        self.create_table()
        
    def setup_streamlit(self):
        """Configure Streamlit interface"""
        # st.set_page_config(page_title="AI Task Manager", layout="wide")
        st.title("🤖 AI-Powered Task Manager")
        st.markdown("""
            <style>
                .stTextInput input {font-size: 18px;}
                .task-card {border-radius: 10px; padding: 15px; margin: 10px 0; 
                           box-shadow: 0 2px 8px rgba(0,0,0,0.1); position: relative;}
                .high-priority {border-left: 5px solid #ff4b4b;}
                .normal-priority {border-left: 5px solid #f0f0f0;}
                .low-priority {border-left: 5px solid #ccc;}
                .completed-task {background-color: #f0f8ff;}
                .verified-task {background-color: #f0fff0;}
                /* VERIFICATION ENHANCEMENTS */
                .verification-badge {
                    display: inline-block;
                    padding: 3px 10px;
                    border-radius: 15px;
                    font-weight: bold;
                    font-size: 0.8em;
                    margin-left: 10px;
                }
                .verified-approved {
                    background-color: #4CAF50;
                    color: white;
                }
                .verified-revision {
                    background-color: #FFC107;
                    color: black;
                }
                .verified-rejected {
                    background-color: #F44336;
                    color: white;
                }
                .verification-stamp {
                    position: absolute;
                    right: 20px;
                    top: 10px;
                    transform: rotate(15deg);
                    opacity: 0.8;
                    font-family: 'Courier New', monospace;
                    font-weight: bold;
                    color: #4CAF50;
                    border: 3px solid #4CAF50;
                    padding: 5px 10px;
                    border-radius: 5px;
                }
                .verification-dialog {
                    animation: fadeIn 0.5s;
                    border-left: 4px solid #4CAF50;
                    padding: 15px;
                    margin-top: 10px;
                }
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .verification-comments {
                    font-style: italic;
                    color: #555;
                    margin-top: 5px;
                }
                .verification-header {
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 5px;
                    margin-bottom: 15px;
                }
            </style>
        """, unsafe_allow_html=True)
    
    def setup_upload_folder(self):
        """Create folder for uploaded documents"""
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
    
    def create_connection(self) -> sqlite3.Connection:
        """Create and return a database connection."""
        return sqlite3.connect(DB_NAME)
    
    def migrate_database(self):
        """Migrate existing database to new schema with verification columns"""
        with self.create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
            if not cursor.fetchone():
                return
            
            cursor.execute("PRAGMA table_info(tasks)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Add verification-related columns if they don't exist
            verification_columns = {
                'verification_comments': 'TEXT',
                'verification_evidence_path': 'TEXT',
                'verified_at': 'TEXT'
            }
            
            for column, col_type in verification_columns.items():
                if column not in columns:
                    try:
                        conn.execute(f"ALTER TABLE tasks ADD COLUMN {column} {col_type}")
                    except sqlite3.OperationalError as e:
                        st.warning(f"Could not add column {column}: {str(e)}")
            
            # Original migration logic
            regular_columns = {
                'title': 'TEXT',
                'description': 'TEXT',
                'start_date': 'TEXT',
                'due_date': 'TEXT',
                'priority': 'TEXT DEFAULT "Normal"',
                'category': 'TEXT DEFAULT "Other"',
                'status': 'TEXT DEFAULT "Pending"',
                'document_path': 'TEXT',
                'verification_status': 'TEXT',
                'reminder_sent': 'INTEGER DEFAULT 0'
            }
            
            for column, col_type in regular_columns.items():
                if column not in columns:
                    try:
                        conn.execute(f"ALTER TABLE tasks ADD COLUMN {column} {col_type}")
                    except sqlite3.OperationalError as e:
                        st.warning(f"Could not add column {column}: {str(e)}")
            
            # Special handling for created_at column
            if 'created_at' not in columns:
                try:
                    conn.execute("ALTER TABLE tasks ADD COLUMN created_at TEXT")
                    conn.execute("UPDATE tasks SET created_at = datetime('now') WHERE created_at IS NULL")
                    conn.execute("PRAGMA foreign_keys=off")
                    conn.execute("BEGIN TRANSACTION")
                    conn.execute("""
                        CREATE TABLE tasks_new (
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
                        )
                    """)
                    conn.execute("""
                        INSERT INTO tasks_new 
                        SELECT id, created_at, title, description, category, status, 
                               start_date, due_date, priority, document_path, 
                               verification_status, NULL, NULL, NULL, reminder_sent
                        FROM tasks
                    """)
                    conn.execute("DROP TABLE tasks")
                    conn.execute("ALTER TABLE tasks_new RENAME TO tasks")
                    conn.execute("COMMIT")
                    conn.execute("PRAGMA foreign_keys=on")
                except sqlite3.OperationalError as e:
                    st.warning(f"Could not add column created_at: {str(e)}")
            
            conn.commit()
    
    def create_table(self) -> None:
        """Create the tasks table if it doesn't exist."""
        with self.create_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
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
            ''')
            conn.commit()

    def save_uploaded_file(self, uploaded_file) -> Optional[str]:
        """Save uploaded file and return its path"""
        if uploaded_file is None:
            return None
            
        file_ext = os.path.splitext(uploaded_file.name)[1]
        filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        try:
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            return file_path
        except Exception as e:
            st.error(f"Error saving file: {str(e)}")
            return None

    def add_task(self, title: str, description: str, start_date: str, due_date: str, uploaded_file=None) -> None:
        """Add a new task with all details"""
        if not title.strip():
            st.warning("Please provide a task title")
            return
            
        document_path = self.save_uploaded_file(uploaded_file)
        
        with self.create_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO tasks 
                    (title, description, start_date, due_date, document_path, verification_status)
                    VALUES (?, ?, ?, ?, ?, ?);
                ''', (
                    title,
                    description,
                    start_date,
                    due_date,
                    document_path,
                    "Not Verified"
                ))
                conn.commit()
                st.success(f"✅ Task added")
                
            except sqlite3.Error as e:
                st.error(f"Database error: {str(e)}")

    def verify_task(self, task_id: int) -> None:
        """Enhanced verification workflow with comments and evidence"""
        with self.create_connection() as conn:
            conn.row_factory = sqlite3.Row
            task = conn.execute(
                "SELECT * FROM tasks WHERE id=?",
                (task_id,)
            ).fetchone()
            
        if task:
            with st.expander(f"🔍 Verify Task: {task['title']}", expanded=True):
                st.markdown("<h3 class='verification-header'>Task Details</h3>", unsafe_allow_html=True)
                cols = st.columns(2)
                with cols[0]:
                    st.write(f"**Description:** {task['description']}")
                    st.write(f"**Status:** {task['status']}")
                with cols[1]:
                    st.write(f"**Start Date:** {task['start_date']}")
                    st.write(f"**Due Date:** {task['due_date']}")
                
                if task['document_path']:
                    st.markdown(f"**Document:** [View File]({task['document_path']})")
                
                st.divider()
                st.markdown("<h3 class='verification-header'>Verification Process</h3>", unsafe_allow_html=True)
                
                # Verification options
                verification_status = st.selectbox(
                    "Verification Outcome*",
                    ["Verified - Approved", "Verified - Needs Revision", "Verified - Rejected"],
                    index=0,
                    key=f"verify_status_{task_id}"
                )
                
                # Verification comments
                verification_comments = st.text_area(
                    "Verification Comments*",
                    placeholder="Provide detailed feedback about the task completion...",
                    key=f"verify_comments_{task_id}"
                )
                
                # Evidence upload
                verification_evidence = st.file_uploader(
                    "Upload Verification Evidence (Optional)",
                    type=['pdf', 'jpg', 'png', 'docx'],
                    key=f"verify_evidence_{task_id}"
                )
                
                if st.button("Submit Verification", key=f"submit_verify_{task_id}"):
                    if not verification_comments:
                        st.error("Please provide verification comments")
                        return
                    
                    # Save verification evidence if provided
                    evidence_path = None
                    if verification_evidence:
                        evidence_path = self.save_uploaded_file(verification_evidence)
                    
                    # Update task with verification details
                    with self.create_connection() as conn:
                        conn.execute('''
                            UPDATE tasks SET 
                            verification_status=?,
                            verification_comments=?,
                            verification_evidence_path=?,
                            verified_at=datetime('now')
                            WHERE id=?
                        ''', (
                            verification_status,
                            verification_comments,
                            evidence_path,
                            task_id
                        ))
                        conn.commit()
                    
                    st.success("✅ Task verification submitted!")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()

    def visualize_tasks(self, tasks: List[Dict]) -> None:
        """Enhanced task display with verification status"""
        for task in tasks:
            # Set default values
            task.setdefault('description', '')
            task.setdefault('start_date', '')
            task.setdefault('due_date', '')
            task.setdefault('priority', 'Normal')
            task.setdefault('document_path', None)
            task.setdefault('verification_status', 'Not Verified')  # This ensures it's never None
            task.setdefault('status', 'Pending')
            task.setdefault('verification_comments', '')
            task.setdefault('verified_at', '')
            task.setdefault('verification_evidence_path', None)
            
            # Determine CSS classes
            task_class = "task-card"
            if task['status'] == 'Completed':
                task_class += " completed-task"
            if task['verification_status'] and task['verification_status'].startswith('Verified'):
                task_class += " verified-task"
            
            with st.container():
                # Verification badge
                verification_badge = ""
                if task['verification_status'] == 'Verified - Approved':
                    verification_badge = f"""
                        <div class='verification-stamp'>VERIFIED</div>
                        <span class='verification-badge verified-approved'>
                            ✓ {task['verification_status']}
                        </span>
                    """
                elif task['verification_status'] == 'Verified - Needs Revision':
                    verification_badge = f"""
                        <span class='verification-badge verified-revision'>
                            ↻ {task['verification_status']}
                        </span>
                    """
                elif task['verification_status'] == 'Verified - Rejected':
                    verification_badge = f"""
                        <span class='verification-badge verified-rejected'>
                            ✗ {task['verification_status']}
                        </span>
                    """
                
                # Main task card
                st.markdown(f"""
                    <div class="{task_class}">
                        <h3>{task['title']} {verification_badge}</h3>
                        <p><strong>Description:</strong> {task['description']}</p>
                        <p><strong>Dates:</strong> {task['start_date']} to {task['due_date']}</p>
                        <p><strong>Status:</strong> {task['status']}</p>
                        {f'<p><a href="{task["document_path"]}" target="_blank">View Document</a></p>' if task["document_path"] else ''}
                
                """, unsafe_allow_html=True)
                
                # Show verification details if verified
                if task['verification_status'] and task['verification_status'].startswith('Verified'):
                    with st.expander("Verification Details", expanded=False):
                        st.write(f"**Verified on:** {task['verified_at']}")
                        st.write(f"**Status:** {task['verification_status']}")
                        if task['verification_comments']:
                            st.write(f"**Comments:** {task['verification_comments']}")
                        if task['verification_evidence_path']:
                            st.markdown(f"**Evidence:** [View File]({task['verification_evidence_path']})")
                
                # Action buttons
                cols = st.columns(4)
                with cols[0]:
                    if task['status'] != 'Completed':
                        if st.button("Complete", key=f"complete_{task['id']}"):
                            self.update_task_status(task['id'], "Completed")
                            st.rerun()
                with cols[1]:
                    if st.button("Edit", key=f"edit_{task['id']}"):
                        self.edit_task(task['id'])
                with cols[2]:
                    if st.button("Delete", key=f"delete_{task['id']}"):
                        self.delete_task_and_file(task['id'])
                        st.rerun()
                with cols[3]:
                    if task['status'] == 'Completed' and task['verification_status'] in [None, 'Not Verified']:
                        if st.button("Verify", key=f"verify_{task['id']}"):
                            st.session_state['verify_task'] = task['id']
                            st.rerun()

    def delete_task_and_file(self, task_id: int) -> None:
        """Delete task and its associated documents"""
        with self.create_connection() as conn:
            conn.row_factory = sqlite3.Row
            task = conn.execute(
                "SELECT document_path, verification_evidence_path FROM tasks WHERE id=?",
                (task_id,)
            ).fetchone()
            
            # Delete associated files
            for file_path in [task['document_path'], task['verification_evidence_path']]:
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        st.error(f"Error deleting file: {str(e)}")
            
            try:
                conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
                conn.commit()
            except sqlite3.Error as e:
                st.error(f"Database error: {str(e)}")

    def update_task_status(self, task_id: int, status: str) -> None:
        """Update task status"""
        with self.create_connection() as conn:
            try:
                conn.execute(
                    "UPDATE tasks SET status=? WHERE id=?",
                    (status, task_id)
                )
                conn.commit()
            except sqlite3.Error as e:
                st.error(f"Database error: {str(e)}")

    def edit_task(self, task_id: int) -> None:
        """Edit task details"""
        with self.create_connection() as conn:
            conn.row_factory = sqlite3.Row
            task = conn.execute(
                "SELECT * FROM tasks WHERE id=?",
                (task_id,)
            ).fetchone()
            
        if task:
            with st.form(f"edit_{task_id}"):
                title = st.text_input("Title", value=task['title'])
                description = st.text_area("Description", value=task['description'])
                
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date", 
                        value=datetime.datetime.strptime(task['start_date'], '%Y-%m-%d').date() if task['start_date'] else datetime.date.today())
                with col2:
                    due_date = st.date_input("Due Date", 
                        value=datetime.datetime.strptime(task['due_date'], '%Y-%m-%d').date() if task['due_date'] else datetime.date.today())
                
                submitted = st.form_submit_button("Update")
                if submitted:
                    with self.create_connection() as conn:
                        try:
                            conn.execute('''
                                UPDATE tasks SET 
                                title=?, description=?, start_date=?, due_date=?
                                WHERE id=?
                            ''', (
                                title,
                                description,
                                start_date.isoformat(),
                                due_date.isoformat(),
                                task_id
                            ))
                            conn.commit()
                            st.rerun()
                        except sqlite3.Error as e:
                            st.error(f"Database error: {str(e)}")

    def show_verification_analytics(self):
        """Enhanced verification analytics dashboard"""
        with self.create_connection() as conn:
            conn.row_factory = sqlite3.Row
            stats = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN verification_status LIKE 'Verified%' THEN 1 ELSE 0 END) as verified,
                    SUM(CASE WHEN verification_status = 'Verified - Approved' THEN 1 ELSE 0 END) as approved,
                    SUM(CASE WHEN verification_status = 'Verified - Needs Revision' THEN 1 ELSE 0 END) as needs_revision,
                    SUM(CASE WHEN verification_status = 'Verified - Rejected' THEN 1 ELSE 0 END) as rejected,
                    SUM(CASE WHEN verification_evidence_path IS NOT NULL THEN 1 ELSE 0 END) as with_evidence
                FROM tasks
            """).fetchall()
        
        if stats and stats[0]['total'] > 0:
            stats = stats[0]
            with st.expander("📊 Verification Analytics Dashboard", expanded=True):
                tab1, tab2 = st.tabs(["Summary Metrics", "Detailed Insights"])
                
                with tab1:
                    cols = st.columns(4)
                    cols[0].metric("Total Tasks", stats['total'])
                    cols[1].metric("Completed", stats['completed'], 
                                f"{stats['completed']/stats['total']*100:.1f}%")
                    cols[2].metric("Verified", stats['verified'], 
                                f"{stats['verified']/stats['completed']*100:.1f}" 
                                if stats['completed'] > 0 else "N/A")
                    cols[3].metric("With Evidence", stats['with_evidence'], 
                                f"{stats['with_evidence']/stats['verified']*100:.1f}%" 
                                if stats['verified'] > 0 else "N/A")
                
                with tab2:
                    if stats['verified'] > 0:
                        st.subheader("Verification Breakdown")
                        verified_data = {
                            'Approved': stats['approved'],
                            'Needs Revision': stats['needs_revision'],
                            'Rejected': stats['rejected']
                        }
                        st.bar_chart(verified_data)
                        
                        # Recent verifications
                        st.subheader("Recent Verification Activity")
                        recent = conn.execute("""
                            SELECT title, verification_status, verified_at 
                            FROM tasks 
                            WHERE verified_at IS NOT NULL
                            ORDER BY verified_at DESC
                            LIMIT 5
                        """).fetchall()
                        for task in recent:
                            status_color = {
                                'Verified - Approved': 'green',
                                'Verified - Needs Revision': 'orange',
                                'Verified - Rejected': 'red'
                            }.get(task['verification_status'], 'blue')
                            
                            st.markdown(f"""
                                <div style="margin-bottom: 10px; padding: 10px; border-radius: 5px; border-left: 4px solid {status_color};">
                                    <strong>{task['title']}</strong><br>
                                    <span style="color: {status_color}">{task['verification_status']}</span> • 
                                    {task['verified_at']}
                                </div>
                            """, unsafe_allow_html=True)

    def run(self):
        # Only set/reset session state before widgets are created!
        if st.session_state.get("clear_new_task_form"):
            st.session_state["new_task_title"] = ""
            st.session_state["new_task_description"] = ""
            st.session_state["new_task_start_date"] = datetime.date.today()
            st.session_state["new_task_due_date"] = datetime.date.today() + datetime.timedelta(days=7)
            st.session_state["clear_new_task_form"] = False

        if "new_task_title" not in st.session_state:
            st.session_state["new_task_title"] = ""
        if "new_task_description" not in st.session_state:
            st.session_state["new_task_description"] = ""
        if "new_task_start_date" not in st.session_state:
            st.session_state["new_task_start_date"] = datetime.date.today()
        if "new_task_due_date" not in st.session_state:
            st.session_state["new_task_due_date"] = datetime.date.today() + datetime.timedelta(days=7)

        # Now create your widgets
        with st.expander("➕ Assign New Task", expanded=True):
            with st.form("task_input"):
                title = st.text_input("Task Title*", placeholder="Enter task title", key="new_task_title")
                description = st.text_area("Description", placeholder="Enter task details", key="new_task_description")
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date", datetime.date.today(), key="new_task_start_date")
                with col2:
                    due_date = st.date_input("Due Date", datetime.date.today() + datetime.timedelta(days=7), key="new_task_due_date")
                uploaded_file = st.file_uploader(
                    "Attach Document (Optional)",
                    type=['pdf', 'docx', 'txt', 'ppt', 'pptx', 'xls', 'xlsx']
                )
                submitted = st.form_submit_button("Assign Task")
                if submitted:
                    if not title.strip():
                        st.warning("Please provide a task title")
                    else:
                        self.add_task(
                            title,
                            description,
                            start_date.isoformat(),
                            due_date.isoformat(),
                            uploaded_file
                        )
                        st.session_state["clear_new_task_form"] = True
                        st.rerun()
        
        # Task management section
        st.subheader("📋 Your Tasks")
        col1, col2 = st.columns(2)
        
        with col1:
            filter_option = st.selectbox("Filter by:", ["All", "Pending", "Completed", "Verified"])
        
        with col2:
            search_query = st.text_input("Search tasks:", placeholder="Enter title or description")
        
        # Task display with filtering
        with self.create_connection() as conn:
            conn.row_factory = sqlite3.Row
            try:
                query = "SELECT * FROM tasks"
                conditions = []
                
                if filter_option != "All":
                    if filter_option == "Verified":
                        conditions.append("verification_status LIKE 'Verified%'")
                    elif filter_option == "Completed":
                        conditions.append("status = 'Completed'")
                    else:
                        conditions.append(f"status = '{filter_option}'")
                
                if search_query:
                    conditions.append(f"(title LIKE '%{search_query}%' OR description LIKE '%{search_query}%')")
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY due_date ASC"
                tasks = conn.execute(query).fetchall()
                
                if tasks:
                    self.visualize_tasks([dict(task) for task in tasks])
                else:
                    st.info("No tasks found matching your criteria")
            except sqlite3.Error as e:
                st.error(f"Database error: {str(e)}")
        
        # Verification analytics
        self.show_verification_analytics()

        st.markdown("""
            <hr>
            <div style='text-align: center; color: #888; font-size: 0.95em;'>
                Made with ❤️ using Vinothkumar  | <b>Your ONEDATA SOFTWARE SOLUTIONS PRIVATE LIMITED</b> | © 2025
            </div>
        """, unsafe_allow_html=True)

        with st.sidebar:
            st.header("📝 How to Use")
            st.markdown("""
            1. **Assign New Task:** Fill in the details and click 'Assign Task'.
            2. **Manage Tasks:** Mark as complete, edit, or delete tasks.
            3. **Verify:** After completion, verify tasks with comments and evidence.
            4. **Analytics:** View verification stats and recent activity.
            """)
            st.success("Tip: Use the search and filter options to quickly find tasks!")
            st.markdown("---")

if __name__ == "__main__":
    manager = AITaskManager()
    manager.run()
    
    # Handle task verification if triggered
    if 'verify_task' in st.session_state:
        task_id = st.session_state['verify_task']
        with manager.create_connection() as conn:
            conn.row_factory = sqlite3.Row
            task = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if task:
            # If not verified, show the verification form
            if task['verification_status'] in [None, '', 'None', 'Not Verified']:
                manager.verify_task(task_id)