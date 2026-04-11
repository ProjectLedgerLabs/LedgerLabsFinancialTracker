document.addEventListener('DOMContentLoaded', function() {
    
    async function refreshSavingsData() {
        try {
            const response = await fetch('/savings/api/summary');
            if (response.ok) {
                const data = await response.json();
                console.log('Savings summary updated:', data);
            }
        } catch (error) {
            console.error('Error refreshing savings data:', error);
        }
    }
    

    function formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(amount);
    }
    

    function daysBetween(date1, date2) {
        const oneDay = 24 * 60 * 60 * 1000;
        return Math.round(Math.abs((date1 - date2) / oneDay));
    }
    

    async function updateGoalProgress(goalName, newAmount) {
        try {
            const response = await fetch('/savings/api/contribute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ goal_name: goalName, amount: newAmount })
            });
            
            if (response.ok) {
                const result = await response.json();
                return result;
            }
            return null;
        } catch (error) {
            console.error('Error updating goal:', error);
            return null;
        }
    }
    
    window.savingsHelpers = {
        formatCurrency,
        daysBetween,
        updateGoalProgress,
        refreshSavingsData
    };
});