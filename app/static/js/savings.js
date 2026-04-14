document.addEventListener('DOMContentLoaded', function () {
    const addGoalBtn = document.getElementById('addGoalBtn');
    const newGoalModal = document.getElementById('newGoalModal');
    const contributeModal = document.getElementById('contributeModal');
    const toast = document.getElementById('toast');
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    const toastClose = document.querySelector('.toast-close');
    const saveGoalBtn = document.getElementById('saveGoalBtn');
    const confirmContributeBtn = document.getElementById('confirmContributeBtn');
    const contributeGoalName = document.getElementById('contributeGoalName');
    const contributeAmount = document.getElementById('contributeAmount');
    const remainingHint = document.getElementById('remainingHint');
    const goalNameInput = document.getElementById('goalName');
    const goalTargetInput = document.getElementById('goalTarget');
    const goalDeadlineInput = document.getElementById('goalDeadline');
    const goalDescriptionInput = document.getElementById('goalDescription');

    let activeGoalId = null;
    let activeGoalName = '';
    let activeGoalRemaining = 0;

    function showToast(message, type = 'success') {
        toastTitle.textContent = type === 'success' ? 'Success' : 'Error';
        toastMessage.textContent = message;
        toast.classList.add('show');
        toast.style.backgroundColor = type === 'success' ? '#e8f4ef' : '#fdecea';
        toastTitle.style.color = type === 'success' ? '#196633' : '#b71c1c';

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    function showModal(modal) {
        modal?.classList.add('show');
    }

    function hideModal(modal) {
        modal?.classList.remove('show');
    }

    function resetNewGoalForm() {
        goalNameInput.value = '';
        goalTargetInput.value = '';
        goalDeadlineInput.value = '';
        goalDescriptionInput.value = '';
    }

    function openContributeModal(goalCard) {
        activeGoalId = parseInt(goalCard.dataset.goalId, 10);
        activeGoalName = goalCard.dataset.goalName;
        activeGoalRemaining = parseFloat(goalCard.dataset.goalTarget || '0') - parseFloat(goalCard.dataset.goalCurrent || '0');

        contributeGoalName.value = activeGoalName;
        contributeAmount.value = '';
        remainingHint.textContent = `Remaining: $${activeGoalRemaining.toFixed(2)}`;
        showModal(contributeModal);
    }

    if (addGoalBtn) {
        addGoalBtn.addEventListener('click', () => {
            resetNewGoalForm();
            showModal(newGoalModal);
        });
    }

    document.querySelectorAll('.modal-close').forEach(button => {
        button.addEventListener('click', () => {
            hideModal(button.closest('.modal'));
        });
    });

    document.querySelectorAll('.modal-cancel').forEach(button => {
        button.addEventListener('click', () => {
            hideModal(button.closest('.modal'));
        });
    });

    [newGoalModal, contributeModal].forEach(modal => {
        modal?.addEventListener('click', event => {
            if (event.target === modal) {
                hideModal(modal);
            }
        });
    });

    toastClose?.addEventListener('click', () => {
        hideModal(toast);
    });

    document.querySelectorAll('.goal-card').forEach(card => {
        card.addEventListener('click', event => {
            if (event.target.closest('.btn-contribute')) {
                return;
            }
            openContributeModal(card);
        });
    });

    document.querySelectorAll('.btn-contribute').forEach(button => {
        button.addEventListener('click', event => {
            const card = event.target.closest('.goal-card');
            if (card) {
                openContributeModal(card);
            }
        });
    });

    async function submitNewGoal() {
        const name = goalNameInput.value.trim();
        const target = parseFloat(goalTargetInput.value);
        const targetDate = goalDeadlineInput.value || null;
        const description = goalDescriptionInput.value.trim() || null;

        if (!name) {
            showToast('Enter a goal name.', 'error');
            return;
        }
        if (isNaN(target) || target <= 0) {
            showToast('Enter a valid target amount.', 'error');
            return;
        }

        const response = await fetch('/savings/api/goals/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                target_amount: target,
                target_date: targetDate,
                description,
            }),
        });

        if (response.ok) {
            hideModal(newGoalModal);
            showToast('Savings goal created successfully.');
            setTimeout(() => window.location.reload(), 700);
            return;
        }

        const result = await response.json().catch(() => ({}));
        showToast(result.detail || 'Unable to create savings goal.', 'error');
    }

    async function submitContribution() {
        const amount = parseFloat(contributeAmount.value);
        if (isNaN(amount) || amount <= 0) {
            showToast('Enter a valid contribution amount.', 'error');
            return;
        }
        if (amount > activeGoalRemaining) {
            showToast('Contribution exceeds remaining amount.', 'error');
            return;
        }

        const response = await fetch('/savings/api/contribute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                goal_id: activeGoalId,
                amount,
            }),
        });

        if (response.ok) {
            hideModal(contributeModal);
            showToast(`Added $${amount.toFixed(2)} to ${activeGoalName}.`);
            setTimeout(() => window.location.reload(), 700);
            return;
        }

        const result = await response.json().catch(() => ({}));
        showToast(result.detail || 'Unable to update savings goal.', 'error');
    }

    saveGoalBtn?.addEventListener('click', submitNewGoal);
    confirmContributeBtn?.addEventListener('click', submitContribution);
});