from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List
from datetime import datetime
from app.routers.sidebar import get_sidebar_html
import json

router = APIRouter(prefix="/reports", tags=["reports"])

# Service Layer
class ReportsService:
    def __init__(self):
        # Monthly spending data (last 6 months)
        self.monthly_data = {
            "labels": ["Nov", "Dec", "Jan", "Feb", "Mar", "Apr"],
            "spending": [4200, 3800, 3433, 3100, 2950, 2800],
            "income": [5000, 5000, 5000, 5000, 5000, 5000]
        }
        
        self.category_data = {
            "Food": 258.57,
            "Transportation": 65.00,
            "Entertainment": 34.00,
            "Health": 49.99,
            "Software": 30.98,
            "Utilities": 180.00
        }
        
        self.subscriptions = [
            {"name": "Gym Membership", "amount": 49.99, "nextBilling": "2026-04-10"},
            {"name": "Software Subscription", "amount": 20.00, "nextBilling": "2026-04-12"},
            {"name": "Streaming Service A", "amount": 15.99, "nextBilling": "2026-04-15"},
            {"name": "Music Streaming", "amount": 9.99, "nextBilling": "2026-04-20"}
        ]
        
        self.current_month_spending = 2800.00
        self.previous_month_spending = 3100.00
        self.average_monthly_spending = 3433.33
        
        self.savings_data = {
            "total_saved": 9550.00,
            "total_target": 15500.00,
            "progress": 61.6
        }
    
    def get_monthly_trend(self) -> Dict:
        return self.monthly_data
    
    def get_category_breakdown(self) -> Dict:
        return self.category_data
    
    def get_subscription_summary(self) -> Dict:
        total_monthly = sum(sub["amount"] for sub in self.subscriptions)
        total_yearly = total_monthly * 12
        return {
            "monthly_cost": total_monthly,
            "yearly_projection": total_yearly,
            "active_services": len(self.subscriptions),
            "subscriptions": self.subscriptions
        }
    
    def get_spending_insights(self) -> Dict:
        month_over_month = ((self.current_month_spending - self.previous_month_spending) / self.previous_month_spending) * 100
        return {
            "current_month": self.current_month_spending,
            "previous_month": self.previous_month_spending,
            "average_monthly": self.average_monthly_spending,
            "month_over_month": round(month_over_month, 1),
            "is_decreasing": month_over_month < 0
        }
    
    def get_savings_summary(self) -> Dict:
        return self.savings_data
    
    def get_top_expense_categories(self, limit: int = 3) -> List[Dict]:
        sorted_categories = sorted(self.category_data.items(), key=lambda x: x[1], reverse=True)
        return [{"name": cat, "amount": amt} for cat, amt in sorted_categories[:limit]]

reports_service = ReportsService()

# Page Route

@router.get("/", response_class=HTMLResponse)
async def reports_page(request: Request):
    """Render the reports page with inline HTML"""
    
    username = "User"
    if hasattr(request, "session") and request.session:
        username = request.session.get("username", "User")
    
    monthly_data = reports_service.get_monthly_trend()
    category_data = reports_service.get_category_breakdown()
    subscription_summary = reports_service.get_subscription_summary()
    spending_insights = reports_service.get_spending_insights()
    savings_summary = reports_service.get_savings_summary()
    top_categories = reports_service.get_top_expense_categories()
    
    top_category_name = top_categories[0]['name'] if top_categories else 'None'
    top_category_amount = top_categories[0]['amount'] if top_categories else 0
    
    monthly_labels_json = json.dumps(monthly_data["labels"])
    monthly_spending_json = json.dumps(monthly_data["spending"])
    monthly_income_json = json.dumps(monthly_data["income"])
    category_labels_json = json.dumps(list(category_data.keys()))
    category_values_json = json.dumps(list(category_data.values()))
    

    top_categories_html = ""
    for cat in top_categories:
        top_categories_html += f'''
        <div class="top-category-item">
            <span>{cat["name"]}</span>
            <strong>${cat["amount"]:.2f}</strong>
        </div>
        '''
    
    subscriptions_html = ""
    for sub in subscription_summary["subscriptions"]:
        subscriptions_html += f'''
        <div class="subscription-item">
            <div>
                <h6 class="mb-0">{sub["name"]}</h6>
                <small class="text-muted">Next: {sub["nextBilling"]}</small>
            </div>
            <span class="fw-bold">${sub["amount"]:.2f}/mo</span>
        </div>
        '''
    sidebar_html = get_sidebar_html(active_page="reports")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FinancePlan - Financial Reports</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,100,1,200" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                overflow-x: hidden;
                background-color: #f8f9fa;
            }}
            
            #wrapper {{
                display: flex;
            }}
            
            #sidebar {{
                min-width: 250px;
                max-width: 250px;
                min-height: 100vh;
                transition: all 0.3s;
                background: #1b263b;
                color: #fff;
            }}
            
            #sidebar.collapsed {{
                margin-left: -250px;
            }}
            
            #sidebar .nav-link {{
                color: #adb5bd;
                font-weight: 500;
            }}
            
            #sidebar .nav-link:hover,
            #sidebar .nav-link.active {{
                color: #fff;
                background-color: #415a77;
                border-radius: 0.5rem;
            }}
            
            #sidebar .nav-link.active {{
                background-color: #0d6efd;
            }}
            
            #content {{
                width: 100%;
                padding: 1rem;
                transition: all 0.3s;
                display: flex;
                flex-direction: column;
                background-color: #f8f9fa;
            }}
            
            .stats-card {{
                background: white;
                border-radius: 12px;
                padding: 20px;
                display: flex;
                align-items: center;
                gap: 15px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }}
            
            .stats-card:hover {{
                transform: translateY(-3px);
            }}
            
            .stats-card-icon {{
                width: 50px;
                height: 50px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            
            .stats-card-icon.purple {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            
            .stats-card-icon.blue {{
                background: linear-gradient(135deg, #0d6efd 0%, #0dcaf0 100%);
                color: white;
            }}
            
            .stats-card-icon.green {{
                background: linear-gradient(135deg, #198754 0%, #20c997 100%);
                color: white;
            }}
            
            .stats-card-icon.orange {{
                background: linear-gradient(135deg, #fd7e14 0%, #ffc107 100%);
                color: white;
            }}
            
            .stats-card-icon .material-symbols-outlined {{
                font-size: 28px;
            }}
            
            .stats-card-content {{
                flex: 1;
            }}
            
            .stats-card-content small {{
                font-size: 12px;
                color: #6c757d;
                display: block;
            }}
            
            .stats-card-content h3 {{
                margin: 5px 0 0;
                font-size: 24px;
                font-weight: bold;
            }}
            
            .chart-container {{
                height: 300px;
                position: relative;
            }}
            
            .insight-item {{
                display: flex;
                align-items: flex-start;
                gap: 12px;
                padding: 12px 0;
                border-bottom: 1px solid #e9ecef;
            }}
            
            .insight-item:last-child {{
                border-bottom: none;
            }}
            
            .top-category-item {{
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid #f0f0f0;
            }}
            
            .subscription-summary {{
                text-align: center;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
            }}
            
            .subscriptions-list {{
                max-height: 300px;
                overflow-y: auto;
            }}
            
            .subscription-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px;
                border-bottom: 1px solid #e9ecef;
            }}
            
            .savings-stats {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                text-align: center;
                margin-bottom: 20px;
            }}
            
            .savings-stat h3 {{
                margin: 5px 0 0;
                font-size: 28px;
                font-weight: bold;
            }}
            
            .progress-bar-custom {{
                background-color: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
                height: 12px;
            }}
            
            .progress-fill {{
                height: 100%;
                border-radius: 10px;
                transition: width 0.5s ease;
            }}
            
            .card {{
                border: none;
                border-radius: 12px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            
            @media (max-width: 768px) {{
                #sidebar {{
                    transform: translateX(-100%);
                    position: fixed;
                    z-index: 1000;
                }}
                
                #sidebar.collapsed {{
                    transform: translateX(0);
                }}
                
                #content {{
                    margin-left: 0;
                }}
                
                .savings-stats {{
                    grid-template-columns: 1fr;
                }}
                
                .chart-container {{
                    height: 250px;
                }}
            }}
        </style>
    </head>
    <body>
        <div id="wrapper">
            {sidebar_html}
            
            <div id="content">
                <!-- Top Navbar -->
                <nav class="navbar navbar-expand-lg bg-white mb-4 px-3 rounded-3 shadow-sm">
                    <button class="btn btn-outline-secondary" id="menu-toggle">
                        <span class="material-symbols-outlined">menu</span>
                    </button>
                    <div class="ms-auto d-flex align-items-center gap-3">
                        <span class="fw-semibold">Welcome, {username}</span>
                    </div>
                </nav>
                
                <div class="container-fluid">
                    <!-- Header -->
                    <div class="mb-4">
                        <h1>Financial Reports</h1>
                        <p class="text-muted">Comprehensive analytics and insights</p>
                    </div>
                    
                    <!-- Stats Cards Row -->
                    <div class="row mb-4">
                        <div class="col-md-3">
                            <div class="stats-card">
                                <div class="stats-card-icon purple">
                                    <span class="material-symbols-outlined">payments</span>
                                </div>
                                <div class="stats-card-content">
                                    <small>This Month's Spending</small>
                                    <h3>${spending_insights['current_month']:.2f}</h3>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stats-card">
                                <div class="stats-card-icon blue">
                                    <span class="material-symbols-outlined">trending_up</span>
                                </div>
                                <div class="stats-card-content">
                                    <small>Avg. Monthly Spending</small>
                                    <h3>${spending_insights['average_monthly']:.2f}</h3>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stats-card">
                                <div class="stats-card-icon green">
                                    <span class="material-symbols-outlined">compare_arrows</span>
                                </div>
                                <div class="stats-card-content">
                                    <small>Month over Month</small>
                                    <h3 class="{'text-danger' if not spending_insights['is_decreasing'] else 'text-success'}">{spending_insights['month_over_month']:.1f}%</h3>
                                    <small>{'↓ Decreasing' if spending_insights['is_decreasing'] else '↑ Increasing'}</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stats-card">
                                <div class="stats-card-icon orange">
                                    <span class="material-symbols-outlined">subscriptions</span>
                                </div>
                                <div class="stats-card-content">
                                    <small>Active Subscriptions</small>
                                    <h3>${subscription_summary['monthly_cost']:.2f}</h3>
                                    <small>monthly</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Monthly Trend Chart -->
                    <div class="card mb-4">
                        <div class="card-header bg-white">
                            <h5 class="mb-0">6-Month Financial Trend</h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="trendChart"></canvas>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Two Column Layout -->
                    <div class="row mb-4">
                        <div class="col-lg-6">
                            <div class="card h-100">
                                <div class="card-header bg-white">
                                    <h5 class="mb-0">Spending by Category</h5>
                                </div>
                                <div class="card-body">
                                    <div class="chart-container">
                                        <canvas id="categoryChart"></canvas>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-lg-6">
                            <div class="card h-100">
                                <div class="card-header bg-white">
                                    <h5 class="mb-0">Spending Insights</h5>
                                </div>
                                <div class="card-body">
                                    <div class="insight-item">
                                        <span class="material-symbols-outlined text-warning">warning</span>
                                        <div>
                                            <strong>Top Spending Category</strong>
                                            <p class="mb-0">{top_category_name} (${top_category_amount:.2f})</p>
                                        </div>
                                    </div>
                                    <div class="insight-item">
                                        <span class="material-symbols-outlined text-success">trending_down</span>
                                        <div>
                                            <strong>Month-over-Month Change</strong>
                                            <p class="mb-0">{'Decreased' if spending_insights['is_decreasing'] else 'Increased'} by {abs(spending_insights['month_over_month']):.1f}%</p>
                                        </div>
                                    </div>
                                    <div class="insight-item">
                                        <span class="material-symbols-outlined text-info">savings</span>
                                        <div>
                                            <strong>Savings Progress</strong>
                                            <p class="mb-0">{savings_summary['progress']:.1f}% of goal achieved</p>
                                        </div>
                                    </div>
                                    <div class="mt-3">
                                        <h6>Top Spending Categories</h6>
                                        <div class="top-categories">
                                            {top_categories_html}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Subscriptions Section -->
                    <div class="card mb-4">
                        <div class="card-header bg-white">
                            <h5 class="mb-0">Active Subscriptions</h5>
                        </div>
                        <div class="card-body">
                            <div class="row mb-3">
                                <div class="col-md-4">
                                    <div class="subscription-summary">
                                        <small>Monthly Cost</small>
                                        <h4>${subscription_summary['monthly_cost']:.2f}</h4>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="subscription-summary">
                                        <small>Yearly Projection</small>
                                        <h4>${subscription_summary['yearly_projection']:.2f}</h4>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="subscription-summary">
                                        <small>Active Services</small>
                                        <h4>{subscription_summary['active_services']}</h4>
                                    </div>
                                </div>
                            </div>
                            <div class="subscriptions-list">
                                {subscriptions_html}
                            </div>
                        </div>
                    </div>
                    
                    <!-- Savings Goal Progress -->
                    <div class="card">
                        <div class="card-header bg-white">
                            <h5 class="mb-0">Savings Goal Progress</h5>
                        </div>
                        <div class="card-body">
                            <div class="savings-stats">
                                <div class="savings-stat">
                                    <small>Total Saved</small>
                                    <h3>${savings_summary['total_saved']:.2f}</h3>
                                </div>
                                <div class="savings-stat">
                                    <small>Total Target</small>
                                    <h3>${savings_summary['total_target']:.2f}</h3>
                                </div>
                                <div class="savings-stat">
                                    <small>Overall Progress</small>
                                    <h3>{savings_summary['progress']:.1f}%</h3>
                                </div>
                            </div>
                            <div class="progress-bar-custom mt-3">
                                <div class="progress-fill bg-success" style="width: {savings_summary['progress']:.1f}%;"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Pass data to JavaScript
            window.reportsData = {{
                monthlyLabels: {monthly_labels_json},
                monthlySpending: {monthly_spending_json},
                monthlyIncome: {monthly_income_json},
                categoryLabels: {category_labels_json},
                categoryValues: {category_values_json}
            }};
            
            let trendChart = null;
            let categoryChart = null;
            
            function initTrendChart() {{
                const canvas = document.getElementById('trendChart');
                if (!canvas) return;
                const ctx = canvas.getContext('2d');
                const data = window.reportsData || {{}};
                
                if (trendChart) trendChart.destroy();
                trendChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: data.monthlyLabels,
                        datasets: [
                            {{ label: 'Income', data: data.monthlyIncome, borderColor: '#0d6efd', backgroundColor: 'rgba(13, 110, 253, 0.1)', fill: true, tension: 0.4, borderWidth: 2 }},
                            {{ label: 'Expenses', data: data.monthlySpending, borderColor: '#fd7e14', backgroundColor: 'rgba(253, 126, 20, 0.1)', fill: true, tension: 0.4, borderWidth: 2 }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{ legend: {{ position: 'bottom' }}, tooltip: {{ callbacks: {{ label: function(context) {{ return context.dataset.label + ': $' + context.raw.toFixed(2); }} }} }} }},
                        scales: {{ y: {{ beginAtZero: true, ticks: {{ callback: function(value) {{ return '$' + value; }} }} }} }}
                    }}
                }});
            }}
            
            function initCategoryChart() {{
                const canvas = document.getElementById('categoryChart');
                if (!canvas) return;
                const ctx = canvas.getContext('2d');
                const data = window.reportsData || {{}};
                const colors = ['#0d6efd', '#20c997', '#0dcaf0', '#fd7e14', '#6c757d', '#d63384'];
                
                if (categoryChart) categoryChart.destroy();
                categoryChart = new Chart(ctx, {{
                    type: 'doughnut',
                    data: {{ labels: data.categoryLabels, datasets: [{{ data: data.categoryValues, backgroundColor: colors.slice(0, data.categoryLabels.length), borderWidth: 2, borderColor: '#fff' }}] }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'bottom' }}, tooltip: {{ callbacks: {{ label: function(context) {{ return context.label + ': $' + context.raw.toFixed(2); }} }} }} }} }}
                }});
            }}
            
            document.getElementById('menu-toggle')?.addEventListener('click', () => {{
                document.getElementById('sidebar').classList.toggle('collapsed');
            }});
            
            initTrendChart();
            initCategoryChart();
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


# API Routes

@router.get("/api/monthly-trend")
async def get_monthly_trend():
    return reports_service.get_monthly_trend()

@router.get("/api/category-breakdown")
async def get_category_breakdown():
    return reports_service.get_category_breakdown()

@router.get("/api/subscriptions")
async def get_subscriptions():
    return reports_service.get_subscription_summary()

@router.get("/api/spending-insights")
async def get_spending_insights():
    return reports_service.get_spending_insights()

@router.get("/api/savings-summary")
async def get_savings_summary():
    return reports_service.get_savings_summary()