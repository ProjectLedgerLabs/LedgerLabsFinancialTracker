// Expenses Page JavaScript
let currentUser = null;

// Category color mapping
const categoryColors = {
    'Food': '#006699',
    'Transportation': '#669900',
    'Entertainment': '#ff6600',
    'Health': '#cc3399',
    'Software': '#99cc33',
    'Utilities': '#ffcc00'
};

// Initialize sidebar toggle fallback
function initSidebarToggleFallback() {
    if (window.__sidebarToggleAttached) return;
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function () {
            sidebar.classList.toggle('collapsed');
        });
        window.__sidebarToggleAttached = true;
    }
}

// Initialize page
async function init() {
    initSidebarToggleFallback();
    await getUserInfo();
    initModal();
    await loadExpenses();
}

// Get user info
async function getUserInfo() {
    try {
        const response = await fetch('/api/users/current');
        if (response.ok) {
            const data = await response.json();
            currentUser = data;
        }
    } catch (error) {
        console.error('Error fetching user:', error);
    }
}

// Load and display expenses
async function loadExpenses() {
    const container = document.getElementById('expensesContainer');
    const spinner = document.getElementById('loadingSpinner');
    
    try {
        if (spinner) spinner.style.display = 'flex';
        
        const response = await fetch('/expenses/api/expenses/categories');
        if (!response.ok) throw new Error('Failed to load expenses');
        
        const categories = await response.json();
        
        // Update total
        const totalResponse = await fetch('/expenses/api/expenses/total');
        const totalData = await totalResponse.json();
        const totalAmount = document.getElementById('totalAmount');
        if (totalAmount) totalAmount.textContent = `$${totalData.total.toFixed(2)}`;
        
        // Render categories
        if (Object.keys(categories).length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <h4>No expenses yet</h4>
                    <p class="text-muted">Click "Add Expense" to get started</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        for (const [category, data] of Object.entries(categories)) {
            const categoryId = category.replace(/\s/g, '');
            html += `
                <div class="category-section">
                    <div class="category-header" data-category="${category}">
                        <div class="d-flex align-items-center gap-3">
                            <h4>${escapeHtml(category)}</h4>
                            <span class="category-badge">${data.count} entries</span>
                        </div>
                        <div class="category-total">$${data.total.toFixed(2)}</div>
                    </div>
                    <div class="expense-list" id="category-${categoryId}">
            `;
            
            data.entries.forEach((expense, index) => {
                html += `
                    <div class="expense-item" data-expense-index="${index}">
                        <div>
                            <div class="expense-name">${escapeHtml(expense.name)}</div>
                            <div class="expense-date">${expense.date}</div>
                        </div>
                        <div class="d-flex align-items-center gap-3">
                            <span class="expense-amount">-$${expense.amount.toFixed(2)}</span>
                            <button class="delete-expense" data-category="${category}" data-expense-name="${expense.name}">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                                </svg>
                            </button>
                        </div>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        container.innerHTML = html;
        
        // Add event listeners
        document.querySelectorAll('.category-header').forEach(header => {
            header.addEventListener('click', () => {
                const category = header.getAttribute('data-category');
                const list = document.getElementById(`category-${category.replace(/\s/g, '')}`);
                if (list) {
                    list.classList.toggle('expanded');
                    list.style.display = list.style.display === 'none' ? 'block' : 'none';
                }
            });
        });
        
        document.querySelectorAll('.delete-expense').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const expenseName = btn.getAttribute('data-expense-name');
                if (confirm(`Delete "${expenseName}"?`)) {
                    showToast('Info', 'Delete functionality requires backend implementation', 'info');
                }
            });
        });
        
    } catch (error) {
        console.error('Error loading expenses:', error);
        container.innerHTML = `<div class="alert alert-danger">Failed to load expenses. Please refresh the page.</div>`;
    } finally {
        if (spinner) spinner.style.display = 'none';
    }
}

// Add expense
async function addExpense(expenseData) {
    try {
        const response = await fetch('/expenses/api/expenses/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(expenseData)
        });
        
        if (response.ok) {
            showToast('Success', 'Expense added successfully!', 'success');
            return true;
        } else {
            const error = await response.json();
            showToast('Error', error.detail || 'Failed to add expense', 'error');
            return false;
        }
    } catch (error) {
        console.error('Error adding expense:', error);
        showToast('Error', 'Network error occurred', 'error');
        return false;
    }
}

// Initialize modal
function initModal() {
    const modal = document.getElementById('addExpenseModal');
    const addBtn = document.getElementById('addExpenseBtn');
    const cancelBtn = document.querySelector('.modal-cancel');
    const closeBtn = document.querySelector('.modal-close');
    const saveBtn = document.getElementById('saveExpenseBtn');
    
    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('expenseDate');
    if (dateInput) dateInput.value = today;
    
    if (addBtn) {
        addBtn.addEventListener('click', () => {
            document.getElementById('addExpenseForm').reset();
            if (dateInput) dateInput.value = today;
            modal.classList.add('show');
        });
    }
    
    const closeModal = () => modal.classList.remove('show');
    
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
    
    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
            const name = document.getElementById('expenseName').value.trim();
            const category = document.getElementById('expenseCategory').value;
            const amount = parseFloat(document.getElementById('expenseAmount').value);
            const date = document.getElementById('expenseDate').value;
            
            if (!name) {
                showToast('Error', 'Please enter an expense name', 'error');
                return;
            }
            
            if (isNaN(amount) || amount <= 0) {
                showToast('Error', 'Please enter a valid amount', 'error');
                return;
            }
            
            const expenseData = { name, category, amount, date };
            const success = await addExpense(expenseData);
            
            if (success) {
                closeModal();
                await loadExpenses();
            }
        });
    }
}

// Show toast notification
function showToast(title, message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    const toastHeader = toast.querySelector('.toast-header');
    
    toastTitle.textContent = title;
    toastMessage.textContent = message;
    
    const colors = {
        success: '#198754',
        error: '#dc3545',
        info: '#0d6efd'
    };
    
    toastHeader.style.backgroundColor = colors[type] || colors.success;
    toastHeader.style.color = 'white';
    
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toastHeader.style.backgroundColor = '';
            toastHeader.style.color = '';
        }, 300);
    }, 3000);
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Start when page loads
document.addEventListener('DOMContentLoaded', init);