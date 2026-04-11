def get_sidebar_html(active_page: str = "dashboard"):
    """Return the sidebar HTML with the active page highlighted"""
    
    nav_items = [
        {"name": "Dashboard", "path": "/finance/dashboard", "icon": "dashboard", "id": "dashboard"},
        {"name": "Expenses", "path": "/expenses/", "icon": "receipt", "id": "expenses"},
        {"name": "Subscriptions", "path": "/subscriptions/", "icon": "subscriptions", "id": "subscriptions"},
        {"name": "Budget", "path": "/budget/", "icon": "account_balance", "id": "budget"},
        {"name": "Reports", "path": "/reports/", "icon": "bar_chart", "id": "reports"},
        {"name": "Savings", "path": "/savings/", "icon": "savings", "id": "savings"},
        {"name": "Calendar", "path": "/calendar/", "icon": "calendar_month", "id": "calendar"},
        {"name": "Users", "path": "/app", "icon": "people", "id": "users"},
    ]
    
    html = '<ul class="nav nav-pills flex-column gap-2 flex-grow-1">'
    
    for item in nav_items:
        active_class = 'active' if active_page == item["id"] else ''
        html += f'''
            <li class="nav-item">
                <a class="nav-link d-flex align-items-center {active_class}" href="{item['path']}">
                    <span class="material-symbols-outlined me-2">{item['icon']}</span>
                    {item['name']}
                </a>
            </li>
        '''
    
    html += '''
            <li class="nav-item mt-auto">
                <a class="nav-link d-flex align-items-center text-danger" href="/logout">
                    <span class="material-symbols-outlined me-2">logout</span>
                    Logout
                </a>
            </li>
        </ul>
    '''
    
    return html