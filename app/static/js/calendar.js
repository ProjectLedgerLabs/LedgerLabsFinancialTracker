// Calendar Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Month navigation
    const prevBtn = document.getElementById('prevMonth');
    const nextBtn = document.getElementById('nextMonth');
    
    if (prevBtn || nextBtn) {
        // Get current year and month from URL
        const params = new URLSearchParams(window.location.search);
        const currentYear = parseInt(params.get('year')) || new Date().getFullYear();
        const currentMonth = parseInt(params.get('month')) || new Date().getMonth() + 1;
        
        if (prevBtn) {
            prevBtn.addEventListener('click', function() {
                let year = currentYear;
                let month = currentMonth - 1;
                if (month < 1) {
                    month = 12;
                    year -= 1;
                }
                window.location.href = `/calendar/?year=${year}&month=${month}`;
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', function() {
                let year = currentYear;
                let month = currentMonth + 1;
                if (month > 12) {
                    month = 1;
                    year += 1;
                }
                window.location.href = `/calendar/?year=${year}&month=${month}`;
            });
        }
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