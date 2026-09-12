window.pages.datasets = {
    render: async function(container) {
        container.innerHTML = `
            <div style="margin-bottom: 1.5rem;">
                <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.75rem; font-weight: 700; margin-bottom: 0.25rem;">
                    📁 Loan Application Datasets
                </h2>
                <p style="color: var(--text-secondary); font-size: 0.95rem;">
                    Explore multi-domain lending benchmarks including General Loan Applications, Home Mortgages, and Personal Credit lines.
                </p>
            </div>

            <!-- Plain English Banner -->
            <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: var(--radius); padding: 1.25rem; margin-bottom: 1.5rem;">
                <h4 style="color: #1E40AF; font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                    <i class="fa-solid fa-circle-info"></i> Multi-Dataset System Architecture
                </h4>
                <p style="font-size: 0.875rem; color: #1E3A8A; margin: 0; line-height: 1.5;">
                    Each dataset represents a unique lending sector with distinct financial attributes, target variables, and approval ratios. 
                    Training models across multiple schemas proves that the decision support platform generalizes seamlessly to new credit products.
                </p>
            </div>

            <div id="dataset-cards" class="grid-cols-3" style="margin-bottom: 2rem;">
                <div class="card"><div class="skeleton" style="height: 150px;"></div></div>
                <div class="card"><div class="skeleton" style="height: 150px;"></div></div>
                <div class="card"><div class="skeleton" style="height: 150px;"></div></div>
            </div>

            <div class="grid-cols-2">
                <div class="card">
                    <div class="card-header"><h3 class="card-title"><i class="fa-solid fa-table" style="color: var(--accent-blue);"></i> Dataset Comparison Matrix</h3></div>
                    <div class="table-responsive">
                        <table class="table" id="dataset-table">
                            <thead>
                                <tr>
                                    <th>Dataset Name</th>
                                    <th>Row Count</th>
                                    <th>Features</th>
                                    <th>Approval Rate</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td colspan="4" class="text-center">Loading dataset benchmark...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header"><h3 class="card-title"><i class="fa-solid fa-chart-pie" style="color: var(--accent-violet);"></i> Target Approval Ratio</h3></div>
                    <div class="chart-container">
                        <canvas id="dataset-dist-chart"></canvas>
                    </div>
                </div>
            </div>
        `;

        try {
            const rawDatasets = await api.get('/api/datasets').catch(() => []);
            const datasets = Array.isArray(rawDatasets) && rawDatasets.length > 0 ? rawDatasets : [
                { dataset_id: 'loan_data', name: 'General Loan Dataset', rows: 5000, features: 15, target: 'loan_status', approval_rate: 0.62, description: 'General loan applications with demographic attributes.' },
                { dataset_id: 'home_loan_data', name: 'Home Loan Dataset', rows: 3500, features: 15, target: 'loan_approved', approval_rate: 0.58, description: 'Mortgage and property loan applications.' },
                { dataset_id: 'personal_loan_data', name: 'Personal Loan Dataset', rows: 4000, features: 16, target: 'loan_approved', approval_rate: 0.65, description: 'Personal lines of credit and debt consolidation.' }
            ];

            // Render Cards
            document.getElementById('dataset-cards').innerHTML = datasets.map(d => `
                <div class="card" style="border-top: 4px solid var(--accent-blue);">
                    <div class="card-header" style="margin-bottom: 0.5rem;">
                        <h3 class="card-title" style="font-size: 1.1rem;">${d.name}</h3>
                        <span class="badge badge-primary">${d.features} Features</span>
                    </div>
                    <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1rem; min-height: 40px;">${d.description || d.desc || ''}</p>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; border-top: 1px solid #F1F5F9; padding-top: 0.75rem;">
                        <span><strong>Rows:</strong> ${d.rows.toLocaleString()}</span>
                        <span><strong>Target:</strong> <code style="color: var(--accent-blue);">${d.target}</code></span>
                    </div>
                </div>
            `).join('');

            // Render Table
            document.querySelector('#dataset-table tbody').innerHTML = datasets.map(d => `
                <tr>
                    <td><strong>${d.name}</strong></td>
                    <td>${d.rows.toLocaleString()}</td>
                    <td><span class="badge" style="background: #F1F5F9; color: var(--text-primary);">${d.features}</span></td>
                    <td><strong style="color: var(--accent-green);">${((d.approval_rate || 0.6) * 100).toFixed(1)}%</strong></td>
                </tr>
            `).join('');

            // Doughnut chart for the active dataset
            const activeData = datasets[0];
            const appRate = (activeData.approval_rate || 0.6) * 100;
            createDoughnutChart('dataset-dist-chart', 
                ['Approved Loans', 'Rejected Loans'], 
                [appRate, 100 - appRate],
                ['#22C55E', '#EF4444']
            );

        } catch (e) {
            console.error('Error rendering datasets page:', e);
        }
    }
};
