import streamlit as st

def apply_custom_css():
    """
    Applies custom CSS to the Streamlit page to achieve a premium, 
    highly polished interface with clean typography, spacing, and styling.
    """
    st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap');
        
        /* Apply fonts globally */
        html, body, [class*="css"], .stMarkdown {
            font-family: 'Inter', sans-serif;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            color: #1E293B;
        }
        
        .main {
            background-color: #F8FAFC;
            padding: 1rem 2rem;
        }
        
        /* KPI Cards Container */
        .kpi-container {
            display: flex;
            gap: 1.5rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }
        
        /* Individual KPI Card */
        .kpi-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
            border: 1px solid #F1F5F9;
            flex: 1;
            min-width: 220px;
            transition: all 0.3s ease;
        }
        
        .kpi-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
            border-color: #CBD5E1;
        }
        
        .kpi-title {
            font-size: 0.875rem;
            color: #64748B;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }
        
        .kpi-value {
            font-size: 1.875rem;
            color: #0F172A;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 0.25rem;
        }
        
        .kpi-subtext {
            font-size: 0.75rem;
            color: #94A3B8;
        }
        
        /* Status Badges */
        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-align: center;
        }
        
        .badge-approved {
            background-color: #DCFCE7;
            color: #166534;
        }
        
        .badge-denied {
            background-color: #FEE2E2;
            color: #991B1B;
        }
        
        /* Custom styled alerts */
        .info-panel {
            background-color: #EFF6FF;
            border-left: 4px solid #3B82F6;
            color: #1E40AF;
            padding: 1rem;
            border-radius: 0 8px 8px 0;
            margin: 1rem 0;
        }
        
        /* Sidebar layout adjustments */
        [data-testid="stSidebar"] {
            background-color: #0F172A;
            color: #F8FAFC;
        }
        
        [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #F8FAFC !important;
        }
        
        /* Custom section layout card */
        .section-card {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
            border: 1px solid #E2E8F0;
            margin-bottom: 2rem;
        }
        
        </style>
    """, unsafe_allow_html=True)

def render_kpi_card(title: str, value: str, subtext: str = "", trend: str = ""):
    """
    Renders an HTML-styled KPI card using markdown.
    """
    trend_html = ""
    if trend:
        if trend.startswith("+") or "up" in trend.lower():
            trend_html = f"<span style='color: #16A34A; font-weight: 600;'>{trend}</span>"
        else:
            trend_html = f"<span style='color: #DC2626; font-weight: 600;'>{trend}</span>"
            
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-subtext">{subtext} {trend_html}</div>
        </div>
    """, unsafe_allow_html=True)

def render_status_badge(is_approved: bool) -> str:
    """
    Returns HTML string for status badge to be rendered inside streamlit dataframe/table.
    """
    if is_approved:
        return '<span class="badge badge-approved">Approved</span>'
    return '<span class="badge badge-denied">Denied</span>'
