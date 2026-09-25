/* ============================================
   PlantCare - Main JS
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {

    // ============================================
    // Auto-hide alerts after 5 seconds
    // ============================================
    document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // ============================================
    // Password visibility toggle
    // ============================================
    document.querySelectorAll('.password-toggle').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const input = this.parentElement.querySelector('input');
            const icon = this.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('bi-eye');
                icon.classList.add('bi-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('bi-eye-slash');
                icon.classList.add('bi-eye');
            }
        });
    });

    // ============================================
    // Confirm delete buttons
    // ============================================
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            if (!confirm(this.dataset.confirm || 'آیا مطمئن هستید؟')) {
                e.preventDefault();
                return false;
            }
        });
    });

    // ============================================
    // Add fade-up animation to cards
    // ============================================
    document.querySelectorAll('.glass-card, .plant-card, .stat-card').forEach(function (card, i) {
        card.classList.add('animate-fade-up');
        card.style.animationDelay = (i * 0.05) + 's';
    });

    // ============================================
    // Tooltips (Bootstrap)
    // ============================================
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function (el) {
        return new bootstrap.Tooltip(el);
    });

});