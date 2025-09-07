// API Base URL - Update this when deploying
const API_BASE = 'http://localhost:8000';

// Global state
let applications = [];
let filteredApplications = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadApplications();
    setupEventListeners();
    showBotInstructions();
});

// Setup event listeners
function setupEventListeners() {
    // Add application form
    document.getElementById('addApplicationForm').addEventListener('submit', handleAddApplication);
    
    // Search and filter
    document.getElementById('searchInput').addEventListener('input', filterApplications);
    document.getElementById('statusFilter').addEventListener('change', filterApplications);
    
    // Sync button
    document.getElementById('syncBtn').addEventListener('click', syncGmail);
}

// Show bot instructions on first visit
function showBotInstructions() {
    if (!localStorage.getItem('botInstructionsShown')) {
        document.getElementById('botModal').classList.remove('hidden');
        document.getElementById('botModal').classList.add('flex');
        localStorage.setItem('botInstructionsShown', 'true');
    }
}

// Close bot modal
function closeBotModal() {
    document.getElementById('botModal').classList.add('hidden');
    document.getElementById('botModal').classList.remove('flex');
}

// Load applications from API
async function loadApplications() {
    try {
        const response = await fetch(`${API_BASE}/applications`);
        if (response.ok) {
            applications = await response.json();
            filteredApplications = [...applications];
            updateStats();
            renderApplications();
        } else {
            // Show demo data if API is not available
            loadDemoData();
        }
    } catch (error) {
        console.log('API not available, showing demo data');
        loadDemoData();
    }
}

// Load demo data for preview
function loadDemoData() {
    applications = [
        {
            id: 1,
            company_name: "Google",
            role: "Software Engineer",
            platform: "LinkedIn",
            status: "Interview Scheduled",
            date_applied: "2024-01-15",
            job_link: "https://careers.google.com/jobs/123"
        },
        {
            id: 2,
            company_name: "Microsoft",
            role: "Frontend Developer",
            platform: "Indeed",
            status: "In Review",
            date_applied: "2024-01-10",
            job_link: "https://careers.microsoft.com/jobs/456"
        },
        {
            id: 3,
            company_name: "Amazon",
            role: "Full Stack Developer",
            platform: "Company Website",
            status: "Applied",
            date_applied: "2024-01-08",
            job_link: "https://amazon.jobs/en/jobs/789"
        },
        {
            id: 4,
            company_name: "Meta",
            role: "React Developer",
            platform: "LinkedIn",
            status: "Offer",
            date_applied: "2024-01-05",
            job_link: "https://careers.meta.com/jobs/101"
        },
        {
            id: 5,
            company_name: "Netflix",
            role: "Backend Engineer",
            platform: "Naukri",
            status: "Rejected",
            date_applied: "2024-01-03",
            job_link: "https://jobs.netflix.com/jobs/112"
        }
    ];
    filteredApplications = [...applications];
    updateStats();
    renderApplications();
    showToast('Demo data loaded - Connect to API for real data', 'info');
}

// Update statistics
function updateStats() {
    const total = applications.length;
    const interviews = applications.filter(app => app.status === 'Interview Scheduled').length;
    const offers = applications.filter(app => app.status === 'Offer').length;
    const successRate = total > 0 ? Math.round((offers / total) * 100) : 0;

    document.getElementById('totalApps').textContent = total;
    document.getElementById('interviewCount').textContent = interviews;
    document.getElementById('offerCount').textContent = offers;
    document.getElementById('successRate').textContent = `${successRate}%`;
}

// Render applications list
function renderApplications() {
    const container = document.getElementById('applicationsList');
    
    if (filteredApplications.length === 0) {
        container.innerHTML = `
            <div class="p-8 text-center text-gray-500">
                <i class="fas fa-inbox text-4xl mb-4"></i>
                <p class="text-lg">No applications found</p>
                <p class="text-sm">Add your first job application above</p>
            </div>
        `;
        return;
    }

    container.innerHTML = filteredApplications.map(app => `
        <div class="p-6 hover:bg-gray-50 transition-colors duration-200">
            <div class="flex items-center justify-between">
                <div class="flex-1">
                    <div class="flex items-center space-x-4">
                        <div class="flex-1">
                            <h3 class="text-lg font-semibold text-gray-900">${app.company_name}</h3>
                            <p class="text-gray-600">${app.role}</p>
                            <div class="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                                <span><i class="fas fa-calendar mr-1"></i>${formatDate(app.date_applied)}</span>
                                <span><i class="fas fa-globe mr-1"></i>${app.platform}</span>
                                ${app.job_link ? `<a href="${app.job_link}" target="_blank" class="text-blue-600 hover:text-blue-800"><i class="fas fa-external-link-alt mr-1"></i>View Job</a>` : ''}
                            </div>
                        </div>
                        <div class="flex items-center space-x-3">
                            <span class="px-3 py-1 rounded-full text-sm font-medium text-white ${getStatusClass(app.status)}">
                                ${app.status}
                            </span>
                            <div class="flex space-x-2">
                                <button onclick="updateStatus(${app.id}, '${app.status}')" class="text-blue-600 hover:text-blue-800 p-2">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button onclick="deleteApplication(${app.id})" class="text-red-600 hover:text-red-800 p-2">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// Handle add application form
async function handleAddApplication(e) {
    e.preventDefault();
    
    const formData = {
        company_name: document.getElementById('companyName').value,
        role: document.getElementById('roleName').value,
        platform: document.getElementById('platform').value,
        date_applied: new Date().toISOString().split('T')[0],
        status: 'Applied'
    };

    try {
        const response = await fetch(`${API_BASE}/applications`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            const newApp = await response.json();
            applications.unshift(newApp);
            filteredApplications = [...applications];
            updateStats();
            renderApplications();
            document.getElementById('addApplicationForm').reset();
            showToast('Application added successfully!');
        } else {
            throw new Error('Failed to add application');
        }
    } catch (error) {
        // Demo mode - add to local array
        const newApp = {
            id: Date.now(),
            ...formData
        };
        applications.unshift(newApp);
        filteredApplications = [...applications];
        updateStats();
        renderApplications();
        document.getElementById('addApplicationForm').reset();
        showToast('Application added (Demo Mode)');
    }
}

// Update application status
async function updateStatus(id, currentStatus) {
    const statuses = ['Applied', 'In Review', 'Interview Scheduled', 'Offer', 'Rejected'];
    const currentIndex = statuses.indexOf(currentStatus);
    const nextStatus = statuses[(currentIndex + 1) % statuses.length];

    try {
        const response = await fetch(`${API_BASE}/applications/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: nextStatus })
        });

        if (response.ok) {
            const updatedApp = await response.json();
            const index = applications.findIndex(app => app.id === id);
            applications[index] = updatedApp;
            filteredApplications = [...applications];
            updateStats();
            renderApplications();
            showToast(`Status updated to ${nextStatus}`);
        } else {
            throw new Error('Failed to update status');
        }
    } catch (error) {
        // Demo mode - update local array
        const index = applications.findIndex(app => app.id === id);
        applications[index].status = nextStatus;
        filteredApplications = [...applications];
        updateStats();
        renderApplications();
        showToast(`Status updated to ${nextStatus} (Demo Mode)`);
    }
}

// Delete application
async function deleteApplication(id) {
    if (!confirm('Are you sure you want to delete this application?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/applications/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            applications = applications.filter(app => app.id !== id);
            filteredApplications = [...applications];
            updateStats();
            renderApplications();
            showToast('Application deleted successfully!');
        } else {
            throw new Error('Failed to delete application');
        }
    } catch (error) {
        // Demo mode - remove from local array
        applications = applications.filter(app => app.id !== id);
        filteredApplications = [...applications];
        updateStats();
        renderApplications();
        showToast('Application deleted (Demo Mode)');
    }
}

// Filter applications
function filterApplications() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value;

    filteredApplications = applications.filter(app => {
        const matchesSearch = app.company_name.toLowerCase().includes(searchTerm) || 
                            app.role.toLowerCase().includes(searchTerm);
        const matchesStatus = !statusFilter || app.status === statusFilter;
        
        return matchesSearch && matchesStatus;
    });

    renderApplications();
}

// Sync Gmail
async function syncGmail() {
    const syncBtn = document.getElementById('syncBtn');
    const originalText = syncBtn.innerHTML;
    
    syncBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Syncing...</span>';
    syncBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/sync-emails`, {
            method: 'POST'
        });

        if (response.ok) {
            const result = await response.json();
            if (result.updated && result.updated.length > 0) {
                showToast(`Synced ${result.updated.length} updates from Gmail!`);
                loadApplications(); // Reload applications
            } else {
                showToast('No new updates found in Gmail', 'info');
            }
        } else {
            throw new Error('Sync failed');
        }
    } catch (error) {
        showToast('Gmail sync not available (Demo Mode)', 'warning');
    } finally {
        setTimeout(() => {
            syncBtn.innerHTML = originalText;
            syncBtn.disabled = false;
        }, 2000);
    }
}

// Utility functions
function getStatusClass(status) {
    const statusClasses = {
        'Applied': 'status-applied',
        'In Review': 'status-review',
        'Interview Scheduled': 'status-interview',
        'Offer': 'status-offer',
        'Rejected': 'status-rejected'
    };
    return statusClasses[status] || 'bg-gray-500';
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    
    // Set message
    toastMessage.textContent = message;
    
    // Set color based on type
    toast.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg transform transition-transform duration-300 z-50 ${
        type === 'success' ? 'bg-green-500' : 
        type === 'warning' ? 'bg-yellow-500' : 
        type === 'error' ? 'bg-red-500' : 'bg-blue-500'
    } text-white`;
    
    // Show toast
    toast.style.transform = 'translateX(0)';
    
    // Hide after 3 seconds
    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
    }, 3000);
}