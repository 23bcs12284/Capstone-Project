window.pages.applicant = {
    render: async function(container) {
        container.innerHTML = `
            <div style="margin-bottom: 1.5rem;">
                <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.75rem; font-weight: 700; margin-bottom: 0.25rem;">
                    👤 Individual Applicant Deep-Dive & XAI Analysis
                </h2>
                <p style="color: var(--text-secondary); font-size: 0.95rem;">
                    Inspect specific loan applicant profiles, SHAP waterfall feature contribution charts, and actionable decision advice.
                </p>
            </div>

            <!-- Plain English Explanation Banner -->
            <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: var(--radius); padding: 1.25rem; margin-bottom: 1.5rem;">
                <h4 style="color: #1E40AF; font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                    <i class="fa-solid fa-circle-info"></i> How Individual Explainability Works
                </h4>
                <p style="font-size: 0.875rem; color: #1E3A8A; margin: 0; line-height: 1.5;">
                    Rather than treating the AI model as a black box, SHAP (SHapley Additive exPlanations) breaks down exact contributions for this individual. 
                    Green bars push the decision toward Approval, while Red bars push toward Rejection.
                </p>
            </div>

            <div class="card" style="margin-bottom: 1.5rem;">
                <div class="card-header"><h3 class="card-title"><i class="fa-solid fa-user-check" style="color: var(--accent-blue);"></i> Select Sample Applicant Profile</h3></div>
                <div class="form-group" style="margin-bottom: 0;">
                    <select class="form-select" id="applicant-select" style="font-size: 1rem; padding: 0.75rem;">
                        <option value="">Choose an applicant to analyze...</option>
                        <option value="APP-1001" selected>APP-1001 — John Doe (High Credit, Approved)</option>
                        <option value="APP-1002">APP-1002 — Jane Smith (High DTI, Rejected)</option>
                    </select>
                </div>
            </div>

            <div id="applicant-content">
                <div class="grid-cols-3" style="margin-bottom: 1.5rem;">
                    <div class="card" style="border-top: 4px solid var(--accent-blue);">
                        <div class="card-header"><h3 class="card-title" style="font-size: 1.1rem;"><i class="fa-solid fa-id-card" style="color: var(--accent-blue);"></i> Applicant Profile</h3></div>
                        <p style="margin-bottom: 0.5rem;"><strong>Full Name:</strong> <span id="app-name">John Doe</span></p>
                        <p style="margin-bottom: 0.5rem;"><strong>Age:</strong> <span id="app-age">35 yrs</span></p>
                        <p style="margin-bottom: 0.5rem;"><strong>Employment:</strong> <span id="app-emp">8 years</span></p>
                    </div>
                    <div class="card" style="border-top: 4px solid var(--accent-teal);">
                        <div class="card-header"><h3 class="card-title" style="font-size: 1.1rem;"><i class="fa-solid fa-wallet" style="color: var(--accent-teal);"></i> Financial Profile</h3></div>
                        <p style="margin-bottom: 0.5rem;"><strong>Annual Income:</strong> $<span id="app-income">85,000</span></p>
                        <p style="margin-bottom: 0.5rem;"><strong>Credit Score:</strong> <span id="app-credit" style="font-weight: 700; color: var(--accent-green);">760</span></p>
                        <p style="margin-bottom: 0.5rem;"><strong>DTI Ratio:</strong> <span id="app-dti">22.0%</span></p>
                    </div>
                    <div class="card" style="border-top: 4px solid var(--accent-violet);">
                        <div class="card-header"><h3 class="card-title" style="font-size: 1.1rem;"><i class="fa-solid fa-file-contract" style="color: var(--accent-violet);"></i> Loan Request</h3></div>
                        <p style="margin-bottom: 0.5rem;"><strong>Requested Amount:</strong> $<span id="app-amount">180,000</span></p>
                        <p style="margin-bottom: 0.5rem;"><strong>Loan Term:</strong> <span id="app-term">360 months (30 yrs)</span></p>
                        <p style="margin-bottom: 0.5rem;"><strong>AI Decision:</strong> <span id="app-status" class="badge badge-success">APPROVED</span></p>
                    </div>
                </div>

                <div class="grid-cols-2">
                    <div class="card">
                        <div class="card-header"><h3 class="card-title"><i class="fa-solid fa-chart-bar" style="color: var(--accent-blue);"></i> SHAP Feature Contribution Waterfall</h3></div>
                        <div class="chart-container">
                            <canvas id="shap-waterfall-chart"></canvas>
                        </div>
                        <p style="margin-top: 1rem; font-size: 0.8rem; color: var(--text-secondary);">
                            * Positive values (right) push toward approval; Negative values (left) push toward rejection.
                        </p>
                    </div>
                    
                    <div>
                        <div class="card" style="margin-bottom: 1.5rem;">
                            <div class="card-header"><h3 class="card-title"><i class="fa-solid fa-message" style="color: var(--accent-blue);"></i> Plain-English AI Explanation</h3></div>
                            <p id="decision-text" style="line-height: 1.6; font-size: 0.95rem;"></p>
                        </div>
                        
                        <div class="card" id="counterfactuals-card" style="display: none; background: #EFF6FF; border: 1px solid #BFDBFE;">
                            <div class="card-header"><h3 class="card-title" style="color: #1E40AF;"><i class="fa-solid fa-lightbulb"></i> Counterfactual Recommendations</h3></div>
                            <p style="margin-bottom: 0.75rem; font-size: 0.875rem; color: #1E3A8A;">To flip this decision from REJECTED to APPROVED, the applicant should target:</p>
                            <ul id="cf-list" style="padding-left: 1.5rem; color: #1E3A8A; font-size: 0.875rem;"></ul>
                        </div>
                    </div>
                </div>
            </div>
        `;

        const renderApplicantData = (applicantId) => {
            const isApproved = applicantId === 'APP-1001';
            
            document.getElementById('app-name').textContent = isApproved ? 'John Doe' : 'Jane Smith';
            document.getElementById('app-age').textContent = isApproved ? '35 yrs' : '28 yrs';
            document.getElementById('app-emp').textContent = isApproved ? '8 years' : '1 year';
            document.getElementById('app-income').textContent = isApproved ? '85,000' : '32,000';
            document.getElementById('app-credit').textContent = isApproved ? '760' : '520';
            document.getElementById('app-dti').textContent = isApproved ? '22.0%' : '54.0%';
            document.getElementById('app-amount').textContent = isApproved ? '180,000' : '280,000';
            document.getElementById('app-term').textContent = isApproved ? '360 months' : '360 months';

            const statusBadge = document.getElementById('app-status');
            if (isApproved) {
                statusBadge.textContent = 'APPROVED';
                statusBadge.className = 'badge badge-success';
                document.getElementById('decision-text').innerHTML = `
                    Applicant <strong>John Doe</strong> was <span style="color: var(--accent-green); font-weight:700;">APPROVED</span> for the requested loan of $180,000.
                    The primary drivers were an excellent credit score of 760 (+0.32 SHAP) and a low Debt-to-Income ratio of 22% (+0.21 SHAP).
                `;
                document.getElementById('counterfactuals-card').style.display = 'none';
            } else {
                statusBadge.textContent = 'REJECTED';
                statusBadge.className = 'badge badge-danger';
                document.getElementById('decision-text').innerHTML = `
                    Applicant <strong>Jane Smith</strong> was <span style="color: var(--accent-red); font-weight:700;">REJECTED</span> due to high credit risk.
                    The main negative drivers were a low credit score of 520 (-0.38 SHAP) and an excessively high DTI ratio of 54% (-0.28 SHAP).
                `;
                document.getElementById('counterfactuals-card').style.display = 'block';
                document.getElementById('cf-list').innerHTML = `
                    <li><strong>Credit Score</strong>: Increase from 520 to at least <strong>650+</strong></li>
                    <li><strong>Debt-to-Income (DTI)</strong>: Reduce monthly debts to bring DTI below <strong>35%</strong></li>
                    <li><strong>Annual Income</strong>: Increase income or add a co-borrower with <strong>$15,000+</strong> salary</li>
                `;
            }

            // Render Chart
            const features = isApproved 
                ? ['Credit Score (760)', 'Low DTI (22%)', 'Income ($85k)', 'Employment (8y)', 'High Loan Amount']
                : ['Credit Score (520)', 'High DTI (54%)', 'Low Income ($32k)', 'Short Employment', 'High Loan Request'];
            const shapValues = isApproved 
                ? [0.32, 0.21, 0.15, 0.08, -0.05]
                : [-0.38, -0.28, -0.18, -0.12, -0.09];
            const colors = shapValues.map(v => v >= 0 ? '#22C55E' : '#EF4444');

            createBarChart('shap-waterfall-chart', features, [
                { label: 'SHAP Contribution', data: shapValues, backgroundColor: colors }
            ], { indexAxis: 'y' });
        };

        renderApplicantData('APP-1001');

        document.getElementById('applicant-select').addEventListener('change', (e) => {
            if (e.target.value) renderApplicantData(e.target.value);
        });
    }
};
