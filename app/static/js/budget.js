
document.getElementById('menu-toggle')?.addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('collapsed');
});

// Show toast notification
function showToast(message, type = 'success') {
    const toastElement = document.getElementById('liveToast');
    const toastBody = toastElement.querySelector('.toast-body');
    const toastHeader = toastElement.querySelector('.toast-header');
    
    toastBody.textContent = message;
    
    if (type === 'success') {
        toastHeader.style.backgroundColor = '#198754';
        toastHeader.style.color = 'white';
    } else {
        toastHeader.style.backgroundColor = '#dc3545';
        toastHeader.style.color = 'white';
    }
    
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    setTimeout(() => {
        toastHeader.style.backgroundColor = '';
        toastHeader.style.color = '';
    }, 3000);
}

// Edit budget modal
let editModal = null;
let currentCategory = '';

document.querySelectorAll('.edit-budget-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const category = btn.getAttribute('data-category');
        const limit = parseFloat(btn.getAttribute('data-limit'));
        
        document.getElementById('editCategory').value = category;
        document.getElementById('editLimit').value = limit;
        currentCategory = category;
        
        editModal = new bootstrap.Modal(document.getElementById('editBudgetModal'));
        editModal.show();
    });
});

// Save budget changes
document.getElementById('saveBudgetBtn')?.addEventListener('click', async () => {
    const newLimit = parseFloat(document.getElementById('editLimit').value);
    
    if (isNaN(newLimit) || newLimit <= 0) {
        showToast('Please enter a valid budget limit', 'error');
        return;
    }
    
    const response = await fetch('/budget/api/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            category: currentCategory,
            limit: newLimit
        })
    });
    
    if (response.ok) {
        showToast('Budget updated successfully!', 'success');
        if (editModal) editModal.hide();
        setTimeout(() => window.location.reload(), 1000);
    } else {
        showToast('Failed to update budget', 'error');
    }
});

// Add category modal
let addModal = null;
document.getElementById('addCategoryBtn')?.addEventListener('click', () => {
    document.getElementById('addCategoryForm').reset();
    addModal = new bootstrap.Modal(document.getElementById('addCategoryModal'));
    addModal.show();
});

// Create new budget category
document.getElementById('createBudgetBtn')?.addEventListener('click', async () => {
    const category = document.getElementById('newCategory').value.trim();
    const limit = parseFloat(document.getElementById('newLimit').value);
    
    if (!category) {
        showToast('Please enter a category name', 'error');
        return;
    }
    
    if (isNaN(limit) || limit <= 0) {
        showToast('Please enter a valid budget limit', 'error');
        return;
    }
    
    const response = await fetch('/budget/api/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            category: category,
            limit: limit
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        showToast('Budget category added successfully!', 'success');
        if (addModal) addModal.hide();
        setTimeout(() => window.location.reload(), 1000);
    } else {
        showToast(result.error || 'Failed to add category', 'error');
    }
});