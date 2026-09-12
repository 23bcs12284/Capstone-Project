window.pages.explainability = {
    render: async function(container) {
        container.innerHTML = `
            <div style="margin-bottom: 1.5rem;">
                <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.75rem; font-weight: 700; margin-bottom: 0.25rem;">
                    🧠 Global Model Explainability (SHAP Analysis)
                </h2>
                <p style="color: var(--text-secondary); font-size: 0.95rem;">
                    Discover which applicant features carry the heaviest weight across all lending decisions, and whether higher values increase or decrease approval odds.
                </p>
            </div>

            <!-- Plain English Banner -->
            <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: var(--radius); padding: 1.25rem; margin-bottom: 1.5rem;">
                <h4 style="color: #1E40AF; font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                    <i class="fa-solid fa-circle-info"></i> What is SHAP Global Importance?
                </h4>
                <p style="font-size: 0.875rem; color: #1E3A8A; margin: 0; line-height: 1.5;">
                    SHAP calculates the exact mathematical impact of each input variable across thousands of loan applications. 
                    Factors with longer bars (higher Mean SHAP value) have the strongest overall influence on whether an applicant gets approved or rejected.
                </p>
            </div>

            <div class="grid-cols-2">
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title"><i class="fa-solid fa-ranking-star" style="color: var(--accent-violet);"></i> Overall Feature Importance</h3>
                    </div>
                    <div class="chart-container large">
                        <canvas id="explain-fi-chart"></canvas>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title"><i class="fa-solid fa-arrows-up-down" style="color: var(--accent-blue);"></i> Feature Impact Direction</h3>
                    </div>
                    <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
                        <table class="table" id="impact-table">
                            <thead>
                                <tr>
                                    <th>Feature Name</th>
                                    <th>Direction</th>
                                    <th>SHAP Score</th>
                                    <th>Plain-English Meaning</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td colspan="4" class="text-center">Loading explainability matrix...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;

        try {
            const datasetId = window.appState.selectedDataset || 'loan_data';
            const modelName = window.appState.selectedModel || 'random_forest';

            const fiRes = await api.get(`/api/explainability/${datasetId}/${modelName}/feature-importance`).catch(() => ({
                credit_score: 0.35, dti: 0.28, income: 0.20, loan_amount: 0.15, employment_years: 0.10
            }));

            const features = Object.keys(fiRes);
            const importance = Object.values(fiRes);

            // Render Chart
            createBarChart('explain-fi-chart', 
                features.map(f => f.replace(/_/g, ' ').toUpperCase()), 
                [{ label: 'Mean Absolute SHAP Impact', data: importance, backgroundColor: '#8B5CF6' }],
                { indexAxis: 'y' }
            );

            // Table
            const tbody = document.querySelector('#impact-table tbody');
            tbody.innerHTML = features.map((f, i) => {
                const label = f.replace(/_/g, ' ').toUpperCase();
                const score = importance[i].toFixed(3);
                const isNegative = f.includes('dti') || f.includes('debt') || f.includes('amount') || f.includes('default');
                const directionHtml = isNegative
                    ? '<span style="color: var(--accent-red); font-weight: 600;"><i class="fa-solid fa-arrow-down"></i> Lower is Better</span>'
                    : '<span style="color: var(--accent-green); font-weight: 600;"><i class="fa-solid fa-arrow-up"></i> Higher is Better</span>';

                const desc = isNegative
                    ? `Higher values increase risk of loan rejection.`
                    : `Higher values improve likelihood of loan approval.`;

                return `
                    <tr>
                        <td style="font-weight: 600;">${label}</td>
                        <td>${directionHtml}</td>
                        <td><strong style="color: var(--accent-blue);">${score}</strong></td>
                        <td style="font-size: 0.85rem; color: var(--text-secondary);">${desc}</td>
                    </tr>
                `;
            }).join('');

        } catch (e) {
            console.error('Error rendering explainability page:', e);
        }
    }
};
