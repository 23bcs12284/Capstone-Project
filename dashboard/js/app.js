// Global namespace for pages (MUST be initialized first)
window.pages = window.pages || {};

// App State Management
class AppState {
    constructor() {
        this.selectedDataset = 'loan_data';
        this.selectedModel = 'random_forest';
        this.threshold = 0.5;
        this.datasets = [];
        this.models = [];
        this.listeners = [];
        this.userSelectedModel = false;
    }
    
    set(key, value) {
        this[key] = value;
        this.notify();
    }
    
    subscribe(listener) {
        this.listeners.push(listener);
    }
    
    notify() {
        this.listeners.forEach(listener => listener(this));
    }
}

// API Client
class ApiClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }

    async request(path, options = {}) {
        try {
            const response = await fetch(`${this.baseUrl}${path}`, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            showToast(error.message, 'error');
            throw error;
        }
    }

    get(path) { return this.request(path); }
    post(path, data) { return this.request(path, { method: 'POST', body: JSON.stringify(data) }); }
}

// Router
class Router {
    constructor() {
        this.routes = {};
        window.addEventListener('hashchange', () => this.navigate());
    }

    register(hash, pageModule) {
        this.routes[hash] = pageModule;
    }

    navigate() {
        const hash = window.location.hash.slice(1) || 'dashboard';
        const page = this.routes[hash];
        
        if (page) {
            // Update breadcrumb
            const breadcrumb = document.getElementById('page-breadcrumb');
            const routeName = hash.charAt(0).toUpperCase() + hash.slice(1).replace(/_/g, ' ');
            if (breadcrumb) {
                breadcrumb.innerHTML = `<h2>${routeName}</h2>`;
            }
            
            // Clean up charts before rendering new page
            destroyAllCharts();
            
            // Render new content
            const contentArea = document.getElementById('main-content');
            if (contentArea) {
                contentArea.innerHTML = '';
                try {
                    page.render(contentArea);
                } catch (error) {
                    console.error("Error rendering page:", error);
                    contentArea.innerHTML = `<div class="card"><div class="card-body"><h3 style="color:var(--accent-red)">Error loading page</h3><p>${error.message}</p></div></div>`;
                }
            }
        }
        this.updateActiveNav(hash);
    }

    updateActiveNav(hash) {
        document.querySelectorAll('.sidebar-nav .nav-item').forEach(el => {
            el.classList.remove('active');
            if (el.getAttribute('href') === `#${hash}`) {
                el.classList.add('active');
            }
        });
    }
}

// Global Variables
window.appState = new AppState();
window.api = new ApiClient();
window.router = new Router();
window.charts = {};

// UI Helpers
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.toggle('collapsed');
}

function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.style.display = 'flex';
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.style.display = 'none';
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = 'fa-info-circle';
    if (type === 'success') icon = 'fa-check-circle';
    if (type === 'error') icon = 'fa-exclamation-circle';
    if (type === 'warning') icon = 'fa-exclamation-triangle';

    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Chart Helpers
function destroyChart(canvasId) {
    if (window.charts[canvasId]) {
        window.charts[canvasId].destroy();
        delete window.charts[canvasId];
    }
}

function destroyAllCharts() {
    Object.keys(window.charts).forEach(canvasId => {
        destroyChart(canvasId);
    });
}

function createChart(type, canvasId, config) {
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    
    const ctx = canvas.getContext('2d');
    const chart = new Chart(ctx, {
        type: type,
        ...config,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            ...config.options
        }
    });
    window.charts[canvasId] = chart;
    return chart;
}

function createBarChart(canvasId, labels, datasets, options = {}) {
    return createChart('bar', canvasId, {
        data: { labels: labels, datasets: datasets },
        options: {
            plugins: { legend: { display: datasets.length > 1 } },
            scales: { y: { beginAtZero: true } },
            ...options
        }
    });
}

function createLineChart(canvasId, labels, datasets, options = {}) {
    return createChart('line', canvasId, {
        data: { labels: labels, datasets: datasets },
        options: {
            plugins: { legend: { display: datasets.length > 1 } },
            scales: { y: { beginAtZero: true } },
            ...options
        }
    });
}

function createRadarChart(canvasId, labels, datasets, options = {}) {
    return createChart('radar', canvasId, {
        data: { labels: labels, datasets: datasets },
        options: {
            plugins: { legend: { position: 'bottom' } },
            scales: { r: { beginAtZero: true, max: 1 } },
            ...options
        }
    });
}

function createDoughnutChart(canvasId, labels, data, colors, options = {}) {
    return createChart('doughnut', canvasId, {
        data: {
            labels: labels,
            datasets: [{ data: data, backgroundColor: colors, borderWidth: 0 }]
        },
        options: {
            cutout: '75%',
            plugins: { legend: { position: 'bottom' } },
            ...options
        }
    });
}

// Helper to Update Model Selector with Accuracy Metrics & Recommendation Tags
async function updateModelSelector(datasetId) {
    const modelSelect = document.getElementById('global-model-select');
    if (!modelSelect) return;

    try {
        const compareRes = await api.get(`/api/models/compare?dataset_id=${datasetId}`).catch(() => []);
        if (Array.isArray(compareRes) && compareRes.length > 0) {
            let maxAcc = 0;
            compareRes.forEach(m => {
                const acc = m.metrics ? (m.metrics.accuracy || 0) : (m.acc || 0);
                if (acc > maxAcc) maxAcc = acc;
            });

            const optionsHtml = compareRes.map(m => {
                const id = m.model_name || m.name;
                const name = id.replace(/_/g, ' ').toUpperCase();
                const acc = m.metrics && m.metrics.accuracy !== undefined ? (m.metrics.accuracy * 100).toFixed(1) : (m.acc ? (m.acc * 100).toFixed(1) : 'N/A');
                const roc = m.metrics && m.metrics.roc_auc !== undefined ? m.metrics.roc_auc.toFixed(3) : (m.roc ? m.roc.toFixed(3) : 'N/A');
                const isBest = (m.metrics && m.metrics.accuracy === maxAcc) || (m.acc === maxAcc);

                const label = isBest 
                    ? `⭐ ${name} — ${acc}% Acc (Recommended)` 
                    : `${name} — ${acc}% Acc | ROC: ${roc}`;

                return `<option value="${id}" ${isBest && !window.appState.userSelectedModel ? 'selected' : ''}>${label}</option>`;
            }).join('');

            modelSelect.innerHTML = optionsHtml;

            const bestModelObj = compareRes.find(m => (m.metrics && m.metrics.accuracy === maxAcc) || (m.acc === maxAcc));
            if (bestModelObj && !window.appState.userSelectedModel) {
                window.appState.selectedModel = bestModelObj.model_name || bestModelObj.name;
            }
            if (window.appState.selectedModel) {
                modelSelect.value = window.appState.selectedModel;
            }
        }
    } catch (e) {
        console.warn('Failed to update model selector with performance data:', e);
    }
}

// App Initialization
async function initApp() {
    try {
        const datasetsRes = await api.get('/api/datasets').catch(() => [
            { dataset_id: 'loan_data', name: 'General Loan Dataset' },
            { dataset_id: 'home_loan_data', name: 'Home Loan Dataset' },
            { dataset_id: 'personal_loan_data', name: 'Personal Loan Dataset' }
        ]);

        window.appState.datasets = datasetsRes;
        
        const datasetSelect = document.getElementById('global-dataset-select');
        const modelSelect = document.getElementById('global-model-select');
        
        if (datasetSelect && datasetsRes && datasetsRes.length > 0) {
            datasetSelect.innerHTML = datasetsRes.map(d => `<option value="${d.dataset_id || d.id}">${d.name}</option>`).join('');
            window.appState.selectedDataset = datasetsRes[0].dataset_id || datasetsRes[0].id;
        }

        // Populate Model Selector with Performance Metrics & Recommendations
        await updateModelSelector(window.appState.selectedDataset);
        
        if (datasetSelect) {
            datasetSelect.addEventListener('change', async (e) => {
                const newDs = e.target.value;
                window.appState.userSelectedModel = false;
                window.appState.set('selectedDataset', newDs);
                await updateModelSelector(newDs);
                window.router.navigate();
            });
        }

        if (modelSelect) {
            modelSelect.addEventListener('change', (e) => {
                window.appState.userSelectedModel = true;
                window.appState.set('selectedModel', e.target.value);
                window.router.navigate();
            });
        }

    } catch (e) {
        console.warn('Failed to fetch initial config. Using defaults.', e);
    }
    
    // Register all loaded page modules & navigate
    setTimeout(() => {
        if (window.pages) {
            Object.keys(window.pages).forEach(key => window.router.register(key, window.pages[key]));
        }
        window.router.navigate();
    }, 50);
}

// Initialize on load
document.addEventListener('DOMContentLoaded', initApp);
