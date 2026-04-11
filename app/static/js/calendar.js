// Calendar Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Toggle sidebar
    const toggleBtn = document.getElementById('menu-toggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('collapsed');
        });
    }
    
    // Add click handlers to calendar events
    const calendarEvents = document.querySelectorAll('.calendar-event');
    calendarEvents.forEach(function(eventEl) {
        eventEl.addEventListener('click', function(e) {
            e.stopPropagation();
            const title = this.querySelector('.event-title')?.textContent || '';
            showEventDetails(title);
        });
    });
    
    // Show event details
    function showEventDetails(title) {
        alert('Event: ' + title);
    }
    
    // Refresh events button
    const refreshBtn = document.getElementById('refreshEventsBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async function() {
            try {
                const response = await fetch('/calendar/api/upcoming?days=14');
                if (response.ok) {
                    const data = await response.json();
                    const container = document.querySelector('.upcoming-events-list');
                    if (container && data.events) {
                        container.innerHTML = '';
                        if (data.events.length === 0) {
                            container.innerHTML = '<div class="text-center text-muted py-4">No upcoming events</div>';
                        } else {
                            data.events.forEach(function(event) {
                                const eventDate = new Date(event.date);
                                const formattedDate = eventDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                                
                                let badgeClass = 'danger';
                                let icon = 'shopping_cart';
                                if (event.type === 'subscription') {
                                    badgeClass = 'warning';
                                    icon = 'subscriptions';
                                } else if (event.type === 'bill') {
                                    badgeClass = 'info';
                                    icon = 'receipt';
                                } else if (event.type === 'income') {
                                    badgeClass = 'success';
                                    icon = 'attach_money';
                                }
                                
                                const eventDiv = document.createElement('div');
                                eventDiv.className = 'upcoming-event-item';
                                eventDiv.innerHTML = `
                                    <div class="event-date">${formattedDate}</div>
                                    <div class="event-info">
                                        <span class="material-symbols-outlined event-icon">${icon}</span>
                                        <span class="event-title">${event.title}</span>
                                    </div>
                                    <div class="event-amount text-${badgeClass}">$${event.amount.toFixed(2)}</div>
                                `;
                                container.appendChild(eventDiv);
                            });
                        }
                    }
                }
            } catch (error) {
                console.error('Error refreshing events:', error);
            }
        });
    }
});