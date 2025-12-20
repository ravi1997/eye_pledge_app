
document.addEventListener('DOMContentLoaded', () => {
    // Chart Configuration
    Chart.defaults.font.family = "'Inter', system-ui, -apple-system, sans-serif";
    Chart.defaults.color = '#64748b'; // slate-500

    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: 'rgba(15, 23, 42, 0.9)', // slate-900
                padding: 12,
                titleFont: { size: 13, weight: '600', family: "'Inter', sans-serif" },
                bodyFont: { size: 12, family: "'Inter', sans-serif" },
                cornerRadius: 8,
                displayColors: false
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: { color: '#f1f5f9', drawBorder: false }, // slate-100
                ticks: { font: { size: 11 } }
            },
            x: {
                grid: { display: false },
                ticks: { font: { size: 11 } }
            }
        },
        animation: {
            duration: 1000,
            easing: 'easeOutQuart'
        }
    };

    // Helper: Fetch Data
    async function fetchData(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Fetch error:', error);
            return null;
        }
    }

    // 1. Load Summary Stats (Cards)
    async function loadSummaryStats() {
        const data = await fetchData('/api/stats/summary');
        if (data) {
            const totalEl = document.getElementById('totalPledges');
            const todayEl = document.getElementById('todayPledges');

            if (totalEl) totalEl.innerText = data.total_pledges;
            if (todayEl) todayEl.innerText = data.today_pledges;
            // Optionally update avg/day if ID exists, currently static in template
        }
    }

    // 2. Load Monthly Chart
    async function loadMonthlyChart() {
        const data = await fetchData('/api/stats/monthly');
        const element = document.getElementById('monthlyChart');
        if (data && element) {
            const ctx = element.getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Pledges',
                        data: data.data,
                        backgroundColor: '#2563eb',
                        borderRadius: 6,
                        hoverBackgroundColor: '#1d4ed8'
                    }]
                },
                options: {
                    ...commonOptions,
                    plugins: {
                        ...commonOptions.plugins,
                        tooltip: {
                            ...commonOptions.plugins.tooltip,
                            callbacks: { label: (c) => ` ${c.parsed.y} Pledges` }
                        }
                    }
                }
            });
        }
    }

    // 3. Load Weekly Chart
    async function loadWeeklyChart() {
        const data = await fetchData('/api/stats/weekly');
        const element = document.getElementById('weeklyChart');
        if (data && element) {
            const ctx = element.getContext('2d');
            const gradient = ctx.createLinearGradient(0, 0, 0, 300);
            gradient.addColorStop(0, 'rgba(59, 130, 246, 0.2)');
            gradient.addColorStop(1, 'rgba(59, 130, 246, 0)');

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Daily',
                        data: data.data,
                        borderColor: '#3b82f6',
                        backgroundColor: gradient,
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: '#ffffff',
                        pointBorderColor: '#3b82f6',
                        pointBorderWidth: 2,
                        pointRadius: 4
                    }]
                },
                options: commonOptions
            });
        }
    }

    // 4. Load Yearly Chart
    async function loadYearlyChart() {
        const data = await fetchData('/api/stats/yearly');
        const element = document.getElementById('yearlyChart');
        if (data && element) {
            const ctx = element.getContext('2d');
            const gradient = ctx.createLinearGradient(0, 0, 0, 300);
            gradient.addColorStop(0, 'rgba(168, 85, 247, 0.2)');
            gradient.addColorStop(1, 'rgba(168, 85, 247, 0)');

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Total',
                        data: data.data,
                        borderColor: '#a855f7',
                        backgroundColor: gradient,
                        borderWidth: 3,
                        tension: 0.3,
                        fill: true,
                        pointBackgroundColor: '#ffffff',
                        pointBorderColor: '#a855f7',
                        pointBorderWidth: 2,
                        pointRadius: 4
                    }]
                },
                options: commonOptions
            });
        }
    }

    // 5. Load Top States
    async function loadTopStates() {
        const data = await fetchData('/api/stats/states');
        const container = document.getElementById('topStatesList');
        if (data && container) {
            container.innerHTML = ''; // Clear loading state

            if (data.length === 0) {
                container.innerHTML = '<div class="text-center text-slate-500 py-4">No data available</div>';
                return;
            }

            data.forEach((item, index) => {
                const [state, count] = item;
                const rank = index + 1;

                // Styling logic matching the Jinja template
                let trophyColor = 'bg-white text-slate-400';
                let icon = `#${rank}`;
                let rowBg = 'bg-slate-50 border border-slate-100';
                let badgeColor = 'text-brand-600';

                if (rank === 1) {
                    trophyColor = 'bg-amber-100 text-amber-600';
                    icon = '<i class="bi bi-trophy-fill text-xs"></i>';
                    rowBg = 'bg-amber-50 border border-amber-100';
                    badgeColor = 'text-amber-600';
                } else if (rank === 2) {
                    trophyColor = 'bg-slate-200 text-slate-600';
                    icon = '<i class="bi bi-trophy-fill text-xs"></i>';
                } else if (rank === 3) {
                    trophyColor = 'bg-orange-100 text-orange-600';
                    icon = '<i class="bi bi-trophy-fill text-xs"></i>';
                }

                const html = `
                    <div class="flex items-center justify-between p-3 rounded-xl ${rowBg} hover:shadow-sm transition-all group animate-enter" style="animation-delay: ${index * 100}ms">
                        <div class="flex items-center gap-3">
                            <div class="w-8 h-8 flex items-center justify-center rounded-lg ${trophyColor} font-bold text-sm">
                                ${icon}
                            </div>
                            <span class="font-semibold text-slate-700 group-hover:text-slate-900">${state}</span>
                        </div>
                        <span class="font-bold ${badgeColor} bg-white px-2 py-1 rounded-md text-sm shadow-sm border border-slate-100">${count}</span>
                    </div>
                `;
                container.insertAdjacentHTML('beforeend', html);
            });
        }
    }

    // 6. Demographics
    async function loadDemographics() {
        const data = await fetchData('/api/stats/demographics');

        // Age Chart
        const ageEl = document.getElementById('ageChart');
        if (data && ageEl) {
            new Chart(ageEl.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: data.age.labels,
                    datasets: [{
                        data: data.age.data,
                        backgroundColor: ['#60a5fa', '#3b82f6', '#2563eb', '#1d4ed8', '#1e40af'],
                        borderWidth: 0,
                        hoverOffset: 4
                    }]
                },
                options: {
                    ...commonOptions,
                    cutout: '70%',
                    // scales: { display: false }, // Removed to fix console error
                    plugins: {
                        legend: {
                            display: true,
                            position: 'right',
                            labels: { usePointStyle: true, boxWidth: 8, padding: 15, font: { size: 11 } }
                        }
                    }
                }
            });
        }

        // Gender Chart (if element exists, added for completeness)
        const genderEl = document.getElementById('genderChart');
        if (data && genderEl) {
            new Chart(genderEl.getContext('2d'), {
                type: 'pie',
                data: {
                    labels: data.gender.labels,
                    datasets: [{
                        data: data.gender.data,
                        backgroundColor: ['#3b82f6', '#ec4899', '#10b981'],
                        borderWidth: 0
                    }]
                },
                options: {
                    ...commonOptions,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });
        }
    }

    // 7. Hourly Activity
    async function loadHourlyChart() {
        const data = await fetchData('/api/stats/hourly');
        const element = document.getElementById('hourlyChart');
        if (data && element) {
            new Chart(element.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: '#14b8a6',
                        borderRadius: 4
                    }]
                },
                options: {
                    ...commonOptions,
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: {
                                font: { size: 10 },
                                callback: function (val, index) {
                                    // Show only every 4th label to avoid crowding
                                    return index % 4 === 0 ? this.getLabelForValue(val) : '';
                                }
                            }
                        },
                        y: { display: false }
                    }
                }
            });
        }
    }

    // Initialize all components
    loadSummaryStats();
    loadMonthlyChart();
    loadWeeklyChart();
    loadYearlyChart();
    loadDemographics();
    loadHourlyChart();

    // Auto-refresh summary only every 30s to be light
    setInterval(loadSummaryStats, 30000);
});
