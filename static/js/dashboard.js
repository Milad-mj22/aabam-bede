/* ============================================
   Dashboard — Charts
   ============================================ */

(function () {
    'use strict';

    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: 'rgba(255, 255, 255, 0.85)',
                    font: { family: 'Vazirmatn', size: 12 },
                    boxWidth: 12,
                    padding: 10,
                },
            },
            tooltip: {
                backgroundColor: 'rgba(15, 23, 42, 0.95)',
                titleColor: '#fff',
                bodyColor: '#fff',
                borderColor: 'rgba(255, 255, 255, 0.2)',
                borderWidth: 1,
                padding: 10,
                cornerRadius: 8,
                titleFont: { family: 'Vazirmatn' },
                bodyFont: { family: 'Vazirmatn' },
            },
        },
        scales: {
            x: {
                ticks: {
                    color: 'rgba(255, 255, 255, 0.7)',
                    font: { family: 'Vazirmatn', size: 11 },
                },
                grid: {
                    color: 'rgba(255, 255, 255, 0.08)',
                },
            },
            y: {
                beginAtZero: true,
                ticks: {
                    color: 'rgba(255, 255, 255, 0.7)',
                    font: { family: 'Vazirmatn', size: 11 },
                    precision: 0,
                },
                grid: {
                    color: 'rgba(255, 255, 255, 0.08)',
                },
            },
        },
    };

    fetch('/api/charts/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
    })
        .then(r => r.json())
        .then(data => {
            renderActivityChart(data.activity);
            renderStatusChart(data.plant_status);
            renderCareChart(data.care_distribution);
        })
        .catch(err => {
            console.error('خطا در بارگذاری چارت‌ها:', err);
        });

    // ============================================
    //  Activity Line Chart
    // ============================================
    function renderActivityChart(data) {
        const ctx = document.getElementById('activityChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'آبیاری',
                        data: data.watering,
                        borderColor: '#06b6d4',
                        backgroundColor: 'rgba(6, 182, 212, 0.15)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 2,
                        pointRadius: 3,
                        pointHoverRadius: 6,
                    },
                    {
                        label: 'کوددهی',
                        data: data.fertilizer,
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.15)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 2,
                        pointRadius: 3,
                        pointHoverRadius: 6,
                    },
                    {
                        label: 'دارو',
                        data: data.medicine,
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.15)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 2,
                        pointRadius: 3,
                        pointHoverRadius: 6,
                    },
                    {
                        label: 'سایر',
                        data: data.other,
                        borderColor: '#8b5cf6',
                        backgroundColor: 'rgba(139, 92, 246, 0.15)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 2,
                        pointRadius: 3,
                        pointHoverRadius: 6,
                    },
                ],
            },
            options: commonOptions,
        });
    }

    // ============================================
    //  Status Doughnut Chart
    // ============================================
    function renderStatusChart(data) {
        const ctx = document.getElementById('statusChart');
        if (!ctx) return;

        const total = data.values.reduce((a, b) => a + b, 0);

        if (total === 0) {
            ctx.parentElement.innerHTML = `
                <div class="empty-state" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <i class="bi bi-pie-chart"></i>
                    <div class="small">گیاهی برای نمایش نیست</div>
                </div>
            `;
            return;
        }

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: data.colors,
                    borderColor: 'rgba(255, 255, 255, 0.15)',
                    borderWidth: 2,
                    hoverOffset: 8,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: 'rgba(255, 255, 255, 0.85)',
                            font: { family: 'Vazirmatn', size: 11 },
                            padding: 8,
                            boxWidth: 10,
                        },
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.95)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        padding: 10,
                        cornerRadius: 8,
                        titleFont: { family: 'Vazirmatn' },
                        bodyFont: { family: 'Vazirmatn' },
                        callbacks: {
                            label: function (context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const pct = ((context.parsed / total) * 100).toFixed(1);
                                return ` ${context.label}: ${context.parsed} (${pct}%)`;
                            },
                        },
                    },
                },
            },
        });
    }

    // ============================================
    //  Care Distribution Bar Chart
    // ============================================
    function renderCareChart(data) {
        const ctx = document.getElementById('careChart');
        if (!ctx) return;

        if (!data.values.length) {
            ctx.parentElement.innerHTML = `
                <div class="empty-state" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <i class="bi bi-bar-chart"></i>
                    <div class="small">داده‌ای برای نمایش نیست</div>
                </div>
            `;
            return;
        }

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'تعداد',
                    data: data.values,
                    backgroundColor: data.colors.map(c => c + '90'),
                    borderColor: data.colors,
                    borderWidth: 2,
                    borderRadius: 8,
                    hoverBackgroundColor: data.colors,
                }],
            },
            options: {
                ...commonOptions,
                indexAxis: 'y',
                plugins: {
                    ...commonOptions.plugins,
                    legend: { display: false },
                },
                scales: {
                    ...commonOptions.scales,
                    x: {
                        ...commonOptions.scales.x,
                        beginAtZero: true,
                    },
                },
            },
        });
    }

})();