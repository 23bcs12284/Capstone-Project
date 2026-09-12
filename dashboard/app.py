import os
import sys
import json
import yaml
import pickle
import requests
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# Add root folder to python path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from dashboard.components import apply_custom_css, render_kpi_card, render_status_badge

# Backend API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", f"http://localhost:{settings.PORT}")

st.set_page_config(
    page_title="Explainable AI Loan Approval System",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authentication token state in Streamlit session
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None

def get_headers():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

# ================= API WRAPPERS WITH STANDALONE FALLBACK =================

def check_backend_alive() -> bool:
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=1)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def make_request(method: str, path: str, json_data: dict = None, data: dict = None) -> dict:
    url = f"{API_BASE_URL}/{path.lstrip('/')}"
    try:
        if method.lower() == "post":
            if data:  # Form data for login
                res = requests.post(url, data=data, headers=get_headers(), timeout=10)
            else:
                res = requests.post(url, json=json_data, headers=get_headers(), timeout=10)
        else:
            res = requests.get(url, headers=get_headers(), timeout=10)
            
        if res.status_code in [200, 201]:
            return res.json()
        elif res.status_code == 401:
            st.session_state.token = None
            st.session_state.username = None
            st.session_state.role = None
            st.error("Authentication expired or invalid. Please login again.")
            return {"error": "Unauthorized"}
        else:
            return {"error": res.json().get("detail", "Request failed")}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection to API failed: {str(e)}"}

# Direct Local Execution Fallback (in case backend is not running)
def run_prediction_locally(app_data: dict) -> dict:
    from database.connection import SessionLocal
    from database.repository import DatabaseRepository
    import pandas as pd
    
    # Load pipeline
    with open(settings.MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(settings.SCALER_PATH, "rb") as f:
        transformer = pickle.load(f)
    with open(settings.ENCODER_PATH, "rb") as f:
        cleaner = pickle.load(f)
        
    cleaned_dict = cleaner.transform_dict(app_data)
    
    # Add age group
    age = cleaned_dict["age"]
    if age < 30:
        age_group = "Young"
    elif age <= 55:
        age_group = "Middle-aged"
    else:
        age_group = "Senior"
    cleaned_dict["age_group"] = age_group
    
    # Save to db
    db = SessionLocal()
    try:
        app_db = DatabaseRepository.create_loan_application(db, cleaned_dict)
        app_df = pd.DataFrame([cleaned_dict]).drop(columns=["applicant_id", "age_group"])
        trans_df = transformer.transform(app_df)
        
        prob = float(model.predict_proba(trans_df)[0, 1])
        pred_label = int(model.predict(trans_df)[0])
        
        pred_db = DatabaseRepository.create_prediction(
            db, 
            loan_application_id=app_db.id, 
            predicted_status=pred_label, 
            probability=prob, 
            model_version="local-fallback"
        )
        app_db.status = pred_label
        db.commit()
        
        return {
            "prediction_id": pred_db.id,
            "loan_application_id": app_db.id,
            "predicted_status": pred_label,
            "probability": prob,
            "model_version": "local-fallback",
            "created_at": str(pred_db.created_at)
        }
    finally:
        db.close()

def run_explanation_locally(prediction_id: int) -> dict:
    from database.connection import SessionLocal
    from database.repository import DatabaseRepository
    from explainability.shap_explainer import ShapExplainerManager
    from explainability.lime_explainer import LimeExplainerManager
    
    db = SessionLocal()
    try:
        pred = DatabaseRepository.get_prediction_by_id(db, prediction_id)
        app = pred.loan_application
        
        # Preprocessing
        with open(settings.MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        with open(settings.SCALER_PATH, "rb") as f:
            transformer = pickle.load(f)
            
        app_data = {
            "gender": app.gender, "age": app.age, "race": app.race, "income": app.income,
            "coapplicant_income": app.coapplicant_income, "credit_score": app.credit_score,
            "loan_amount": app.loan_amount, "loan_term": app.loan_term,
            "employment_years": app.employment_years, "home_ownership": app.home_ownership,
            "education": app.education, "self_employed": app.self_employed,
            "dependents": app.dependents, "property_area": app.property_area, "dti": app.dti
        }
        app_df = pd.DataFrame([app_data])
        trans_df = transformer.transform(app_df)
        
        train_df = pd.read_csv(settings.DATASET_PATH)
        train_X_raw = train_df.drop(columns=["applicant_id", "loan_status", "age_group"], errors="ignore")
        train_X_trans = transformer.transform(train_X_raw)
        
        lime_manager = LimeExplainerManager(train_X_trans)
        shap_manager = ShapExplainerManager(model, train_X_trans)
        
        predict_fn = model.predict_proba
        lime_contribs = lime_manager.get_contributions(trans_df.iloc[0], predict_fn)
        
        # Save plots
        waterfall_path = os.path.join(settings.ARTIFACTS_DIR, f"shap_waterfall_{prediction_id}.png")
        shap_manager.plot_waterfall(trans_df, waterfall_path)
        
        lime_html_path = os.path.join(settings.ARTIFACTS_DIR, f"lime_explanation_{prediction_id}.html")
        lime_manager.save_explanation_html(trans_df.iloc[0], predict_fn, lime_html_path)
        
        return {
            "prediction_id": prediction_id,
            "lime_contributions": lime_contribs,
            "shap_waterfall_path": waterfall_path,
            "lime_html_path": lime_html_path
        }
    finally:
        db.close()

def get_history_locally() -> list:
    from database.connection import SessionLocal
    from database.repository import DatabaseRepository
    db = SessionLocal()
    try:
        preds = DatabaseRepository.get_predictions_history(db, limit=100)
        res = []
        for p in preds:
            app = p.loan_application
            res.append({
                "prediction_id": p.id,
                "applicant_id": app.applicant_id,
                "gender": app.gender,
                "age": app.age,
                "race": app.race,
                "income": app.income,
                "credit_score": app.credit_score,
                "loan_amount": app.loan_amount,
                "dti": app.dti,
                "predicted_status": p.predicted_status,
                "probability": p.probability,
                "model_version": p.model_version,
                "created_at": p.created_at
            })
        return res
    finally:
        db.close()

def get_analytics_locally() -> dict:
    from database.connection import SessionLocal
    from database.repository import DatabaseRepository
    from fairness.auditor import FairnessAuditor
    db = SessionLocal()
    try:
        preds = DatabaseRepository.get_predictions_history(db, limit=2000)
        if not preds:
            return {"total_applications": 0, "approval_rate": 0.0, "average_credit_score": 0.0, "average_dti": 0.0, "fairness_audit": {}}
            
        records = []
        for p in preds:
            app = p.loan_application
            records.append({
                "gender": app.gender, "age": app.age, "age_group": app.age_group, "race": app.race,
                "loan_status": app.status if app.status is not None else p.predicted_status,
                "predicted_status": p.predicted_status
            })
        df_audit = pd.DataFrame(records)
        auditor = FairnessAuditor()
        audit_res = auditor.audit(df_audit, y_true_col="loan_status", y_pred_col="predicted_status")
        
        return {
            "total_applications": len(preds),
            "approval_rate": float(df_audit["predicted_status"].mean()),
            "average_credit_score": float(np.mean([p.loan_application.credit_score for p in preds])),
            "average_dti": float(np.mean([p.loan_application.dti for p in preds])),
            "fairness_audit": audit_res
        }
    finally:
        db.close()

# ================= DASHBOARD UI =================

apply_custom_css()

# Sidebar: System Connection Mode & Auth
is_alive = check_backend_alive()

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/bank.png", width=80)
    st.title("Control Center")
    
    # Show Connection Mode
    if is_alive:
        st.success("🟢 API Server Connected")
        st.caption(f"Backend listening at {API_BASE_URL}")
    else:
        st.warning("🟡 Standalone Mode")
        st.caption("Backend offline. Direct pipeline execution loaded.")
        
    st.markdown("---")
    
    # Authenticate Section
    if st.session_state.token is None and is_alive:
        st.subheader("Sign In")
        auth_mode = st.radio("Choose Action", ["Login", "Register"], label_visibility="collapsed")
        user_input = st.text_input("Username", key="auth_user")
        pass_input = st.text_input("Password", type="password", key="auth_pass")
        
        if st.button("Submit", use_container_width=True):
            if auth_mode == "Login":
                payload = {"username": user_input, "password": pass_input}
                res = make_request("POST", "/auth/login", data=payload)
                if "access_token" in res:
                    st.session_state.token = res["access_token"]
                    st.session_state.username = user_input
                    # Decode token role
                    try:
                        import jwt
                        decoded = jwt.decode(res["access_token"], options={"verify_signature": False})
                        st.session_state.role = decoded.get("role", "user")
                    except Exception:
                        st.session_state.role = "user"
                    st.success(f"Logged in as {user_input}")
                    st.rerun()
                else:
                    st.error(res.get("error", "Login failed"))
            else:
                payload = {"username": user_input, "password": pass_input, "role": "admin" if user_input == "admin" else "user"}
                res = make_request("POST", "/auth/register", json_data=payload)
                if "error" not in res:
                    st.success("Registration successful! Please log in.")
                else:
                    st.error(res.get("error", "Registration failed"))
    else:
        if is_alive:
            st.write(f"Logged in as: **{st.session_state.username}**")
            st.caption(f"Role: `{st.session_state.role}`")
            if st.button("Logout", use_container_width=True):
                st.session_state.token = None
                st.session_state.username = None
                st.session_state.role = None
                st.rerun()
        else:
            st.write("Logged in as: **Administrator (Local)**")
            st.caption("Role: `Superadmin`")

# Main Page Layout
st.markdown("<h1 style='margin-bottom: 0px;'>💳 Loan Approval Prediction Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B; font-size: 1.1rem; margin-top: 5px; margin-bottom: 25px;'>Explainable AI & Fair lending decision support system powered by LIME & SHAP.</p>", unsafe_allow_html=True)

# Select Tabs
tabs = st.tabs(["🏛️ Overview", "✍️ Loan application form", "📊 Analytics & History", "⚖️ Fairness Audit", "⚙️ System Logs"])

# ================= TAB 1: OVERVIEW =================
with tabs[0]:
    st.markdown("### System Description")
    st.write(
        "This software tool provides explainable machine learning predictions for credit risk auditing. "
        "It supports dual-explainability pipelines: SHAP for global model analysis and individual waterfalls, "
        "and LIME for local feature contributions on single applicant reviews. The fairness module measures model bias "
        "against protected variables (Gender, Age, and Race) and provides automated recommendations for compliance audits."
    )
    
    st.markdown("---")
    
    # Read Model Metadata
    metadata = {}
    if os.path.exists(os.path.join(settings.MODEL_DIR, "model_metadata.yaml")):
        with open(os.path.join(settings.MODEL_DIR, "model_metadata.yaml"), "r") as f:
            metadata = yaml.safe_load(f)
            
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Active Model Metadata")
        if metadata:
            st.info(f"🏆 **Selected Model**: {metadata.get('model_name', 'classifier').upper()}")
            st.markdown(f"**Hyperparameters used:**")
            st.code(json.dumps(metadata.get('params', {}), indent=2), language="json")
        else:
            st.warning("No model metadata found. Please execute the training pipeline first.")
            
    with col2:
        st.markdown("#### Model Performance Metrics")
        if metadata:
            metrics = metadata.get("metrics", {})
            st.markdown(f"- **ROC AUC**: `{metrics.get('roc_auc', 0.0):.4f}`")
            st.markdown(f"- **Accuracy**: `{metrics.get('accuracy', 0.0):.4f}`")
            st.markdown(f"- **F1 Score**: `{metrics.get('f1_score', 0.0):.4f}`")
            st.markdown(f"- **Precision**: `{metrics.get('precision', 0.0):.4f}`")
            st.markdown(f"- **Recall**: `{metrics.get('recall', 0.0):.4f}`")
        else:
            st.write("Run the ML pipeline script to generate model performance charts.")

# ================= TAB 2: PREDICTION FORM =================
with tabs[1]:
    if is_alive and st.session_state.token is None:
        st.warning("Please sign in from the sidebar to request new loan evaluations.")
    else:
        st.markdown("### Enter New Loan Application Details")
        
        with st.form("loan_prediction_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                applicant_id = st.text_input("Applicant ID", value="L98765")
                gender = st.selectbox("Gender", ["Male", "Female"])
                age = st.slider("Age", 18, 90, 35)
                race = st.selectbox("Race/Ethnicity", ["Caucasian", "African American", "Asian", "Hispanic"])
                education = st.selectbox("Education Level", ["Graduate", "Undergraduate"])
                
            with col2:
                income = st.number_input("Annual Income ($)", value=55000, step=1000)
                coapplicant_income = st.number_input("Coapplicant Annual Income ($)", value=0, step=1000)
                credit_score = st.slider("FICO Credit Score", 300, 850, 680)
                employment_years = st.number_input("Employment History (Years)", value=4.5, step=0.5)
                self_employed = st.selectbox("Self Employed?", ["No", "Yes"])
                
            with col3:
                loan_amount = st.number_input("Loan Amount Requested ($)", value=150000, step=5000)
                loan_term = st.selectbox("Loan Duration (Months)", [360, 180, 120])
                home_ownership = st.selectbox("Housing Status", ["Mortgage", "Own", "Rent"])
                dependents = st.selectbox("Dependents", ["0", "1", "2", "3+"])
                property_area = st.selectbox("Property Area Type", ["Semiurban", "Urban", "Rural"])
                
            submit_btn = st.form_submit_button("Predict & Explain Application", use_container_width=True)
            
        if submit_btn:
            # Auto-calculate DTI
            monthly_income = (income + coapplicant_income) / 12.0
            r = 0.06 / 12.0
            monthly_payment = loan_amount * (r * (1 + r)**loan_term) / ((1 + r)**loan_term - 1)
            dti = round(monthly_payment / monthly_income, 3)
            
            payload = {
                "applicant_id": applicant_id, "gender": gender, "age": age, "race": race,
                "income": float(income), "coapplicant_income": float(coapplicant_income),
                "credit_score": int(credit_score), "loan_amount": float(loan_amount),
                "loan_term": int(loan_term), "employment_years": float(employment_years),
                "home_ownership": home_ownership, "education": education,
                "self_employed": self_employed, "dependents": dependents,
                "property_area": property_area, "dti": float(dti)
            }
            
            # Predict
            with st.spinner("Processing prediction & explanations..."):
                if is_alive:
                    pred_res = make_request("POST", "/predict", json_data=payload)
                else:
                    pred_res = run_prediction_locally(payload)
                    
                if "error" in pred_res:
                    st.error(pred_res["error"])
                else:
                    pred_id = pred_res["prediction_id"]
                    status_lbl = "APPROVED" if pred_res["predicted_status"] == 1 else "DENIED"
                    status_color = "#16A34A" if pred_res["predicted_status"] == 1 else "#DC2626"
                    
                    st.markdown(f"""
                        <div style='background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; margin-bottom: 25px;'>
                            <h3 style='margin: 0px;'>Evaluation Result</h3>
                            <h2 style='color: {status_color}; margin: 5px 0px;'>{status_lbl}</h2>
                            <p style='margin: 0px; color: #64748B;'>Probability of Approval: <b>{pred_res['probability']:.2%}</b> (Model Version: {pred_res['model_version']})</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Explanations
                    if is_alive:
                        exp_res = make_request("GET", f"/explain/{pred_id}")
                    else:
                        exp_res = run_explanation_locally(pred_id)
                        
                    if "error" in exp_res:
                        st.error(f"Explanations generation failed: {exp_res['error']}")
                    else:
                        st.markdown("### Decision Explanations")
                        exp_col1, exp_col2 = st.columns(2)
                        
                        with exp_col1:
                            st.markdown("#### Local Explanations (LIME)")
                            # Render list of contributions
                            contribs = exp_res.get("lime_contributions", [])
                            if contribs:
                                df_contribs = pd.DataFrame(contribs)
                                
                                # Highlight color based on direction
                                def color_direction(val):
                                    color = 'green' if 'Positive' in val else 'red'
                                    return f'color: {color}; font-weight: 500;'
                                    
                                st.dataframe(
                                    df_contribs.style.map(color_direction, subset=['direction']),
                                    hide_index=True,
                                    use_container_width=True
                                )
                                
                                # Render LIME HTML link if exists
                                html_path = exp_res.get("lime_html_path")
                                if html_path and os.path.exists(html_path):
                                    with open(html_path, "r") as f:
                                        html_content = f.read()
                                    st.components.v1.html(html_content, height=400, scrolling=True)
                            else:
                                st.info("LIME contributions not computed.")
                                
                        with exp_col2:
                            st.markdown("#### Feature Attributions (SHAP)")
                            # Load waterfall image
                            img_path = exp_res.get("shap_waterfall_path")
                            if img_path and os.path.exists(img_path):
                                st.image(img_path, caption=f"SHAP Waterfall Plot for Prediction ID: {pred_id}", use_container_width=True)
                            else:
                                st.info("SHAP waterfall plot not found.")

# ================= TAB 3: ANALYTICS & HISTORY =================
with tabs[2]:
    st.markdown("### System History & Performance Analytics")
    
    if is_alive:
        analytics = make_request("GET", "/analytics")
        history_list = make_request("GET", "/history?limit=100")
    else:
        analytics = get_analytics_locally()
        history_list = get_history_locally()
        
    if "error" in analytics:
        st.error(analytics["error"])
    else:
        # Render KPIs
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_kpi_card("Total Applications", f"{analytics['total_applications']}", "Audited database size")
        with col2:
            render_kpi_card("Overall Approval Rate", f"{analytics['approval_rate']:.2%}", "Favorable output ratio")
        with col3:
            render_kpi_card("Avg FICO Score", f"{analytics['average_credit_score']:.1f}", "Average applicant score")
        with col4:
            render_kpi_card("Avg DTI Ratio", f"{analytics['average_dti']:.2f}", "Average debt ratio")
            
        st.markdown("---")
        
        # History Table
        st.markdown("#### Historical Application Decisions")
        if history_list:
            df_hist = pd.DataFrame(history_list)
            
            # Map predictions to badges
            df_hist["status_badge"] = df_hist["predicted_status"].apply(lambda x: "APPROVED" if x == 1 else "DENIED")
            
            # Column selection
            show_cols = [
                "prediction_id", "applicant_id", "gender", "age", "race", 
                "income", "credit_score", "loan_amount", "dti", 
                "status_badge", "probability", "model_version"
            ]
            st.dataframe(df_hist[show_cols], hide_index=True, use_container_width=True)
            
            # Interactive lookup details for a historical prediction
            st.markdown("#### Detail Explainability Lookup")
            lookup_id = st.selectbox("Select Prediction ID to load details & plots", df_hist["prediction_id"].unique())
            
            if st.button("Load Historical Explanation"):
                with st.spinner("Retrieving historical plot..."):
                    if is_alive:
                        hist_exp = make_request("GET", f"/explain/{lookup_id}")
                    else:
                        hist_exp = run_explanation_locally(lookup_id)
                        
                    if "error" in hist_exp:
                        st.error(hist_exp["error"])
                    else:
                        col_e1, col_e2 = st.columns(2)
                        with col_e1:
                            st.markdown("##### Tabular Feature Contributions")
                            st.dataframe(pd.DataFrame(hist_exp.get("lime_contributions", [])), hide_index=True, use_container_width=True)
                            
                        with col_e2:
                            st.markdown("##### SHAP Waterfall attribution")
                            path = hist_exp.get("shap_waterfall_path")
                            if path and os.path.exists(path):
                                st.image(path, use_container_width=True)
                            else:
                                st.info("Plot file not found on disk.")
        else:
            st.info("No applications present in the database log yet.")

# ================= TAB 4: FAIRNESS AUDIT =================
with tabs[3]:
    st.markdown("### Bias & Fairness Auditing Report")
    st.write(
        "Standard fairness requirements assess Demographic Parity and Equal Opportunity Parity. "
        "The panels below measure demographic disparities across Gender, Age, and Race attribute subsets."
    )
    
    if is_alive:
        analytics = make_request("GET", "/analytics")
    else:
        analytics = get_analytics_locally()
        
    if "error" in analytics:
        st.error(analytics["error"])
    elif not analytics.get("fairness_audit"):
        st.info("Insufficient historical applications to run demographic bias audit. Run prediction forms first.")
    else:
        fairness_data = analytics["fairness_audit"]
        
        # Selection attribute dropdown
        sel_attr = st.selectbox("Audit Attribute Segment", list(fairness_data.keys()))
        
        attr_data = fairness_data[sel_attr]
        
        # Metric stats
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            render_kpi_card(
                "Demographic Parity Ratio", 
                f"{attr_data['demographic_parity_ratio']:.2f}",
                "Favorable approval ratio (Fair threshold >= 0.80)"
            )
        with col_f2:
            render_kpi_card(
                "Demographic Parity Diff", 
                f"{attr_data['demographic_parity_difference']:.2%}",
                "Max selection difference (Fair threshold <= 10.0%)"
            )
        with col_f3:
            render_kpi_card(
                "Equal Opportunity Diff", 
                f"{attr_data['equal_opportunity_difference']:.2%}",
                "Max TPR difference (Fair threshold <= 10.0%)"
            )
            
        st.markdown("---")
        
        # Disparity Bar Chart
        groups = list(attr_data["group_metrics"].keys())
        selection_rates = [attr_data["group_metrics"][g]["selection_rate"] for g in groups]
        tprs = [attr_data["group_metrics"][g]["true_positive_rate"] for g in groups]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=groups, y=selection_rates, name='Selection (Approval) Rate', marker_color='#3B82F6'))
        fig.add_trace(go.Bar(x=groups, y=tprs, name='True Positive (Recall) Rate', marker_color='#10B981'))
        
        fig.update_layout(
            title=f"Fairness Comparison: {sel_attr.capitalize()} Groups",
            xaxis_title="Demographic Group",
            yaxis_title="Rate Percentage",
            barmode='group',
            yaxis=dict(tickformat=".0%", range=[0, 1]),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        st.markdown("#### Automated Auditor Findings & Compliance Advice")
        for rec in attr_data["recommendations"]:
            if "Significant bias" in rec or "shows unequal" in rec:
                st.warning(rec)
            else:
                st.success(rec)

# ================= TAB 5: SYSTEM LOGS =================
with tabs[4]:
    st.markdown("### System Audit Logs")
    st.write("Chronological transaction history of the Loan Approval system for compliance review.")
    
    if is_alive:
        # Fetch audit logs
        # Since we might not have a direct endpoint exported on /audit/logs in router schema, 
        # let's look up history or read database session if locally accessible.
        from database.connection import SessionLocal
        from database.repository import DatabaseRepository
        db = SessionLocal()
        try:
            logs = DatabaseRepository.get_audit_logs(db, limit=100)
            log_records = []
            for l in logs:
                usr = DatabaseRepository.get_user_by_id(db, l.user_id) if l.user_id else None
                log_records.append({
                    "Timestamp": l.timestamp,
                    "Operator": usr.username if usr else "System",
                    "Action Type": l.action,
                    "Operational Details": l.details
                })
            if log_records:
                st.dataframe(pd.DataFrame(log_records), use_container_width=True)
            else:
                st.info("No audit transactions logged yet.")
        finally:
            db.close()
    else:
        # Local standalone mode audit logs reading
        from database.connection import SessionLocal
        from database.repository import DatabaseRepository
        db = SessionLocal()
        try:
            logs = DatabaseRepository.get_audit_logs(db, limit=100)
            log_records = []
            for l in logs:
                log_records.append({
                    "Timestamp": l.timestamp,
                    "Operator": "Administrator",
                    "Action Type": l.action,
                    "Operational Details": l.details
                })
            if log_records:
                st.dataframe(pd.DataFrame(log_records), use_container_width=True)
            else:
                st.info("No transactions logged in SQLite.")
        finally:
            db.close()
