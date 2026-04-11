let currentUser = null;

async function getUserInfo() {
    try {
        const response = await fetch('/api/users/current');
        if (response.ok) {
            const data = await response.json();
            currentUser = data;
            document.getElementById('welcomeUser').innerHTML = `Welcome, ${data.username || 'User'}`;
        }
    } catch (error) {
        console.error('Error fetching user:', error);
        document.getElementById('welcomeUser').innerHTML = 'Welcome, User';
    }
}

// Show toast notification
function showToast(title, message, type = 'success') {
    const toastElement = document.getElementById('liveToast');
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    
    toastTitle.textContent = title;
    toastMessage.textContent = message;
    
    const toastHeader = toastElement.querySelector('.toast-header');
    if (type === 'success') {
        toastHeader.style.backgroundColor = '#198754';
        toastHeader.style.color = 'white';
    } else if (type === 'error') {
        toastHeader.style.backgroundColor = '#dc3545';
        toastHeader.style.color = 'white';
    } else {
        toastHeader.style.backgroundColor = '#0d6efd';
        toastHeader.style.color = 'white';
    }
    
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Reset color after 3 seconds
    setTimeout(() => {
        toastHeader.style.backgroundColor = '';
        toastHeader.style.color = '';
    }, 3000);
}

// Load and display expenses
async function loadExpenses() {
    const container = document.getElementById('expensesContainer');
    const spinner = document.getElementById('loadingSpinner');
    
    try {
        spinner.style.display = 'block';
        
        const response = await fetch('/expenses/api/expenses/categories');
        if (!response.ok) throw new Error('Failed to load expenses');
        
        const categories = await response.json();
        
    
        const totalResponse = await fetch('/expenses/api/expenses/total');
        const totalData = await totalResponse.json();
        document.getElementById('totalAmount').innerHTML = `$${totalData.total.toFixed(2)}`;
        

        if (Object.keys(categories).length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <span class="material-symbols-outlined" style="font-size: 64px; color: #6c757d;">receipt</span>
                    <h4 class="mt-3">No expenses yet</h4>
                    <p class="text-muted">Click "New Entry" to add your first expense</p>
                </div>
            `;
            spinner.style.display = 'none';
            return;
        }
        
        let html = '';
        for (const [category, data] of Object.entries(categories)) {
            html += `
                <div class="category-section">
                    <div class="category-header d-flex justify-content-between align-items-center" data-category="${category}">
                        <div class="d-flex align-items-center gap-3">
                            <h4>${category}</h4>
                            <span class="category-badge">${data.count} entries</span>
                        </div>
                        <div class="category-total">$${data.total.toFixed(2)}</div>
                    </div>
                    <div class="expense-list" id="category-${category.replace(/\s/g, '')}" style="display: block;">
            `;
            
            data.entries.forEach((expense, index) => {
                html += `
                    <div class="expense-item d-flex justify-content-between align-items-center" data-expense-index="${index}">
                        <div>
                            <div class="expense-name">${escapeHtml(expense.name)}</div>
                            <div class="expense-date">${expense.date}</div>
                        </div>
                        <div class="d-flex align-items-center gap-3">
                            <span class="expense-amount">-$${expense.amount.toFixed(2)}</span>
                            <button class="delete-expense" data-category="${category}" data-expense-name="${expense.name}">
                                <span class="material-symbols-outlined">delete</span>
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
        
        document.querySelectorAll('.category-header').forEach(header => {
            header.addEventListener('click', () => {
                const category = header.getAttribute('data-category');
                const list = document.getElementById(`category-${category.replace(/\s/g, '')}`);
                if (list) {
                    const isVisible = list.style.display !== 'none';
                    list.style.display = isVisible ? 'none' : 'block';
                }
            });
        });
        
        // Add delete handlers
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
        container.innerHTML = `
            <div class="alert alert-danger">
                Failed to load expenses. Please refresh the page.
            </div>
        `;
    } finally {
        spinner.style.display = 'none';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add new expense
async function addExpense(expenseData) {
    try {
        const response = await fetch('/expenses/api/expenses/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(expenseData)
        });
        
        if (response.ok) {
            const result = await response.json();
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


function initModal() {
    const addBtn = document.getElementById('addExpenseBtn');
    const saveBtn = document.getElementById('saveExpenseBtn');
    const modal = new bootstrap.Modal(document.getElementById('addExpenseModal'));
    
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('expenseDate').value = today;
    
    addBtn.addEventListener('click', () => {
        document.getElementById('addExpenseForm').reset();
        document.getElementById('expenseDate').value = today;
        modal.show();
    });
    
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
        
        if (!date) {
            showToast('Error', 'Please select a date', 'error');
            return;
        }
        
        const expenseData = { name, category, amount, date };
        
        const success = await addExpense(expenseData);
        if (success) {
            modal.hide();
            await loadExpenses();
        }
    });
}


function initSidebar() {
    const toggleBtn = document.getElementById('menu-toggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            document.getElementById('sidebar').classList.toggle('collapsed');
        });
    }
}


async function init() {
    await getUserInfo();
    initSidebar();
    initModal();
    await loadExpenses();
}

// Start when page loads
document.addEventListener('DOMContentLoaded', init);