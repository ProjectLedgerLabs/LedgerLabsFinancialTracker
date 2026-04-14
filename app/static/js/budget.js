
// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('menu-toggle')?.addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('collapsed');
    });

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
    const addCategoryBtn = document.getElementById('addCategoryBtn');
    console.log('Button element:', addCategoryBtn);
    console.log('Modal element:', document.getElementById('addCategoryModal'));
    
    if (addCategoryBtn) {
        addCategoryBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🔵 Add Budget button clicked!');
            try {
                const modalEl = document.getElementById('addCategoryModal');
                const form = document.getElementById('addCategoryForm');
                if (form) form.reset();
                if (modalEl) {
                    addModal = new bootstrap.Modal(modalEl);
                    addModal.show();
                    console.log('✅ Modal shown');
                } else {
                    console.error('❌ Modal element not found');
                }
            } catch (err) {
                console.error('Error showing modal:', err);
            }
        });
    } else {
        console.error('❌ Add Budget button not found');
    }

    // Create new budget category
    const createBudgetBtn = document.getElementById('createBudgetBtn');
    console.log('Create button element:', createBudgetBtn);
    
    if (createBudgetBtn) {
        createBudgetBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            console.log('🔵 Save Budget button clicked');
            try {
                const categorySelect = document.getElementById('newCategory');
                const limitInput = document.getElementById('newLimit');
                
                if (!categorySelect || !limitInput) {
                    console.error('Form elements not found');
                    return;
                }
                
                const category = categorySelect.value.trim();
                const limit = parseFloat(limitInput.value);
                
                console.log('📋 Form values:', { category, limit });
                
                if (!category) {
                    console.warn('⚠️ No category selected');
                    showToast('Please select a category', 'error');
                    return;
                }
                
                if (isNaN(limit) || limit <= 0) {
                    console.warn('⚠️ Invalid limit:', limit);
                    showToast('Please enter a valid budget limit', 'error');
                    return;
                }
                
                console.log('🚀 Sending to API:', { category, limit });
                
                const response = await fetch('/budget/api/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        category: category,
                        limit: limit
                    })
                });
                
                console.log('📡 API Response status:', response.status);
                
                const result = await response.json();
                console.log('📦 API Response:', result);
                
                if (response.ok && result.success) {
                    showToast('Budget added successfully!', 'success');
                    if (addModal) addModal.hide();
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    const errorMsg = result.error || result.detail || 'Failed to add budget';
                    console.error('❌ API Error:', errorMsg);
                    showToast(errorMsg, 'error');
                }
            } catch (err) {
                console.error('❌ Exception:', err);
                showToast('An error occurred', 'error');
            }
        });
    } else {
        console.error('❌ Create Budget button not found');
    }
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