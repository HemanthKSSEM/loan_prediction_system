# Loan Approval Prediction System
**Enterprise-Grade AI-Assisted Fintech Platform**

This project is a comprehensive Machine Learning & Django full-stack application designed to automate and augment the loan approval process in a professional banking environment.

## Key Features & Architecture
- **Human-in-the-Loop AI:** Integrates Machine Learning predictions with human verification, demonstrating compliance-oriented AI workflows.
- **Enterprise Analytics Dashboard:** Built with Chart.js to monitor KPIs, monthly application trends, and business intelligence reporting.
- **AI Recommendation Panel:** Provides explainable AI outputs, complete with a Confidence Score progress bar, allowing Loan Officers to make informed override decisions.
- **Role-Based Access Control (RBAC):** Strict separation of privileges implementing the Principle of Least Privilege across Applicant, Loan Officer, and Admin roles.
- **Dual ML Engine:** Utilizes both Decision Tree (for explainability) and Artificial Neural Networks (ANN) for robust predictive modeling.
- **Modern UI/UX:** Features a polished, responsive interface with SweetAlert2 Toast notifications for all system events.

## Technologies Used
- **Backend:** Python, Django, SQLite
- **Machine Learning:** Scikit-Learn, TensorFlow/Keras, Pandas, NumPy
- **Frontend:** HTML5, CSS3, Bootstrap 5, Vanilla JS, Chart.js, SweetAlert2

## Installation & Setup

1. **Clone the repository** and navigate into the directory:
   ```bash
   cd loan_prediction_system
   ```

2. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Train the Initial ML Models** (Required before first use):
   ```bash
   python ml_model/train_model.py
   ```

5. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

## Demo Credentials
To explore the different Role-Based Access views, use the following pre-configured demo accounts:

| Role | Username | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin_demo` | `demo123` | Enterprise Analytics, User Management |
| **Loan Officer** | `officer_demo` | `demo123` | Application Verification, AI Overrides |
| **Applicant** | `user_demo` | `demo123` | Loan Application, History, EMI Calc |

## Project Structure
```text
loan_approval_system/
│
├── dataset/             # Source data for ML training
├── ml_model/            # Training scripts and serialized models (.pkl, .h5)
├── loan_app/            # Core Django application and Views
├── templates/           # HTML templates organized by role (admin/user)
├── static/              # CSS, JS, and image assets
├── requirements.txt     # Python dependencies
├── manage.py            # Django command-line utility
└── README.md            # Project documentation
```

---
*Developed for Final Year Academic Submission.*
