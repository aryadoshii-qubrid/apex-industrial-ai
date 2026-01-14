import streamlit as st
from backend.schemas import DefectReport, InspectionStatus

def render_header():
    st.title("🛡️ DefectGuard AI")
    st.markdown("### Automated Industrial Visual Inspection")
    st.markdown("---")

def render_defect_report(report: DefectReport):
    """Renders the typed DefectReport object into a UI card."""
    
    # FIX: Compare directly against the string value or Enum value
    # Since use_enum_values=True, report.status is likely a string "FAIL"
    status_class = "status-fail" if report.status == "FAIL" else "status-pass"
    
    # FIX: Removed .value because report.status and report.severity are already strings
    html_card = f"""
    <div class="defect-card">
        <h3>Inspection Result: <span class="{status_class}">{report.status}</span></h3>
        <p><strong>Severity:</strong> {report.severity}</p>
        <p><strong>Confidence:</strong> {report.confidence_score * 100:.1f}%</p>
        <hr style="border-color: #444;">
        <p><strong>Recommendation:</strong> {report.recommendation}</p>
    </div>
    """
    st.markdown(html_card, unsafe_allow_html=True)

    # Display specific defects if any
    if report.detected_defects:
        st.error(f"Detected Defects: {', '.join(report.detected_defects)}")
    else:
        st.success("No defects detected. Component is clean.")