// Wait for page to load
document.addEventListener('DOMContentLoaded', function() {
  
  // ========== DATA ==========
  let monthlyIncome = 5000;
  
  let allExpenses = [
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
  ];
  
  let subscriptions = [
    { name: 'Netflix', amount: 15.99, nextBilling: '2026-05-01', category: 'Entertainment' },
    { name: 'Spotify', amount: 9.99, nextBilling: '2026-05-01', category: 'Entertainment' },
    { name: 'Gym Membership', amount: 49.99, nextBilling: '2026-05-01', category: 'Health' },
    { name: 'Cloud Storage', amount: 5.00, nextBilling: '2026-05-15', category: 'Software' }
  ];
  
  let savingsGoals = [
    { name: 'Emergency Fund', target: 10000, current: 3500 },
    { name: 'Vacation', target: 3000, current: 1200 },
    { name: 'New Car', target: 15000, current: 5000 }
  ];
  
  let budgetLimits = {
    Food: 600,
    Transportation: 300,
    Entertainment: 200,
    Health: 150,
    Software: 100,
    Utilities: 200
  };
  
  // Chart variables
  let incomeChart = null;
  let categoryChart = null;
  
  // ========== HELPER FUNCTIONS ==========
  
  // Calculate total expenses
  function getTotalExpenses() {
    let total = 0;
    for (let i = 0; i < allExpenses.length; i++) {
      total = total + allExpenses[i].amount;
    }
    return total;
  }
  
  // Calculate spending by category
  function getCategorySpending() {
    let categories = {};
    for (let i = 0; i < allExpenses.length; i++) {
      let cat = allExpenses[i].category;
      let amount = allExpenses[i].amount;
      if (categories[cat]) {
        categories[cat] = categories[cat] + amount;
      } else {
        categories[cat] = amount;
      }
    }
    return categories;
  }
  
  // Calculate budget spent amounts
  function getBudgetSpent() {
    let spending = getCategorySpending();
    let budgetSpent = {};
    
    for (let category in budgetLimits) {
      budgetSpent[category] = spending[category] || 0;
    }
    return budgetSpent;
  }
  
  // Update dashboard numbers
  function updateDashboardStats() {
    let totalExpenses = getTotalExpenses();
    let burnRate = monthlyIncome - totalExpenses;
    let savingsRate = ((burnRate / monthlyIncome) * 100).toFixed(1);
    
    document.getElementById('monthlyIncome').innerHTML = '$' + monthlyIncome.toFixed(2);
    document.getElementById('totalExpenses').innerHTML = '$' + totalExpenses.toFixed(2);
    document.getElementById('burnRate').innerHTML = '$' + burnRate.toFixed(2);
    document.getElementById('savingsRate').innerHTML = savingsRate + '%';
  }
  
  // Render all expenses on Expenses page
  function renderAllExpenses() {
    let container = document.getElementById('allExpenses');
    if (!container) return;
    
    container.innerHTML = '';
    
    for (let i = 0; i < allExpenses.length; i++) {
      let expense = allExpenses[i];
      let expenseDiv = document.createElement('div');
      expenseDiv.className = 'expense-row';
      expenseDiv.innerHTML = `
        <div>
          <h4>${expense.name}</h4>
          <p>${expense.category} • ${expense.date}</p>
        </div>
        <div class="expense-amount">-$${expense.amount.toFixed(2)}</div>
      `;
      container.appendChild(expenseDiv);
    }
  }
  
  // Render subscriptions
  function renderSubscriptions() {
    let container = document.getElementById('subscriptionList');
    if (!container) return;
    
    container.innerHTML = '';
    
    for (let i = 0; i < subscriptions.length; i++) {
      let sub = subscriptions[i];
      let subDiv = document.createElement('div');
      subDiv.className = 'subscription-item';
      subDiv.innerHTML = `
        <div>
          <h4>${sub.name}</h4>
          <p style="font-size: 12px; color: #6b635c;">${sub.category} • Next: ${sub.nextBilling}</p>
        </div>
        <div><strong>$${sub.amount.toFixed(2)}/mo</strong></div>
      `;
      container.appendChild(subDiv);
    }
  }
  
  // Render budget overview
  function renderBudgetOverview() {
    let container = document.getElementById('budgetOverview');
    if (!container) return;
    
    let spent = getBudgetSpent();
    container.innerHTML = '';
    
    for (let category in budgetLimits) {
      let limit = budgetLimits[category];
      let spentAmount = spent[category];
      let percent = (spentAmount / limit) * 100;
      
      // Pick color class
      let colorClass = 'blue-fill';
      if (category === 'Transportation') colorClass = 'teal-fill';
      if (category === 'Entertainment') colorClass = 'sky-fill';
      if (category === 'Health') colorClass = 'orange-fill';
      if (category === 'Software') colorClass = 'brown-fill';
      
      let budgetDiv = document.createElement('div');
      budgetDiv.className = 'budget-row';
      budgetDiv.innerHTML = `
        <div class="budget-label">${category}</div>
        <div class="budget-numbers">$${spentAmount.toFixed(2)} / $${limit}</div>
        <div class="progress-bar">
          <div class="progress-fill ${colorClass}" style="width: ${percent}%"></div>
        </div>
      `;
      container.appendChild(budgetDiv);
    }
  }
  
  // Render savings goals
  function renderSavingsGoals() {
    let container = document.getElementById('savingsGoals');
    if (!container) return;
    
    container.innerHTML = '';
    
    for (let i = 0; i < savingsGoals.length; i++) {
      let goal = savingsGoals[i];
      let percent = (goal.current / goal.target) * 100;
      
      let goalDiv = document.createElement('div');
      goalDiv.className = 'savings-item';
      goalDiv.innerHTML = `
        <div style="flex: 1;">
          <h4>${goal.name}</h4>
          <p style="font-size: 12px; color: #6b635c; margin: 8px 0;">$${goal.current.toFixed(2)} of $${goal.target.toFixed(2)}</p>
          <div class="progress-bar">
            <div class="progress-fill blue-fill" style="width: ${percent}%"></div>
          </div>
        </div>
        <div><strong>${percent.toFixed(0)}%</strong></div>
      `;
      container.appendChild(goalDiv);
    }
  }
  
  // ========== CHARTS ==========
  
  function initIncomeExpensesChart() {
    let canvas = document.getElementById('incomeExpensesChart');
    if (!canvas) return;
    
    let ctx = canvas.getContext('2d');
    
    let monthlyExpenses = [450, 520, 380, 465];
    let monthlyIncomeData = [5000, 5000, 5000, 5000];
    let months = ['Jan', 'Feb', 'Mar', 'Apr'];
    
    if (incomeChart) {
      incomeChart.destroy();
    }
    
    incomeChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: months,
        datasets: [
          {
            label: 'Income',
            data: monthlyIncomeData,
            borderColor: '#2c5f8d',
            backgroundColor: 'rgba(44, 95, 141, 0.1)',
            fill: true,
            tension: 0.4
          },
          {
            label: 'Expenses',
            data: monthlyExpenses,
            borderColor: '#c4846b',
            backgroundColor: 'rgba(196, 132, 107, 0.1)',
            fill: true,
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          tooltip: {
            callbacks: {
              label: function(context) {
                return context.dataset.label + ': $' + context.raw;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return '$' + value;
              }
            }
          }
        }
      }
    });
  }
  
  function initCategoryChart() {
    let canvas = document.getElementById('categoryChart');
    if (!canvas) return;
    
    let ctx = canvas.getContext('2d');
    let spending = getCategorySpending();
    
    let categories = Object.keys(spending);
    let amounts = Object.values(spending);
    let colors = ['#2c5f8d', '#5a9fc9', '#8db9d9', '#c4846b', '#9a7b6b', '#6b8ea3'];
    
    if (categoryChart) {
      categoryChart.destroy();
    }
    
    categoryChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: categories,
        datasets: [{
          data: amounts,
          backgroundColor: colors.slice(0, categories.length),
          borderWidth: 2,
          borderColor: '#fff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          tooltip: {
            callbacks: {
              label: function(context) {
                return context.label + ': $' + context.raw.toFixed(2);
              }
            }
          }
        }
      }
    });
  }
  
  // ========== PAGE NAVIGATION ==========
  
  function showPage(pageName) {
    // Hide all pages
    let allPages = document.querySelectorAll('.page');
    for (let i = 0; i < allPages.length; i++) {
      allPages[i].classList.remove('active-page');
    }
    
    // Remove active class from all nav links
    let allNavLinks = document.querySelectorAll('.nav-link');
    for (let i = 0; i < allNavLinks.length; i++) {
      allNavLinks[i].classList.remove('active');
    }
    
    // Show selected page
    let selectedPage = document.getElementById(pageName + '-page');
    if (selectedPage) {
      selectedPage.classList.add('active-page');
    }
    
    // Add active class to clicked nav link
    let activeLink = document.querySelector('[data-page="' + pageName + '"]');
    if (activeLink) {
      activeLink.classList.add('active');
    }
    
    // Refresh charts when going to dashboard
    if (pageName === 'dashboard') {
      setTimeout(function() {
        initIncomeExpensesChart();
        initCategoryChart();
      }, 100);
    }
    
    // Load data for specific pages
    if (pageName === 'expenses') {
      renderAllExpenses();
    }
    
    if (pageName === 'subscriptions') {
      renderSubscriptions();
    }
    
    if (pageName === 'budget') {
      renderBudgetOverview();
    }
    
    if (pageName === 'savings') {
      renderSavingsGoals();
    }
  }
  
  // ========== EVENT HANDLERS ==========
  
  // Set income button
  let setIncomeBtn = document.getElementById('setIncomeBtn');
  if (setIncomeBtn) {
    setIncomeBtn.addEventListener('click', function() {
      let newIncome = prompt('Enter your monthly income:', monthlyIncome);
      if (newIncome && !isNaN(newIncome)) {
        monthlyIncome = parseFloat(newIncome);
        updateDashboardStats();
        initIncomeExpensesChart();
      }
    });
  }
  
  // Navigation clicks
  let navLinks = document.querySelectorAll('.nav-link');
  for (let i = 0; i < navLinks.length; i++) {
    navLinks[i].addEventListener('click', function(e) {
      e.preventDefault();
      let page = this.getAttribute('data-page');
      if (page) {
        showPage(page);
      }
    });
  }
  
  // Chat functionality
  let sendBtn = document.getElementById('sendChatBtn');
  let chatInput = document.getElementById('chatInput');
  let chatContainer = document.getElementById('chatContainer');
  
  function sendChatMessage() {
    if (!chatInput || !chatContainer) return;
    
    let message = chatInput.value.trim();
    if (message === '') return;
    
    // Add user message
    let userDiv = document.createElement('div');
    userDiv.style.textAlign = 'right';
    userDiv.style.marginBottom = '12px';
    userDiv.innerHTML = '<div style="display: inline-block; background: #2c5f8d; color: white; padding: 8px 12px; border-radius: 8px; max-width: 70%;">' + message + '</div>';
    chatContainer.appendChild(userDiv);
    
    // Clear input
    chatInput.value = '';
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    // Bot response after 1 second
    setTimeout(function() {
      let totalExp = getTotalExpenses();
      let savingsRate = ((monthlyIncome - totalExp) / monthlyIncome * 100).toFixed(1);
      
      let botDiv = document.createElement('div');
      botDiv.style.marginBottom = '12px';
      botDiv.innerHTML = '<div style="display: inline-block; background: #e8e4df; padding: 8px 12px; border-radius: 8px; max-width: 70%;">Based on your spending, your savings rate is ' + savingsRate + '%. Keep up the good work!</div>';
      chatContainer.appendChild(botDiv);
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 1000);
  }
  
  if (sendBtn) {
    sendBtn.addEventListener('click', sendChatMessage);
  }
  
  if (chatInput) {
    chatInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        sendChatMessage();
      }
    });
  }
  
  // ========== INITIAL LOAD ==========
  updateDashboardStats();
  initIncomeExpensesChart();
  initCategoryChart();
  
  // Show first 5 expenses on dashboard
  let recentContainer = document.getElementById('recentExpenses');
  if (recentContainer) {
    recentContainer.innerHTML = '';
    for (let i = 0; i < 5; i++) {
      let exp = allExpenses[i];
      let expDiv = document.createElement('div');
      expDiv.className = 'expense-row';
      expDiv.innerHTML = `
        <div>
          <h4>${exp.name}</h4>
          <p>${exp.category} • ${exp.date}</p>
        </div>
        <div class="expense-amount">-$${exp.amount.toFixed(2)}</div>
      `;
      recentContainer.appendChild(expDiv);
    }
  }
  
});