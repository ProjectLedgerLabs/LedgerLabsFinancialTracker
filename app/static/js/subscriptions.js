let currentSubscriptions = [];


function showToast(message, type = 'success') {
    const toastElement = document.getElementById('liveToast');
    const toastBody = toastElement.querySelector('.toast-body');
    const toastHeader = toastElement.querySelector('.toast-header');
    
    toastBody.textContent = message;
    
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
    
    setTimeout(() => {
        toastHeader.style.backgroundColor = '';
        toastHeader.style.color = '';
    }, 3000);
}


async function loadSubscriptions() {
    try {
        const response = await fetch('/subscriptions/api/subscriptions/active');
        if (response.ok) {
            const data = await response.json();
            currentSubscriptions = data.subscriptions;
            updateStats();
            renderSubscriptions();
        }
    } catch (error) {
        console.error('Error loading subscriptions:', error);
    }
}


async function updateStats() {
    try {
        const response = await fetch('/subscriptions/api/subscriptions/stats');
        if (response.ok) {
            const stats = await response.json();
            

            const statValues = document.querySelectorAll('.stat-value');
            if (statValues.length >= 4) {
                statValues[0].innerHTML = `$${stats.monthly_cost.toFixed(2)}`;
                statValues[1].innerHTML = `$${stats.yearly_projection.toFixed(2)}`;
                statValues[2].innerHTML = stats.active_count;
                statValues[3].innerHTML = stats.upcoming.length;
            }
            

            const upcomingList = document.getElementById('upcomingList');
            if (upcomingList && stats.upcoming) {
                if (stats.upcoming.length === 0) {
                    upcomingList.innerHTML = '<p class="text-muted text-center">No upcoming bills in the next 30 days</p>';
                } else {
                    let html = '';
                    stats.upcoming.forEach(sub => {
                        html += `
                            <div class="upcoming-item">
                                <div>
                                    <strong>${escapeHtml(sub.name)}</strong>
                                    <div class="text-muted small">${sub.category}</div>
                                </div>
                                <div class="text-end">
                                    <div>$${sub.amount.toFixed(2)}</div>
                                    <small class="text-muted">${sub.days_until} days</small>
                                </div>
                            </div>
                        `;
                    });
                    upcomingList.innerHTML = html;
                }
            }
        }
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}


function renderSubscriptions() {
    const container = document.getElementById('subscriptionsList');
    if (!container) return;
    
    const categoryColors = {
        Health: 'danger',
        Software: 'primary',
        Entertainment: 'success',
        Food: 'warning',
        Utilities: 'info'
    };
    
    let html = '';
    currentSubscriptions.forEach(sub => {
        const color = categoryColors[sub.category] || 'secondary';
        html += `
            <div class="subscription-card" data-id="${sub.id}">
                <div class="card-header">
                    <div>
                        <h5>${escapeHtml(sub.name)}</h5>
                        <span class="badge bg-${color}">${sub.category}</span>
                    </div>
                    <div class="subscription-actions">
                        <span class="badge bg-secondary">${sub.billing_cycle}</span>
                        <button class="btn-icon edit-sub" data-id="${sub.id}">
                            <span class="material-symbols-outlined">edit</span>
                        </button>
                        <button class="btn-icon delete-sub" data-id="${sub.id}">
                            <span class="material-symbols-outlined">delete</span>
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="amount">$${sub.amount.toFixed(2)}</div>
                    <div class="next-billing">
                        <span class="material-symbols-outlined">event</span>
                        Next: ${sub.next_billing}
                    </div>
                </div>
            </div>
        `;
    });
    
    if (currentSubscriptions.length === 0) {
        html = '<p class="text-muted text-center">No active subscriptions. Add one to get started!</p>';
    }
    
    container.innerHTML = html;
    

    document.querySelectorAll('.edit-sub').forEach(btn => {
        btn.addEventListener('click', () => editSubscription(parseInt(btn.dataset.id)));
    });
    
    document.querySelectorAll('.delete-sub').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = parseInt(btn.dataset.id);
            const subscription = currentSubscriptions.find(sub => sub.id === id);
            showDeleteSubscriptionModal(id, subscription ? subscription.name : 'this subscription');
        });
    });
}

function showDeleteSubscriptionModal(id, name) {
    const deleteIdInput = document.getElementById('deleteSubId');
    const message = document.getElementById('deleteSubscriptionMessage');
    if (deleteIdInput) deleteIdInput.value = id;
    if (message) message.textContent = `Are you sure you want to delete "${name}"?`;
    const deleteModalEl = document.getElementById('deleteSubscriptionModal');
    if (deleteModalEl) {
        const modal = new bootstrap.Modal(deleteModalEl);
        modal.show();
    }
}

async function deleteSubscription(id) {
    const deleteIdInput = document.getElementById('deleteSubId');
    if (!deleteIdInput || !deleteIdInput.value) return;
    id = parseInt(deleteIdInput.value);

    try {
        const response = await fetch(`/subscriptions/api/subscriptions/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showToast('Subscription deleted successfully!', 'success');
            await loadSubscriptions();
            const deleteModalEl = document.getElementById('deleteSubscriptionModal');
            if (deleteModalEl) {
                const modal = bootstrap.Modal.getInstance(deleteModalEl);
                if (modal) modal.hide();
            }
        } else {
            showToast('Failed to delete subscription', 'error');
        }
    } catch (error) {
        console.error('Error deleting subscription:', error);
        showToast('Network error occurred', 'error');
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}


async function addSubscription(subscriptionData) {
    try {
        const response = await fetch('/subscriptions/api/subscriptions/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(subscriptionData)
        });
        
        if (response.ok) {
            showToast('Subscription added successfully!', 'success');
            await loadSubscriptions();
            return true;
        } else {
            showToast('Failed to add subscription', 'error');
            return false;
        }
    } catch (error) {
        console.error('Error adding subscription:', error);
        showToast('Network error occurred', 'error');
        return false;
    }
}


async function editSubscription(id) {
    const sub = currentSubscriptions.find(s => s.id === id);
    if (!sub) return;
    
    document.getElementById('modalTitle').textContent = 'Edit Subscription';
    document.getElementById('subId').value = sub.id;
    document.getElementById('subName').value = sub.name;
    document.getElementById('subAmount').value = sub.amount;
    document.getElementById('subCategory').value = sub.category;
    document.getElementById('subBillingCycle').value = sub.billing_cycle;
    document.getElementById('subNextBilling').value = sub.next_billing;
    
    const modal = new bootstrap.Modal(document.getElementById('subscriptionModal'));
    modal.show();
}


async function updateSubscription(id, updates) {
    try {
        const response = await fetch(`/subscriptions/api/subscriptions/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        });
        
        if (response.ok) {
            showToast('Subscription updated successfully!', 'success');
            await loadSubscriptions();
            return true;
        } else {
            showToast('Failed to update subscription', 'error');
            return false;
        }
    } catch (error) {
        console.error('Error updating subscription:', error);
        showToast('Network error occurred', 'error');
        return false;
    }
}


async function deleteSubscription(id) {
    const deleteIdInput = document.getElementById('deleteSubId');
    if (!deleteIdInput || !deleteIdInput.value) return;
    id = parseInt(deleteIdInput.value);

    try {
        const response = await fetch(`/subscriptions/api/subscriptions/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showToast('Subscription deleted successfully!', 'success');
            await loadSubscriptions();
            const deleteModalEl = document.getElementById('deleteSubscriptionModal');
            if (deleteModalEl) {
                const modal = bootstrap.Modal.getInstance(deleteModalEl);
                if (modal) modal.hide();
            }
        } else {
            showToast('Failed to delete subscription', 'error');
        }
    } catch (error) {
        console.error('Error deleting subscription:', error);
        showToast('Network error occurred', 'error');
    }
}

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

function initModal() {
    const addBtn = document.getElementById('addSubBtn');
    const saveBtn = document.getElementById('saveSubBtn');
    let modal = null;
    
    const defaultDate = new Date();
    defaultDate.setMonth(defaultDate.getMonth() + 1);
    const defaultDateStr = defaultDate.toISOString().split('T')[0];
    
    if (addBtn) {
        addBtn.addEventListener('click', () => {
            document.getElementById('modalTitle').textContent = 'Add Subscription';
            document.getElementById('subId').value = '';
            document.getElementById('subscriptionForm').reset();
            document.getElementById('subNextBilling').value = defaultDateStr;
            modal = new bootstrap.Modal(document.getElementById('subscriptionModal'));
            modal.show();
        });
    }
    
    const confirmDeleteBtn = document.getElementById('confirmDeleteSubBtn');

    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
            const id = document.getElementById('subId').value;
            const name = document.getElementById('subName').value.trim();
            const amount = parseFloat(document.getElementById('subAmount').value);
            const category = document.getElementById('subCategory').value;
            const billing_cycle = document.getElementById('subBillingCycle').value;
            const next_billing = document.getElementById('subNextBilling').value;
            
            if (!name) {
                showToast('Please enter a service name', 'error');
                return;
            }
            
            if (isNaN(amount) || amount <= 0) {
                showToast('Please enter a valid amount', 'error');
                return;
            }
            
            if (!next_billing) {
                showToast('Please select a next billing date', 'error');
                return;
            }
            
            const subscriptionData = { name, amount, category, billing_cycle, next_billing };
            
            let success;
            if (id) {
                success = await updateSubscription(parseInt(id), subscriptionData);
            } else {
                success = await addSubscription(subscriptionData);
            }
            
            if (success && modal) {
                modal.hide();
            }
        });
    }

    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', async () => {
            await deleteSubscription();
        });
    }
}

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

async function init() {
    initSidebarToggleFallback();
    initModal();
    await loadSubscriptions();
}

document.addEventListener('DOMContentLoaded', init);