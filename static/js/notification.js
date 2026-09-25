/* ============================================
   Notifications Widget
   ============================================ */

(function () {
    'use strict';

    const badge = document.getElementById('notifBadge');
    const list = document.getElementById('notifList');
    const markAllBtn = document.getElementById('markAllReadBtn');
    const dropdown = document.getElementById('notifDropdown');

    if (!dropdown) return;  // کاربر لاگین نیست

    let loaded = false;

    // ============================================
    //  آپدیت شمارنده
    // ============================================
    function updateBadge(count) {
        if (!badge) return;
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }

    function fetchCount() {
        fetch('/notifications/unread-count/', {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
        })
            .then(r => r.json())
            .then(data => updateBadge(data.count))
            .catch(() => {});
    }

    // ============================================
    //  بارگذاری لیست اخیر
    // ============================================
    function loadRecent() {
        if (loaded || !list) return;
        loaded = true;

        fetch('/notifications/recent/', {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
        })
            .then(r => r.json())
            .then(data => {
                renderList(data.notifications);
                updateBadge(data.unread_count);
            })
            .catch(() => {
                list.innerHTML = `
                    <div class="notif-empty">
                        <i class="bi bi-exclamation-triangle"></i>
                        <div>خطا در بارگذاری اطلاعیه‌ها</div>
                    </div>
                `;
            });
    }

    // ============================================
    //  رندر لیست
    // ============================================
    function renderList(items) {
        if (!list) return;

        if (!items || items.length === 0) {
            list.innerHTML = `
                <div class="notif-empty">
                    <i class="bi bi-bell-slash"></i>
                    <div>اطلاعیه‌ای ندارید</div>
                </div>
            `;
            return;
        }

        const html = items.map(n => `
            <div class="notification-item ${n.is_read ? '' : 'unread'}"
                 data-id="${n.id}"
                 data-url="${n.url}"
                 onclick="handleNotifClick(${n.id}, '${n.url}', ${n.is_read});">
                <div class="notification-icon"
                     style="border-color: ${n.priority_color}40;">
                    <span>${n.icon || '🔔'}</span>
                </div>
                <div class="notification-content">
                    <div class="notification-title">${escapeHtml(n.title)}</div>
                    <div class="notification-message">${escapeHtml(n.message)}</div>
                    <div class="notification-time">
                        <i class="bi bi-clock me-1"></i>${n.time_ago}
                    </div>
                </div>
            </div>
        `).join('');

        list.innerHTML = html;
    }

    // ============================================
    //  کلیک روی نوتیفیکیشن
    // ============================================
    window.handleNotifClick = function (id, url, isRead) {
        // علامت‌گذاری به‌عنوان خوانده‌شده
        fetch(`/notifications/${id}/read/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
            .then(r => r.json())
            .then(data => {
                if (data.unread_count !== undefined) {
                    updateBadge(data.unread_count);
                }
            })
            .catch(() => {});

        // ناوبری
        if (url && url !== '') {
            window.location.href = url;
        }
    };

    // ============================================
    //  علامت‌گذاری همه
    // ============================================
    if (markAllBtn) {
        markAllBtn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            fetch('/notifications/mark-all-read/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
                .then(r => r.json())
                .then(() => {
                    updateBadge(0);
                    loaded = false;
                    loadRecent();
                })
                .catch(() => {});
        });
    }

    // ============================================
    //  Helpers
    // ============================================
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // ============================================
    //  Events
    // ============================================
    dropdown.addEventListener('show.bs.dropdown', function () {
        if (!loaded) {
            loadRecent();
        }
    });

    // بارگذاری اولیه شمارنده
    fetchCount();

    // هر ۶۰ ثانیه یک‌بار شمارنده را آپدیت کن
    setInterval(fetchCount, 60000);

})();