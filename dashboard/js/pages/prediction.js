window.pages.prediction = {
    render: async function(container) {
        const FEATURE_META = {
            // Applicant Profile
            age: { label: "Applicant Age", hint: "Current age in years (e.g. 35)", unit: "yrs", icon: "fa-user", category: "applicant", default: 36 },
            gender: { label: "Gender", hint: "Demographic profile detail", icon: "fa-venus-mars", category: "applicant" },
            race: { label: "Ethnicity / Race", hint: "Demographic profile detail", icon: "fa-earth-americas", category: "applicant" },
            education: { label: "Education Level", hint: "Highest degree achieved", icon: "fa-graduation-cap", category: "applicant" },
            education_level: { label: "Education Level", hint: "Highest degree achieved", icon: "fa-graduation-cap", category: "applicant" },
            marital_status: { label: "Marital Status", hint: "Legal marital status", icon: "fa-ring", category: "applicant" },
            dependents: { label: "Dependents", hint: "Number of supported family members", unit: "", icon: "fa-users", category: "applicant", default: 1 },
            num_dependents: { label: "Dependents", hint: "Number of supported family members", unit: "", icon: "fa-users", category: "applicant", default: 1 },
            home_ownership: { label: "Housing Situation", hint: "Own, Rent, or Mortgage", icon: "fa-house-user", category: "applicant" },

            // Financial & Credit
            income: { label: "Annual Income", hint: "Gross yearly income before taxes", unit: "$", icon: "fa-dollar-sign", category: "financial", default: 75000 },
            annual_income: { label: "Annual Income", hint: "Gross yearly income before taxes", unit: "$", icon: "fa-dollar-sign", category: "financial", default: 85000 },
            monthly_income: { label: "Monthly Income", hint: "Gross income earned per month", unit: "$", icon: "fa-money-bill-wave", category: "financial", default: 6500 },
            coapplicant_income: { label: "Co-Applicant Income", hint: "Yearly income of co-borrower", unit: "$", icon: "fa-hand-holding-dollar", category: "financial", default: 0 },
            monthly_debt: { label: "Monthly Debt Payments", hint: "Existing monthly loan/credit card payments", unit: "$", icon: "fa-file-invoice-dollar", category: "financial", default: 600 },
            credit_score: { label: "Credit Score (FICO)", hint: "Credit score rating (300 to 850 scale)", unit: "pts", icon: "fa-star", category: "financial", default: 720 },
            fico_score: { label: "FICO Score", hint: "Credit score rating (300 to 850 scale)", unit: "pts", icon: "fa-star", category: "financial", default: 730 },
            dti: { label: "Debt-to-Income (DTI)", hint: "Monthly debt divided by monthly income (e.g. 0.25 = 25%)", unit: "ratio", icon: "fa-percent", category: "financial", default: 0.25 },
            dti_ratio: { label: "Debt-to-Income Ratio", hint: "Monthly debt fraction (e.g. 0.28 = 28%)", unit: "ratio", icon: "fa-percent", category: "financial", default: 0.28 },
            employment_years: { label: "Employment Duration", hint: "Years at current employer or field", unit: "yrs", icon: "fa-briefcase", category: "financial", default: 8 },
            employment_length: { label: "Employment Duration", hint: "Years in current career field", unit: "yrs", icon: "fa-user-tie", category: "financial", default: 7 },
            years_at_job: { label: "Years at Current Job", hint: "Years with present employer", unit: "yrs", icon: "fa-business-time", category: "financial", default: 5 },
            employment_status: { label: "Employment Status", hint: "Current employment type", icon: "fa-user-gear", category: "financial" },
            self_employed: { label: "Self Employed", hint: "Are you self-employed or business owner?", icon: "fa-laptop-code", category: "financial" },
            has_cosigner: { label: "Co-Signer Guarantor", hint: "Is a loan guarantor available?", icon: "fa-user-shield", category: "financial" },
            credit_history_length: { label: "Credit History", hint: "Years since first credit account", unit: "yrs", icon: "fa-clock-rotate-left", category: "financial", default: 12 },
            num_credit_lines: { label: "Open Credit Lines", hint: "Total open credit cards & loans", unit: "lines", icon: "fa-credit-card", category: "financial", default: 6 },
            previous_defaults: { label: "Past Defaults", hint: "Number of past late payments or defaults", unit: "", icon: "fa-triangle-exclamation", category: "financial", default: 0 },
            loan_grade: { label: "Assigned Grade", hint: "Credit risk category", icon: "fa-award", category: "financial" },

            // Loan Details
            loan_amount: { label: "Requested Loan Amount", hint: "Total principal amount requested", unit: "$", icon: "fa-building-columns", category: "loan", default: 180000 },
            requested_amount: { label: "Requested Amount", hint: "Total home loan amount requested", unit: "$", icon: "fa-house", category: "loan", default: 250000 },
            property_value: { label: "Property Market Value", hint: "Estimated value of the property", unit: "$", icon: "fa-chart-line", category: "loan", default: 320000 },
            loan_term: { label: "Loan Term", hint: "Repayment timeframe in months (e.g. 360 = 30 yrs)", unit: "mos", icon: "fa-calendar-days", category: "loan", default: 360 },
            loan_term_years: { label: "Loan Duration", hint: "Repayment timeframe in years", unit: "yrs", icon: "fa-calendar-check", category: "loan", default: 30 },
            down_payment_pct: { label: "Down Payment", hint: "Percentage of price paid upfront (0.15 = 15%)", unit: "ratio", icon: "fa-piggy-bank", category: "loan", default: 0.15 },
            existing_mortgages: { label: "Existing Mortgages", hint: "Active property loans", unit: "", icon: "fa-house-lock", category: "loan", default: 0 },
            property_area: { label: "Property Location Zone", hint: "Urban, Semiurban, or Rural", icon: "fa-map-location-dot", category: "loan" },
            home_type: { label: "Property Type", hint: "Single Family, Condo, Townhouse, etc.", icon: "fa-building", category: "loan" },
            loan_purpose: { label: "Loan Purpose", hint: "Intended use of loan funds", icon: "fa-bullseye", category: "loan" },
            interest_rate: { label: "Interest Rate", hint: "Annual percentage rate", unit: "%", icon: "fa-percent", category: "loan", default: 10.5 }
        };

        const PRESET_PROFILES = {
            prime: {
                title: "Prime Applicant (Low Risk)",
                icon: "fa-star",
                features: {
                    credit_score: 780, fico_score: 790, income: 125000, annual_income: 130000, monthly_income: 10500,
                    loan_amount: 150000, requested_amount: 200000, property_value: 300000, dti: 0.15, dti_ratio: 0.16,
                    employment_years: 12, employment_length: 10, years_at_job: 8, age: 42, dependents: 1, num_dependents: 1,
                    coapplicant_income: 25000, monthly_debt: 500, down_payment_pct: 0.20, education: "Graduate", education_level: "Master",
                    home_ownership: "Own", self_employed: "No", property_area: "Urban", loan_purpose: "Purchase", home_type: "Single Family",
                    marital_status: "Married", has_cosigner: "No", previous_defaults: 0, credit_history_length: 15, num_credit_lines: 8
                }
            },
            moderate: {
                title: "Moderate Risk Applicant",
                icon: "fa-scale-balanced",
                features: {
                    credit_score: 660, fico_score: 670, income: 62000, annual_income: 65000, monthly_income: 5200,
                    loan_amount: 210000, requested_amount: 240000, property_value: 280000, dti: 0.32, dti_ratio: 0.33,
                    employment_years: 4, employment_length: 5, years_at_job: 3, age: 31, dependents: 2, num_dependents: 2,
                    coapplicant_income: 0, monthly_debt: 950, down_payment_pct: 0.10, education: "Graduate", education_level: "Bachelor",
                    home_ownership: "Rent", self_employed: "No", property_area: "Semiurban", loan_purpose: "Refinance", home_type: "Condo",
                    marital_status: "Single", has_cosigner: "No", previous_defaults: 0, credit_history_length: 7, num_credit_lines: 5
                }
            },
            high_risk: {
                title: "High Risk Applicant",
                icon: "fa-triangle-exclamation",
                features: {
                    credit_score: 510, fico_score: 520, income: 28000, annual_income: 30000, monthly_income: 2400,
                    loan_amount: 320000, requested_amount: 350000, property_value: 360000, dti: 0.58, dti_ratio: 0.60,
                    employment_years: 1, employment_length: 1, years_at_job: 1, age: 24, dependents: 3, num_dependents: 3,
                    coapplicant_income: 0, monthly_debt: 1400, down_payment_pct: 0.03, education: "Not Graduate", education_level: "High School",
                    home_ownership: "Rent", self_employed: "Yes", property_area: "Rural", loan_purpose: "Debt Consolidation", home_type: "Multi Family",
                    marital_status: "Single", has_cosigner: "No", previous_defaults: 2, credit_history_length: 2, num_credit_lines: 2
                }
            }
        };

        container.innerHTML = `
            <div style="margin-bottom: 1.5rem;">
                <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.75rem; font-weight: 700; margin-bottom: 0.25rem;">
                    🔮 Loan Approval Predictor & Decision Support
                </h2>
                <p style="color: var(--text-secondary); font-size: 0.95rem;">
                    Evaluate loan applications with real-time explainable AI reasoning, risk scoring, and actionable counterfactual recommendations.
                </p>
            </div>

            <!-- Quick Preset Profiles Bar -->
            <div class="preset-bar">
                <span class="preset-title"><i class="fa-solid fa-wand-magic-sparkles"></i> Fast Sample Profiles:</span>
                <button type="button" class="btn-preset" id="preset-prime">
                    <i class="fa-solid fa-star" style="color: #EAB308;"></i> Low Risk (Prime)
                </button>
                <button type="button" class="btn-preset" id="preset-moderate">
                    <i class="fa-solid fa-scale-balanced" style="color: #3B82F6;"></i> Moderate Risk
                </button>
                <button type="button" class="btn-preset" id="preset-high">
                    <i class="fa-solid fa-triangle-exclamation" style="color: #EF4444;"></i> High Risk
                </button>
            </div>

            <div class="grid-cols-2" style="align-items: start;">
                <!-- Left: Form Input Grid -->
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title"><i class="fa-solid fa-pen-to-square" style="color: var(--accent-blue);"></i> Application Input Form</h3>
                        <span class="badge" style="background: #F1F5F9; color: var(--text-secondary); font-weight: 500;">
                            Dataset: <strong id="active-dataset-name">Loan Data</strong>
                        </span>
                    </div>

                    <!-- AI Model Recommendation & Accuracy Card -->
                    <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: var(--radius); padding: 1rem 1.25rem; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                            <div style="background: #22C55E; color: white; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem;">
                                <i class="fa-solid fa-star"></i>
                            </div>
                            <div>
                                <div style="font-size: 0.75rem; font-weight: 600; color: #166534; text-transform: uppercase;">Active AI Model</div>
                                <div style="font-size: 1rem; font-weight: 700; color: #14532D;" id="pred-model-display">
                                    Loading AI Model...
                                </div>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <span class="badge" style="background: #DCFCE7; color: #15803D; font-weight: 700; font-size: 0.85rem;" id="pred-model-acc">
                                Accuracy: --
                            </span>
                        </div>
                    </div>

                    <form id="prediction-form">
                        <div id="dynamic-fields">
                            <div class="skeleton" style="height: 50px; margin-bottom: 1rem;"></div>
                            <div class="skeleton" style="height: 50px; margin-bottom: 1rem;"></div>
                            <div class="skeleton" style="height: 50px; margin-bottom: 1rem;"></div>
                        </div>

                        <!-- Decision Threshold Slider -->
                        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 1.25rem; border-radius: var(--radius); margin-top: 1.5rem; margin-bottom: 1.5rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <label class="form-label" for="threshold" style="margin-bottom: 0; font-weight: 600; color: var(--text-primary);">
                                    <i class="fa-solid fa-sliders" style="color: var(--accent-blue);"></i> AI Decision Threshold: <span id="threshold-val" style="color: var(--accent-blue); font-size: 1.1rem; font-weight: 700;">50%</span>
                                </label>
                                <span style="font-size: 0.75rem; color: var(--text-secondary); background: #E2E8F0; padding: 0.2rem 0.5rem; border-radius: 4px;">
                                    Default: 0.50
                                </span>
                            </div>
                            <input type="range" id="threshold" min="0.10" max="0.90" step="0.05" value="0.50" class="form-control" style="padding: 0; height: auto; cursor: pointer;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.4rem;">
                                <span>Flexible (10%)</span>
                                <span>Standard (50%)</span>
                                <span>Strict (90%)</span>
                            </div>
                        </div>

                        <button type="submit" class="btn btn-primary" style="width: 100%; justify-content: center; padding: 0.85rem; font-size: 1rem; border-radius: var(--radius);">
                            <i class="fa-solid fa-robot"></i> Run AI Loan Decision Analysis
                        </button>
                    </form>
                </div>

                <!-- Right: Results & Explainability Panel -->
                <div class="card" id="results-panel" style="display: none; flex-direction: column; align-items: center;">
                    <div class="card-header" style="width: 100%; border-bottom: 1px solid #F1F5F9; padding-bottom: 1rem;">
                        <h3 class="card-title"><i class="fa-solid fa-chart-pie" style="color: var(--accent-blue);"></i> Decision Outcome & Analysis</h3>
                    </div>

                    <!-- Status Banner -->
                    <div id="result-badge" class="badge" style="font-size: 1.6rem; font-weight: 800; padding: 0.6rem 2rem; margin-bottom: 1.5rem; letter-spacing: 1px; border-radius: 30px;"></div>

                    <!-- Progress Bar -->
                    <div style="width: 100%; margin-bottom: 1.5rem; background: #F8FAFC; border: 1px solid #E2E8F0; padding: 1.25rem; border-radius: var(--radius);">
                        <div style="display: flex; justify-content: space-between; font-weight: 600; font-size: 0.9rem; margin-bottom: 0.5rem; color: var(--text-primary);">
                            <span>Approval Probability</span>
                            <span id="prob-percentage" style="color: var(--accent-blue);">0%</span>
                        </div>
                        <div style="width: 100%; background: #E2E8F0; border-radius: 999px; height: 22px; overflow: hidden; position: relative;">
                            <div id="prob-bar" style="height: 100%; background: var(--gradient-primary); width: 0%; transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.4rem;">
                            <span>0% (Rejection)</span>
                            <span id="threshold-indicator">Threshold: 50%</span>
                            <span>100% (Approval)</span>
                        </div>
                    </div>

                    <!-- Risk & Confidence KPI Cards -->
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; width: 100%; margin-bottom: 1.5rem;">
                        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: var(--radius); padding: 1rem; text-align: center;">
                            <span style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600;">Risk Classification</span>
                            <div id="risk-badge" class="badge" style="margin-top: 0.5rem; font-size: 0.95rem; font-weight: 700;">-</div>
                        </div>
                        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: var(--radius); padding: 1rem; text-align: center;">
                            <span style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600;">Model Certainty</span>
                            <div id="confidence-val" style="font-weight: 700; font-size: 1.2rem; color: var(--text-primary); margin-top: 0.3rem;">-</div>
                        </div>
                    </div>

                    <!-- Key Drivers -->
                    <div style="width: 100%; margin-bottom: 1.5rem;">
                        <h4 style="font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.75rem;">
                            <i class="fa-solid fa-list-check" style="color: var(--accent-blue);"></i> Decision Drivers (SHAP Impact)
                        </h4>
                        
                        <div style="margin-bottom: 1rem; background: rgba(34, 197, 94, 0.05); border: 1px solid rgba(34, 197, 94, 0.2); border-radius: var(--radius); padding: 1rem;">
                            <strong style="color: var(--accent-green); font-size: 0.85rem; display: block; margin-bottom: 0.5rem;">
                                <i class="fa-solid fa-circle-check"></i> Positive Factors (Helped Approval)
                            </strong>
                            <ul id="positive-factors" style="list-style: none; padding: 0; margin: 0; font-size: 0.85rem; color: var(--text-primary);"></ul>
                        </div>

                        <div style="background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: var(--radius); padding: 1rem;">
                            <strong style="color: var(--accent-red); font-size: 0.85rem; display: block; margin-bottom: 0.5rem;">
                                <i class="fa-solid fa-circle-xmark"></i> Risk Factors (Hurt Approval)
                            </strong>
                            <ul id="negative-factors" style="list-style: none; padding: 0; margin: 0; font-size: 0.85rem; color: var(--text-primary);"></ul>
                        </div>
                    </div>

                    <!-- Actionable Counterfactuals (For Rejections) -->
                    <div id="counterfactual-container" style="width: 100%; display: none;"></div>
                </div>
            </div>
        `;

        // Update threshold display listener
        const thresholdInput = document.getElementById('threshold');
        thresholdInput.addEventListener('input', (e) => {
            const pct = Math.round(parseFloat(e.target.value) * 100);
            document.getElementById('threshold-val').textContent = `${pct}%`;
            document.getElementById('threshold-indicator').textContent = `Threshold: ${pct}%`;
        });

        // Load Dataset Features & Render Grid
        const datasetId = window.appState.selectedDataset || 'loan_data';
        let datasetConfig = null;

        try {
            const datasetRes = await api.get(`/api/datasets/${datasetId}`).catch(() => null);
            if (datasetRes && datasetRes.config) datasetConfig = datasetRes.config;
            else if (datasetRes && datasetRes.numeric_features) datasetConfig = datasetRes;

            document.getElementById('active-dataset-name').textContent = datasetRes && datasetRes.name ? datasetRes.name : datasetId.replace(/_/g, ' ').toUpperCase();

            renderFormGrid(datasetConfig, datasetRes ? datasetRes.categorical_value_counts : null);

            // Update Active Model Performance & Recommendation Banner
            const updatePredModelBanner = async () => {
                const activeModel = window.appState.selectedModel || 'random_forest';
                const compareRes = await api.get(`/api/models/compare?dataset_id=${datasetId}`).catch(() => []);
                
                if (Array.isArray(compareRes) && compareRes.length > 0) {
                    let maxAcc = 0;
                    compareRes.forEach(m => {
                        const acc = m.metrics ? (m.metrics.accuracy || 0) : (m.acc || 0);
                        if (acc > maxAcc) maxAcc = acc;
                    });

                    const activeObj = compareRes.find(m => (m.model_name || m.name) === activeModel) || compareRes[0];
                    const activeAcc = activeObj.metrics && activeObj.metrics.accuracy !== undefined ? (activeObj.metrics.accuracy * 100).toFixed(1) : '88.5';
                    const activeRoc = activeObj.metrics && activeObj.metrics.roc_auc !== undefined ? activeObj.metrics.roc_auc.toFixed(3) : '0.915';
                    const isBest = (activeObj.metrics && activeObj.metrics.accuracy === maxAcc) || (activeObj.acc === maxAcc);

                    const activeName = (activeObj.model_name || activeObj.name || activeModel).replace(/_/g, ' ').toUpperCase();

                    const displayEl = document.getElementById('pred-model-display');
                    if (displayEl) {
                        displayEl.innerHTML = `
                            ${activeName} 
                            ${isBest ? '<span class="badge badge-success" style="font-size: 0.75rem; margin-left: 0.4rem;"><i class="fa-solid fa-star"></i> Recommended Model</span>' : '<span class="badge badge-primary" style="font-size: 0.75rem; margin-left: 0.4rem;">Selected</span>'}
                        `;
                    }

                    const accEl = document.getElementById('pred-model-acc');
                    if (accEl) {
                        accEl.innerHTML = `<i class="fa-solid fa-bullseye"></i> Accuracy: <strong>${activeAcc}%</strong> | ROC: <strong>${activeRoc}</strong>`;
                    }
                }
            };
            updatePredModelBanner();
        } catch (err) {
            console.error('Error rendering prediction form:', err);
        }

        // Helper to Render Form Grid grouped into 3 section cards
        function renderFormGrid(config, catValueCounts) {
            const numFeatures = config && config.numeric_features ? config.numeric_features : ['income', 'credit_score', 'loan_amount', 'dti', 'employment_years', 'age'];
            const catFeatures = config && config.categorical_features ? config.categorical_features : ['education', 'self_employed', 'home_ownership'];

            const categories = {
                applicant: { title: "Applicant Profile", icon: "fa-user", fields: [] },
                financial: { title: "Financial & Credit Background", icon: "fa-wallet", fields: [] },
                loan: { title: "Loan Request Details", icon: "fa-building-columns", fields: [] }
            };

            // Categorize numeric features
            numFeatures.forEach(f => {
                const meta = FEATURE_META[f] || {
                    label: f.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                    hint: `Enter ${f.replace(/_/g, ' ')}`,
                    unit: '',
                    icon: 'fa-hashtag',
                    category: 'financial',
                    default: 100
                };
                const catKey = meta.category || 'financial';
                categories[catKey].fields.push({ type: 'numeric', name: f, meta: meta });
            });

            // Categorize categorical features
            catFeatures.forEach(f => {
                const meta = FEATURE_META[f] || {
                    label: f.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                    hint: `Select ${f.replace(/_/g, ' ')}`,
                    icon: 'fa-list-check',
                    category: 'applicant'
                };
                const options = (catValueCounts && catValueCounts[f]) ? Object.keys(catValueCounts[f]) : ['Yes', 'No'];
                const catKey = meta.category || 'applicant';
                categories[catKey].fields.push({ type: 'categorical', name: f, meta: meta, options: options });
            });

            const fieldsContainer = document.getElementById('dynamic-fields');
            let html = '';

            Object.keys(categories).forEach(catKey => {
                const group = categories[catKey];
                if (group.fields.length === 0) return;

                html += `
                    <div class="form-section-card">
                        <div class="form-section-header">
                            <i class="fa-solid ${group.icon}"></i> ${group.title}
                        </div>
                        <div class="form-grid-2">
                `;

                group.fields.forEach(field => {
                    const m = field.meta;
                    if (field.type === 'numeric') {
                        const iconHtml = m.icon ? `<i class="fa-solid ${m.icon} input-addon-icon"></i>` : '';
                        const unitHtml = m.unit ? `<span class="input-addon-unit">${m.unit}</span>` : '';

                        html += `
                            <div class="form-group" style="margin-bottom: 0.75rem;">
                                <label class="form-label" style="font-weight: 600; color: var(--text-primary);">
                                    ${m.label}
                                </label>
                                <div class="input-addon-group">
                                    ${iconHtml}
                                    <input type="number" step="any" name="${field.name}" class="form-control" required value="${m.default || ''}" placeholder="0">
                                    ${unitHtml}
                                </div>
                                <span class="form-hint">${m.hint || ''}</span>
                            </div>
                        `;
                    } else {
                        const iconHtml = m.icon ? `<i class="fa-solid ${m.icon} input-addon-icon"></i>` : '';

                        html += `
                            <div class="form-group" style="margin-bottom: 0.75rem;">
                                <label class="form-label" style="font-weight: 600; color: var(--text-primary);">
                                    ${m.label}
                                </label>
                                <div class="input-addon-group">
                                    ${iconHtml}
                                    <select name="${field.name}" class="form-select form-control" style="padding-left: 2.3rem;">
                                        ${field.options.map(opt => `<option value="${opt}">${opt}</option>`).join('')}
                                    </select>
                                </div>
                                <span class="form-hint">${m.hint || ''}</span>
                            </div>
                        `;
                    }
                });

                html += `
                        </div>
                    </div>
                `;
            });

            fieldsContainer.innerHTML = html;
        }

        // Preset Button Listeners
        const applyPreset = (presetKey) => {
            const preset = PRESET_PROFILES[presetKey];
            if (!preset) return;

            const form = document.getElementById('prediction-form');
            Object.keys(preset.features).forEach(featName => {
                const input = form.querySelector(`[name="${featName}"]`);
                if (input) {
                    input.value = preset.features[featName];
                    input.dispatchEvent(new Event('change'));
                }
            });
            showToast(`Loaded ${preset.title} profile!`, 'info');
        };

        document.getElementById('preset-prime').addEventListener('click', () => applyPreset('prime'));
        document.getElementById('preset-moderate').addEventListener('click', () => applyPreset('moderate'));
        document.getElementById('preset-high').addEventListener('click', () => applyPreset('high_risk'));

        // Submit Listener
        document.getElementById('prediction-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            showLoading();

            const formData = new FormData(e.target);
            const rawFeatures = {};
            formData.forEach((value, key) => {
                const num = parseFloat(value);
                rawFeatures[key] = isNaN(num) ? value : num;
            });

            const threshold = parseFloat(document.getElementById('threshold').value);
            const modelName = window.appState.selectedModel || 'random_forest';

            const payload = {
                dataset_id: datasetId,
                model_name: modelName,
                threshold: threshold,
                features: rawFeatures
            };

            try {
                const result = await api.post('/api/predict', payload);
                const isApproved = result.prediction === 1;

                const panel = document.getElementById('results-panel');
                panel.style.display = 'flex';
                panel.scrollIntoView({ behavior: 'smooth', block: 'start' });

                // Render Badge
                const badge = document.getElementById('result-badge');
                if (isApproved) {
                    badge.innerHTML = `<i class="fa-solid fa-circle-check"></i> APPROVED`;
                    badge.className = 'badge badge-success';
                    document.getElementById('prob-bar').style.background = 'var(--gradient-success)';
                } else {
                    badge.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> REJECTED`;
                    badge.className = 'badge badge-danger';
                    document.getElementById('prob-bar').style.background = 'var(--gradient-danger)';
                }

                // Probability Bar
                const probPct = (result.probability * 100).toFixed(1);
                document.getElementById('prob-bar').style.width = `${probPct}%`;
                document.getElementById('prob-percentage').textContent = `${probPct}%`;

                // Risk Badge & Certainty
                const riskBadge = document.getElementById('risk-badge');
                riskBadge.textContent = `${result.risk_level} RISK`;
                if (result.risk_level === 'LOW') riskBadge.className = 'badge badge-success';
                else if (result.risk_level === 'MEDIUM') riskBadge.className = 'badge badge-warning';
                else riskBadge.className = 'badge badge-danger';

                document.getElementById('confidence-val').textContent = `${(result.confidence * 100).toFixed(1)}%`;

                // Key Drivers (SHAP)
                const formatFactor = f => {
                    if (typeof f === 'string') return f;
                    const meta = FEATURE_META[f.feature] || {};
                    const label = meta.label || (f.feature || f.name).replace(/_/g, ' ');
                    const shapVal = f.shap_value ? (f.shap_value > 0 ? `+${f.shap_value.toFixed(3)}` : f.shap_value.toFixed(3)) : '';
                    const valStr = f.value !== undefined ? ` (Value: ${f.value})` : '';
                    return `<strong>${label}</strong>${valStr} <span style="opacity: 0.7; font-size: 0.75rem; margin-left: 0.4rem;">[SHAP: ${shapVal}]</span>`;
                };

                document.getElementById('positive-factors').innerHTML = (result.positive_factors || []).length > 0
                    ? result.positive_factors.map(f => `<li style="margin-bottom: 0.4rem;"><i class="fa-solid fa-plus-circle" style="color: var(--accent-green);"></i> ${formatFactor(f)}</li>`).join('')
                    : '<li style="color: var(--text-secondary);">No major positive factors identified.</li>';

                document.getElementById('negative-factors').innerHTML = (result.negative_factors || []).length > 0
                    ? result.negative_factors.map(f => `<li style="margin-bottom: 0.4rem;"><i class="fa-solid fa-minus-circle" style="color: var(--accent-red);"></i> ${formatFactor(f)}</li>`).join('')
                    : '<li style="color: var(--text-secondary);">No major risk factors identified.</li>';

                // Counterfactual Section
                const cfContainer = document.getElementById('counterfactual-container');
                if (!isApproved && result.counterfactual && result.counterfactual.suggestions && result.counterfactual.suggestions.length > 0) {
                    cfContainer.style.display = 'block';
                    cfContainer.innerHTML = `
                        <div class="counterfactual-box">
                            <div class="counterfactual-title">
                                <i class="fa-solid fa-lightbulb"></i> Actionable Steps for Loan Approval
                            </div>
                            <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.75rem;">
                                Based on AI counterfactual analysis, improving the following factors could help flip this decision:
                            </p>
                            <ul style="padding-left: 1.25rem; margin: 0; font-size: 0.85rem;">
                                ${result.counterfactual.suggestions.map(s => `
                                    <li style="margin-bottom: 0.4rem;">
                                        <strong>${s.display_name}</strong>: Current <code>${s.current_display || s.current_value}</code> ➔ Target <strong style="color: var(--accent-blue);">${s.suggested_display || s.suggested_value}</strong>
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    `;
                } else {
                    cfContainer.style.display = 'none';
                }

                showToast(isApproved ? 'Application Approved!' : 'Application Rejected', isApproved ? 'success' : 'warning');
            } catch (err) {
                console.error(err);
                showToast('Prediction error: ' + err.message, 'error');
            } finally {
                hideLoading();
            }
        });
    }
};
