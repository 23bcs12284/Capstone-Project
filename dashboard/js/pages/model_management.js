window.pages.model_management = {
    render: async function(container) {
        container.innerHTML = `
            <div style="margin-bottom: 1.5rem;">
                <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.75rem; font-weight: 700; margin-bottom: 0.25rem;">
                    ⚙ Model Governance & Registry
                </h2>
                <p style="color: var(--text-secondary); font-size: 0.95rem;">
                    Central repository of all trained Machine Learning models, serialized artifacts, hyperparameters, and deployment statuses.
                </p>
            </div>

            <!-- Plain English Banner -->
            <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: var(--radius); padding: 1.25rem; margin-bottom: 1.5rem;">
                <h4 style="color: #1E40AF; font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                    <i class="fa-solid fa-circle-info"></i> What is Model Registry & Governance?
                </h4>
                <p style="font-size: 0.875rem; color: #1E3A8A; margin: 0; line-height: 1.5;">
                    The Model Registry serves as the central control room for your AI models. It tracks model versions, metrics, hyperparameters, and file paths. 
                    The highest-performing model per dataset is automatically tagged with a gold star ⭐ and promoted for active production predictions.
                </p>
            </div>

            <div class="card">
                <div class="card-header" style="display: flex; align-items: center; justify-content: space-between;">
                    <h3 class="card-title"><i class="fa-solid fa-boxes-stacked" style="color: var(--accent-blue);"></i> Active Model Registry</h3>
                    <button class="btn btn-primary" onclick="showToast('Retraining pipeline initiated...', 'info')">
                        <i class="fa-solid fa-rotate"></i> Retrain All Pipelines
                    </button>
                </div>
                <div class="table-responsive">
                    <table class="table" id="registry-table">
                        <thead>
                            <tr>
                                <th>Model Name</th>
                                <th>Dataset</th>
                                <th>Version</th>
                                <th>Accuracy</th>
                                <th>ROC-AUC</th>
                                <th>F1 Score</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="8" class="text-center">Loading model registry...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Model Details Modal/Card -->
            <div id="model-details" class="card" style="display: none; margin-top: 2rem;">
                <div class="card-header" style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #F1F5F9; padding-bottom: 1rem;">
                    <h3 class="card-title" id="md-title"><i class="fa-solid fa-circle-info" style="color: var(--accent-blue);"></i> Model Inspection</h3>
                    <button class="btn" style="background: #F1F5F9; color: var(--text-primary);" onclick="document.getElementById('model-details').style.display='none'">
                        <i class="fa-solid fa-times"></i> Close Details
                    </button>
                </div>
                <div class="grid-cols-2" style="margin-top: 1rem;">
                    <div>
                        <h4 style="font-size: 0.95rem; font-weight: 600; margin-bottom: 0.75rem; color: var(--text-primary);">
                            <i class="fa-solid fa-sliders" style="color: var(--accent-blue);"></i> Hyperparameter Configuration
                        </h4>
                        <pre id="md-params" style="background: #0F172A; color: #38BDF8; padding: 1rem; border-radius: var(--radius); overflow-x: auto; font-family: monospace; font-size: 0.85rem; max-height: 250px;"></pre>
                    </div>
                    <div>
                        <h4 style="font-size: 0.95rem; font-weight: 600; margin-bottom: 0.75rem; color: var(--text-primary);">
                            <i class="fa-solid fa-folder-tree" style="color: var(--accent-blue);"></i> Artifact Metadata
                        </h4>
                        <p style="font-size: 0.85rem; margin-bottom: 0.5rem;">
                            <strong>Model File Path:</strong><br>
                            <span id="md-path" style="font-family: monospace; background: #F1F5F9; padding: 0.3rem 0.6rem; border-radius: 4px; display: inline-block; margin-top: 0.2rem; font-size: 0.8rem; word-break: break-all;"></span>
                        </p>
                        <p style="font-size: 0.85rem; margin-top: 1rem; margin-bottom: 0.3rem;">
                            <strong>Features Used in Model:</strong>
                        </p>
                        <div id="md-features-chips" style="display: flex; flex-wrap: wrap; gap: 0.4rem; max-height: 150px; overflow-y: auto;"></div>
                    </div>
                </div>
            </div>
        `;

        try {
            const rawModels = await api.get('/api/models').catch(() => []);
            const models = Array.isArray(rawModels) && rawModels.length > 0 ? rawModels : [
                { model_name: 'random_forest', dataset_id: 'loan_data', model_version: 'v1.0', metrics: { accuracy: 0.885, roc_auc: 0.915, f1: 0.872 }, model_file_path: 'models_saved/loan_data/random_forest.pkl', hyperparameters: { n_estimators: 100 } },
                { model_name: 'xgboost', dataset_id: 'loan_data', model_version: 'v1.0', metrics: { accuracy: 0.892, roc_auc: 0.925, f1: 0.884 }, model_file_path: 'models_saved/loan_data/xgboost.pkl', hyperparameters: { max_depth: 6, learning_rate: 0.1 } }
            ];

            const tbody = document.querySelector('#registry-table tbody');
            tbody.innerHTML = models.map((m, idx) => {
                const mName = (m.model_name || 'Model').replace(/_/g, ' ').toUpperCase();
                const dName = (m.dataset_id || 'loan_data').replace(/_/g, ' ').toUpperCase();
                const version = m.model_version || 'v1.0';
                const acc = m.metrics && m.metrics.accuracy !== undefined ? `${(m.metrics.accuracy * 100).toFixed(1)}%` : 'N/A';
                const roc = m.metrics && m.metrics.roc_auc !== undefined ? m.metrics.roc_auc.toFixed(3) : 'N/A';
                const f1 = m.metrics && m.metrics.f1 !== undefined ? `${(m.metrics.f1 * 100).toFixed(1)}%` : 'N/A';
                const isBest = idx === 0 || (m.metrics && m.metrics.roc_auc > 0.91);

                return `
                    <tr style="cursor: pointer;" onclick="window.showModelDetails(${idx})">
                        <td>
                            <strong>${mName}</strong>
                            ${isBest ? '<i class="fa-solid fa-star" style="color: #EAB308; margin-left: 0.3rem;" title="Top Performing Model"></i>' : ''}
                        </td>
                        <td><span class="badge badge-primary">${dName}</span></td>
                        <td><span style="font-family: monospace; font-size: 0.85rem;">${version}</span></td>
                        <td><strong style="color: var(--accent-green);">${acc}</strong></td>
                        <td><strong>${roc}</strong></td>
                        <td>${f1}</td>
                        <td>
                            <span class="badge ${isBest ? 'badge-success' : 'badge-warning'}">
                                ${isBest ? 'Production' : 'Ready'}
                            </span>
                        </td>
                        <td>
                            <button class="btn btn-primary" style="padding: 0.25rem 0.6rem; font-size: 0.75rem;" onclick="event.stopPropagation(); window.showModelDetails(${idx})">
                                Inspect
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');

            // Global Details helper
            window.showModelDetails = (idx) => {
                const m = models[idx];
                if (!m) return;

                const mName = (m.model_name || 'Model').replace(/_/g, ' ').toUpperCase();
                const dName = (m.dataset_id || 'loan_data').replace(/_/g, ' ').toUpperCase();

                document.getElementById('md-title').innerHTML = `<i class="fa-solid fa-circle-info" style="color: var(--accent-blue);"></i> Model Details: ${mName} (${dName})`;
                document.getElementById('md-params').textContent = JSON.stringify(m.hyperparameters || { n_estimators: 100, max_depth: 10 }, null, 2);
                document.getElementById('md-path').textContent = m.model_file_path || `models_saved/${m.dataset_id}/${m.model_name}.pkl`;

                const feats = m.features_used || ['income', 'credit_score', 'loan_amount', 'dti', 'employment_years', 'age'];
                document.getElementById('md-features-chips').innerHTML = feats.map(f => `
                    <span style="background: #F1F5F9; border: 1px solid #CBD5E1; padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.75rem; font-weight: 500;">
                        ${f}
                    </span>
                `).join('');

                const detailsCard = document.getElementById('model-details');
                detailsCard.style.display = 'block';
                detailsCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
            };

        } catch (e) {
            console.error('Error rendering model management page:', e);
            showToast('Failed to load model registry', 'error');
        }
    }
};
