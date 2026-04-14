(function() {
  'use strict';

  const state = {
    currentPage: 'dashboard',
    monthlyIncome: 5000.00,
    expenses: [
      { name: 'Grocery shopping', category: 'Food', amount: 156.32, date: '2026-04-05' },
      { name: 'Gas station', category: 'Transportation', amount: 65.00, date: '2026-04-03' },
      { name: 'Restaurant dinner', category: 'Food', amount: 89.50, date: '2026-04-01' },
      { name: 'Coffee shop', category: 'Food', amount: 12.75, date: '2026-04-08' },
      { name: 'Movie tickets', category: 'Entertainment', amount: 34.00, date: '2026-04-06' },
      { name: 'Gym membership', category: 'Health', amount: 49.99, date: '2026-04-01' },
      { name: 'Netflix', category: 'Software', amount: 15.99, date: '2026-04-01' },
      { name: 'Spotify', category: 'Software', amount: 9.99, date: '2026-04-01' },
      { name: 'Internet bill', category: 'Utilities', amount: 80.00, date: '2026-04-01' },
      { name: 'Electric bill', category: 'Utilities', amount: 100.00, date: '2026-04-02' }
    ],
    budgets: [], // Will be loaded from API
    subscriptions: [
      { name: 'Netflix', amount: 15.99, nextBilling: '2026-05-01', category: 'Entertainment' },
      { name: 'Spotify', amount: 9.99, nextBilling: '2026-05-01', category: 'Entertainment' },
      { name: 'Gym Membership', amount: 49.99, nextBilling: '2026-05-01', category: 'Health' },
      { name: 'Cloud Storage', amount: 5.00, nextBilling: '2026-05-15', category: 'Software' }
    ],
    savingsGoals: [
      { name: 'Emergency Fund', target: 10000, current: 3500 },
      { name: 'Vacation', target: 3000, current: 1200 },
      { name: 'New Car', target: 15000, current: 5000 }
    ]
  };

  let incomeChart = null;
  let categoryChart = null;

  function calculateStats() {
    const totalExpenses = state.expenses.reduce((sum, exp) => sum + exp.amount, 0);
    const burnRate = state.monthlyIncome - totalExpenses;
    const savingsRate = ((burnRate / state.monthlyIncome) * 100).toFixed(1);
    return {
      totalExpenses: totalExpenses.toFixed(2),
      burnRate: burnRate.toFixed(2),
      savingsRate: savingsRate
    };
  }

  function updateDashboardStats() {
    const stats = calculateStats();
    document.getElementById('monthlyIncome').textContent = `$${state.monthlyIncome.toFixed(2)}`;
    document.getElementById('totalExpenses').textContent = `$${stats.totalExpenses}`;
    document.getElementById('burnRate').textContent = `$${stats.burnRate}`;
    document.getElementById('savingsRate').textContent = `${stats.savingsRate}%`;
  }

  function initIncomeExpensesChart() {
    const ctx = document.getElementById('incomeExpensesChart');
    if (!ctx) return;

    const monthlyData = {
      labels: ['Jan', 'Feb', 'Mar', 'Apr'],
      income: [5000, 5000, 5000, 5000],
      expenses: [450, 520, 380, 465]
    };

    if (incomeChart) incomeChart.destroy();

    incomeChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: monthlyData.labels,
        datasets: [
          {
            label: 'Income',
            data: monthlyData.income,
            borderColor: '#2C5F8D',
            backgroundColor: 'rgba(44, 95, 141, 0.1)',
            fill: true,
            tension: 0.4,
            borderWidth: 2
          },
          {
            label: 'Expenses',
            data: monthlyData.expenses,
            borderColor: '#C4846B',
            backgroundColor: 'rgba(196, 132, 107, 0.1)',
            fill: true,
            tension: 0.4,
            borderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true, position: 'bottom', labels: { usePointStyle: true, padding: 15 } },
          tooltip: { mode: 'index', intersect: false }
        },
        scales: {
          y: { beginAtZero: true, grid: { color: 'rgba(0, 0, 0, 0.05)' }, ticks: { callback: function(value) { return '$' + value; } } },
          x: { grid: { display: false } }
        }
      }
    });
  }

  function initCategoryChart() {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;

    const categoryData = {};
    state.expenses.forEach(exp => {
      categoryData[exp.category] = (categoryData[exp.category] || 0) + exp.amount;
    });

    const labels = Object.keys(categoryData);
    const data = Object.values(categoryData);
    const colors = ['#2C5F8D', '#5A9FC9', '#8DB9D9', '#C4846B', '#9A7B6B', '#6B8EA3'];

    if (categoryChart) categoryChart.destroy();

    categoryChart = new Chart(ctx, {
      type: 'doughnut',
      data: { labels: labels, datasets: [{ data: data, backgroundColor: colors.slice(0, labels.length), borderWidth: 2, borderColor: '#fff' }] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true, position: 'bottom', labels: { usePointStyle: true, padding: 10 } },
          tooltip: { callbacks: { label: function(context) { return context.label + ': $' + context.parsed.toFixed(2); } } }
        }
      }
    });
  }

  function loadBudgets() {
    return fetch('/finance/api/budgets')
      .then(response => response.json())
      .then(data => {
        state.budgets = data.budgets || [];
        return state.budgets;
      })
      .catch(error => {
        console.error('Failed to load budgets:', error);
        return [];
      });
  }
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';
    expensesList.forEach(expense => {
      const item = document.createElement('div');
      item.className = 'expense-item';
      item.innerHTML = `<div class="expense-item__details"><h4 class="expense-item__name">${expense.name}</h4><p class="expense-item__meta">${expense.category} • ${expense.date}</p></div><div class="expense-item__amount">-$${expense.amount.toFixed(2)}</div>`;
      container.appendChild(item);
    });
  }

  function renderSubscriptions() {
    const container = document.getElementById('subscriptionList');
    if (!container) return;
    container.innerHTML = '';
    state.subscriptions.forEach(sub => {
      const item = document.createElement('div');
      item.className = 'subscription-item';
      item.innerHTML = `<div><h4>${sub.name}</h4><p style="font-size: 12px; color: var(--color-text-secondary);">${sub.category} • Next billing: ${sub.nextBilling}</p></div><div style="font-size: 16px; font-weight: 500;">$${sub.amount.toFixed(2)}/mo</div>`;
      container.appendChild(item);
    });
  }

  function renderBudgetOverview() {
    const container = document.getElementById('budgetOverview');
    if (!container) return;
    container.innerHTML = '';
    state.budgets.forEach(budget => {
      const percentage = Math.min(budget.percentage, 100);
      const colorClass = getProgressColorClass(budget.category);
      const item = document.createElement('div');
      item.className = 'budget-item';
      item.innerHTML = `<div class="budget-item__header"><span class="budget-item__label">${budget.category}</span><span class="budget-item__amount">$${budget.spent.toFixed(2)} / $${budget.limit.toFixed(2)}</span></div><div class="progress-bar"><div class="progress-bar__fill ${colorClass}" style="width: ${percentage}%"></div></div>`;
      container.appendChild(item);
    });
  }

  function renderSavingsGoals() {
    const container = document.getElementById('savingsGoals');
    if (!container) return;
    container.innerHTML = '';
    state.savingsGoals.forEach(goal => {
      const percentage = Math.min((goal.current / goal.target) * 100, 100);
      const item = document.createElement('div');
      item.className = 'savings-item';
      item.innerHTML = `<div style="flex: 1;"><h4>${goal.name}</h4><p style="font-size: 12px; color: var(--color-text-secondary); margin: 8px 0;">$${goal.current.toFixed(2)} of $${goal.target.toFixed(2)}</p><div class="progress-bar"><div class="progress-bar__fill progress-bar__fill--blue" style="width: ${percentage}%"></div></div></div><div style="font-size: 18px; font-weight: 500; margin-left: 16px;">${percentage.toFixed(0)}%</div>`;
      container.appendChild(item);
    });
  }

  function getProgressColorClass(category) {
    const colorMap = {
      Food: 'progress-bar__fill--blue',
      Transportation: 'progress-bar__fill--teal',
      Entertainment: 'progress-bar__fill--sky',
      Health: 'progress-bar__fill--orange',
      Software: 'progress-bar__fill--brown',
      Utilities: 'progress-bar__fill--blue'
    };
    return colorMap[category] || 'progress-bar__fill--blue';
  }

  function navigateTo(pageName) {
    document.querySelectorAll('.page').forEach(page => page.classList.remove('page--active'));
    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('nav-item--active'));
    const targetPage = document.getElementById(`${pageName}-page`);
    if (targetPage) targetPage.classList.add('page--active');
    const targetNav = document.querySelector(`[data-page="${pageName}"]`);
    if (targetNav) targetNav.classList.add('nav-item--active');
    state.currentPage = pageName;
    if (pageName === 'dashboard') {
      setTimeout(() => { initIncomeExpensesChart(); initCategoryChart(); }, 100);
    }
    if (pageName === 'expenses') renderExpenses('allExpenses', state.expenses);
    if (pageName === 'subscriptions') renderSubscriptions();
    if (pageName === 'budget') renderBudgetOverview();
    if (pageName === 'savings') renderSavingsGoals();
  }

  function handleSetIncome() {
    const newIncome = prompt('Enter your monthly income:', state.monthlyIncome);
    if (newIncome && !isNaN(newIncome)) {
      state.monthlyIncome = parseFloat(newIncome);
      updateDashboardStats();
      initIncomeExpensesChart();
    }
  }

  function handleChatSend() {
    const input = document.getElementById('chatInput');
    const container = document.getElementById('chatContainer');
    if (!input || !container) return;
    const message = input.value.trim();
    if (!message) return;
    const userMessage = document.createElement('div');
    userMessage.style.cssText = 'margin-bottom: 12px; text-align: right;';
    userMessage.innerHTML = `<div style="display: inline-block; background: var(--color-primary); color: white; padding: 8px 12px; border-radius: 8px; max-width: 70%;">${message}</div>`;
    container.appendChild(userMessage);
    input.value = '';
    setTimeout(() => {
      const botMessage = document.createElement('div');
      botMessage.style.cssText = 'margin-bottom: 12px;';
      botMessage.innerHTML = `<div style="display: inline-block; background: var(--color-progress-bg); padding: 8px 12px; border-radius: 8px; max-width: 70%;">Based on your spending patterns, I recommend allocating more budget to savings. Your current savings rate of ${calculateStats().savingsRate}% is excellent!</div>`;
      container.appendChild(botMessage);
      container.scrollTop = container.scrollHeight;
    }, 1000);
    container.scrollTop = container.scrollHeight;
  }

  async function init() {
    await loadBudgets();
    updateDashboardStats();
    initIncomeExpensesChart();
    initCategoryChart();
    renderExpenses('recentExpenses', state.expenses.slice(0, 5));
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', function(e) {
        e.preventDefault();
        const page = this.getAttribute('data-page');
        if (page) navigateTo(page);
      });
    });
    const setIncomeBtn = document.getElementById('setIncomeBtn');
    if (setIncomeBtn) setIncomeBtn.addEventListener('click', handleSetIncome);
    const sendChatBtn = document.getElementById('sendChatBtn');
    if (sendChatBtn) sendChatBtn.addEventListener('click', handleChatSend);
    const chatInput = document.getElementById('chatInput');
    if (chatInput) chatInput.addEventListener('keypress', function(e) { if (e.key === 'Enter') handleChatSend(); });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();