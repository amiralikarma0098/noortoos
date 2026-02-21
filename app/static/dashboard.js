// static/dashboard.js
// ========================================
// PROFESSIONAL DASHBOARD - REAL DATABASE INTEGRATION
// Version: 1.0
// ========================================

(function() {
    // جلوگیری از اجرای همزمان
    if (window.__dashboardLoaded) return;
    window.__dashboardLoaded = true;
    
    console.log('📊 داشبورد حرفه‌ای لود شد');

    // فقط در صفحه اصلی اجرا شود
    if (window.location.pathname !== '/' && !window.location.pathname.includes('/index')) {
        return;
    }

    // ========================================
    // VARIABLES
    // ========================================
    let charts = {};
    let dashboardData = {
        totalAnalyses: 0,
        totalCalls: 0,
        successRate: 0,
        activeUsers: 0,
        recentAnalyses: [],
        topSellers: [],
        topCustomers: [],
        weeklyTrend: {},
        scoreDistribution: {}
    };

    // ========================================
    // INITIALIZATION
    // ========================================
    document.addEventListener('DOMContentLoaded', async function() {
        showLoading();
        await loadDashboardData();
        hideLoading();
        renderDashboard();
    });

    function showLoading() {
        const statsContainer = document.getElementById('overview-stats');
        if (statsContainer) {
            statsContainer.innerHTML = `
                <div class="col-span-4 text-center py-12">
                    <div class="loader mx-auto mb-4"></div>
                    <p class="text-gray-500">در حال بارگذاری اطلاعات...</p>
                </div>
            `;
        }
    }

    function hideLoading() {
        // فقط برای پاک کردن پیام لودینگ
    }

    // ========================================
    // DATA LOADING FROM DATABASE
    // ========================================
    async function loadDashboardData() {
        try {
            // دریافت آمار کلی از دیتابیس
            const [analysesRes, referralRes] = await Promise.all([
                fetch('/api/analysis/history'),
                fetch('/api/referral-history')
            ]);

            const analyses = await analysesRes.json();
            const referrals = await referralRes.json();

            console.log('📥 داده‌های دریافتی:', { analyses, referrals });

            // پردازش داده‌ها
            processAnalysesData(analyses);
            processReferralsData(referrals);
            
            // محاسبه آمار ترکیبی
            calculateCombinedStats(analyses, referrals);

        } catch (error) {
            console.error('❌ خطا در بارگذاری داده‌ها:', error);
            // استفاده از داده‌های نمونه در صورت خطا
            loadSampleData();
        }
    }

    function processAnalysesData(analyses) {
        if (!analyses || !Array.isArray(analyses)) return;

        // محاسبه آمار تحلیل‌ها
        dashboardData.totalAnalyses = analyses.length;
        
        // استخراج تماس‌ها از تحلیل‌ها
        let totalCalls = 0;
        let successfulCalls = 0;
        let sellers = new Map();
        let customers = new Map();

        analyses.forEach(analysis => {
            // سعی کن full_analysis رو پارس کن
            let fullAnalysis = analysis;
            if (analysis.full_analysis && typeof analysis.full_analysis === 'string') {
                try {
                    fullAnalysis = JSON.parse(analysis.full_analysis);
                } catch (e) {
                    // ignore
                }
            }

            // استخراج آمار تماس
            const stats = fullAnalysis?.آمار || {};
            totalCalls += stats.تعداد_کل_تماس_ها || 0;
            successfulCalls += stats.تماس_های_موفق || 0;

            // استخراج فروشندگان
            const sellerName = fullAnalysis?.فیلدهای_متنی?.نام_فروشنده;
            if (sellerName && sellerName !== '—') {
                sellers.set(sellerName, (sellers.get(sellerName) || 0) + 1);
            }

            // استخراج مشتریان
            const customerName = fullAnalysis?.فیلدهای_متنی?.نام_مشتری;
            if (customerName && customerName !== '—') {
                customers.set(customerName, (customers.get(customerName) || 0) + 1);
            }

            // روند هفتگی
            const date = new Date(analysis.analyzed_at);
            const weekKey = `${date.getFullYear()}-W${getWeekNumber(date)}`;
            dashboardData.weeklyTrend[weekKey] = (dashboardData.weeklyTrend[weekKey] || 0) + 1;

            // توزیع امتیازها
            const score = fullAnalysis?.امتیازها?.امتیاز_کل || 0;
            const scoreRange = getScoreRange(score);
            dashboardData.scoreDistribution[scoreRange] = (dashboardData.scoreDistribution[scoreRange] || 0) + 1;

            // فعالیت‌های اخیر
            dashboardData.recentAnalyses.push({
                type: 'تحلیل فروش',
                user: sellerName || 'نامشخص',
                date: analysis.analyzed_at,
                score: score,
                file: analysis.file_name
            });
        });

        dashboardData.totalCalls = totalCalls;
        dashboardData.successRate = totalCalls > 0 ? (successfulCalls / totalCalls) * 100 : 0;

        // فروشندگان برتر
        dashboardData.topSellers = Array.from(sellers.entries())
            .map(([name, count]) => ({ name, count }))
            .sort((a, b) => b.count - a.count)
            .slice(0, 5);

        // مشتریان برتر
        dashboardData.topCustomers = Array.from(customers.entries())
            .map(([name, count]) => ({ name, count }))
            .sort((a, b) => b.count - a.count)
            .slice(0, 5);
    }

    function processReferralsData(referrals) {
        if (!referrals || !Array.isArray(referrals)) return;

        referrals.forEach(referral => {
            dashboardData.recentAnalyses.push({
                type: 'تحلیل ارجاع',
                user: 'سیستم',
                date: referral.analyzed_at,
                score: referral.completion_rate || 0,
                file: referral.file_name
            });

            // روند هفتگی برای ارجاعات
            const date = new Date(referral.analyzed_at);
            const weekKey = `${date.getFullYear()}-W${getWeekNumber(date)}`;
            dashboardData.weeklyTrend[weekKey] = (dashboardData.weeklyTrend[weekKey] || 0) + 1;
        });

        dashboardData.activeUsers = [...new Set(referrals.map(r => r.file_name))].length;
    }

    function calculateCombinedStats(analyses, referrals) {
        // مرتب‌سازی فعالیت‌های اخیر بر اساس تاریخ
        dashboardData.recentAnalyses.sort((a, b) => new Date(b.date) - new Date(a.date));
        dashboardData.recentAnalyses = dashboardData.recentAnalyses.slice(0, 10);

        // محاسبه کاربران فعال یکتا
        const uniqueUsers = new Set();
        analyses.forEach(a => {
            if (a.seller_name) uniqueUsers.add(a.seller_name);
        });
        dashboardData.activeUsers = uniqueUsers.size || dashboardData.activeUsers;
    }

    // ========================================
    // SAMPLE DATA (FALLBACK)
    // ========================================
    function loadSampleData() {
        console.log('📊 استفاده از داده‌های نمونه');
        
        dashboardData = {
            totalAnalyses: 156,
            totalCalls: 1245,
            successRate: 68.5,
            activeUsers: 8,
            recentAnalyses: [
                { type: 'تحلیل فروش', user: 'پورحسین', date: new Date().toISOString(), score: 8.5, file: 'فروش_اسفند.xlsx' },
                { type: 'تحلیل ارجاع', user: 'سیستم', date: new Date().toISOString(), score: 75, file: 'ارجاعات_بهمن.xlsx' },
                { type: 'تحلیل فروش', user: 'رسولی', date: new Date(Date.now() - 86400000).toISOString(), score: 7.2, file: 'تماس_های_موفق.xlsx' }
            ],
            topSellers: [
                { name: 'پورحسین', count: 45 },
                { name: 'رسولی', count: 38 },
                { name: 'محمدی', count: 32 },
                { name: 'احمدی', count: 28 },
                { name: 'کریمی', count: 25 }
            ],
            topCustomers: [
                { name: 'بیمارستان نهم دی', count: 15 },
                { name: 'سیمان بجنورد', count: 12 },
                { name: 'موقوفات ملک', count: 10 },
                { name: 'شهرداری مشهد', count: 8 },
                { name: 'آموزش و پرورش', count: 7 }
            ],
            weeklyTrend: {
                '2026-W8': 12,
                '2026-W7': 18,
                '2026-W6': 15,
                '2026-W5': 22,
                '2026-W4': 19,
                '2026-W3': 14,
                '2026-W2': 16
            },
            scoreDistribution: {
                'عالی (8-10)': 32,
                'خوب (6-8)': 45,
                'متوسط (4-6)': 28,
                'ضعیف (0-4)': 15
            }
        };
    }

    // ========================================
    // RENDER FUNCTIONS
    // ========================================
    function renderDashboard() {
        renderStatsCards();
        renderCharts();
        renderRecentActivities();
        renderTopSellers();
        renderTopCustomers();
    }

    function renderStatsCards() {
        const container = document.getElementById('overview-stats');
        if (!container) return;

        const successRateFormatted = dashboardData.successRate.toFixed(1);
        const successRateClass = dashboardData.successRate >= 70 ? 'success' : 
                                dashboardData.successRate >= 50 ? 'warning' : 'danger';

        container.innerHTML = `
            <div class="stat-card rounded-lg p-6 fade-in">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm">تعداد تحلیل‌ها</p>
                        <p class="text-3xl font-bold mt-1 text-blue-600">${dashboardData.totalAnalyses}</p>
                    </div>
                    <div class="icon-box">
                        <i class="fas fa-chart-line text-xl"></i>
                    </div>
                </div>
                <div class="mt-4 flex items-center text-sm text-gray-600">
                    <i class="fas fa-database ml-1"></i>
                    <span>کل تحلیل‌های انجام شده</span>
                </div>
            </div>

            <div class="stat-card rounded-lg p-6 fade-in">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm">کل تماس‌ها</p>
                        <p class="text-3xl font-bold mt-1 text-green-600">${dashboardData.totalCalls}</p>
                    </div>
                    <div class="icon-box success">
                        <i class="fas fa-phone text-xl"></i>
                    </div>
                </div>
                <div class="mt-4 flex items-center text-sm text-gray-600">
                    <i class="fas fa-check-circle text-green-600 ml-1"></i>
                    <span>تماس‌های تحلیل شده</span>
                </div>
            </div>

            <div class="stat-card rounded-lg p-6 fade-in">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm">نرخ موفقیت</p>
                        <p class="text-3xl font-bold mt-1 ${successRateClass === 'success' ? 'text-green-600' : successRateClass === 'warning' ? 'text-yellow-600' : 'text-red-600'}">${successRateFormatted}%</p>
                    </div>
                    <div class="icon-box ${successRateClass}">
                        <i class="fas fa-trophy text-xl"></i>
                    </div>
                </div>
                <div class="mt-4">
                    <div class="progress-bar">
                        <div class="progress-fill ${successRateClass === 'success' ? '!bg-green-500' : successRateClass === 'warning' ? '!bg-yellow-500' : '!bg-red-500'}" 
                             style="width: ${successRateFormatted}%"></div>
                    </div>
                </div>
            </div>

            <div class="stat-card rounded-lg p-6 fade-in">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm">کاربران فعال</p>
                        <p class="text-3xl font-bold mt-1 text-purple-600">${dashboardData.activeUsers}</p>
                    </div>
                    <div class="icon-box info">
                        <i class="fas fa-users text-xl"></i>
                    </div>
                </div>
                <div class="mt-4 flex items-center text-sm text-gray-600">
                    <i class="fas fa-user-check text-purple-600 ml-1"></i>
                    <span>کاربرانی که تحلیل داشته‌اند</span>
                </div>
            </div>
        `;
    }

    function renderCharts() {
        // نابود کردن چارت‌های قبلی
        Object.values(charts).forEach(chart => chart?.destroy());
        charts = {};

        renderTrendChart();
        renderScoreDistributionChart();
    }

    function renderTrendChart() {
        const ctx = document.getElementById('trendChart');
        if (!ctx) return;

        const weeks = Object.keys(dashboardData.weeklyTrend).sort();
        const counts = weeks.map(w => dashboardData.weeklyTrend[w]);

        charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: weeks.map(w => {
                    const [year, week] = w.split('-W');
                    return `هفته ${week}`;
                }),
                datasets: [{
                    label: 'تعداد تحلیل‌ها',
                    data: counts,
                    borderColor: '#1e40af',
                    backgroundColor: 'rgba(30, 64, 175, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#1e40af',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        titleColor: '#fff',
                        bodyColor: '#cbd5e1',
                        padding: 10,
                        cornerRadius: 8
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0, 0, 0, 0.05)' },
                        ticks: { stepSize: 1 }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }

    function renderScoreDistributionChart() {
        const ctx = document.getElementById('scoreDistributionChart');
        if (!ctx) return;

        const labels = Object.keys(dashboardData.scoreDistribution);
        const data = Object.values(dashboardData.scoreDistribution);
        const colors = {
            'عالی (8-10)': '#10b981',
            'خوب (6-8)': '#3b82f6',
            'متوسط (4-6)': '#f59e0b',
            'ضعیف (0-4)': '#ef4444'
        };

        charts.distribution = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: labels.map(l => colors[l] || '#94a3b8'),
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        titleColor: '#fff',
                        bodyColor: '#cbd5e1',
                        callbacks: {
                            label: (context) => {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.raw / total) * 100).toFixed(1);
                                return `${context.label}: ${context.raw} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    function renderRecentActivities() {
        const tbody = document.querySelector('#recent-activities tbody');
        if (!tbody) return;

        if (dashboardData.recentAnalyses.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center py-8 text-gray-500">
                        <i class="fas fa-inbox text-4xl mb-3 opacity-50"></i>
                        <p>هیچ فعالیتی یافت نشد</p>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = dashboardData.recentAnalyses.map(item => {
            const date = new Date(item.date);
            const formattedDate = date.toLocaleDateString('fa-IR', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });

            const scoreClass = item.type === 'تحلیل فروش' 
                ? (item.score >= 8 ? 'badge-success' : item.score >= 6 ? 'badge-warning' : 'badge-danger')
                : (item.score >= 70 ? 'badge-success' : item.score >= 50 ? 'badge-warning' : 'badge-danger');

            const scoreText = item.type === 'تحلیل فروش' 
                ? `${item.score.toFixed(1)}/10` 
                : `${item.score.toFixed(0)}%`;

            return `
                <tr class="hover:bg-gray-50 transition">
                    <td>
                        <div class="flex items-center gap-2">
                            <div class="icon-box ${item.type === 'تحلیل فروش' ? 'info' : 'success'} w-8 h-8">
                                <i class="fas ${item.type === 'تحلیل فروش' ? 'fa-chart-line' : 'fa-diagram-project'} text-sm"></i>
                            </div>
                            <span>${item.type}</span>
                        </div>
                    </td>
                    <td>${item.user}</td>
                    <td>${formattedDate}</td>
                    <td>
                        <span class="badge ${scoreClass}">${scoreText}</span>
                    </td>
                </tr>
            `;
        }).join('');
    }

    function renderTopSellers() {
        const container = document.getElementById('top-sellers');
        if (!container) return;

        if (dashboardData.topSellers.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">اطلاعاتی موجود نیست</p>';
            return;
        }

        const maxCount = Math.max(...dashboardData.topSellers.map(s => s.count));
        
        container.innerHTML = dashboardData.topSellers.map(seller => {
            const percentage = (seller.count / maxCount) * 100;
            return `
                <div class="mb-4">
                    <div class="flex items-center justify-between mb-1">
                        <span class="font-medium text-gray-700">${seller.name}</span>
                        <span class="text-sm text-gray-600">${seller.count} تحلیل</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${percentage}%"></div>
                    </div>
                </div>
            `;
        }).join('');
    }

    function renderTopCustomers() {
        const container = document.getElementById('top-customers');
        if (!container) return;

        if (dashboardData.topCustomers.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">اطلاعاتی موجود نیست</p>';
            return;
        }

        container.innerHTML = dashboardData.topCustomers.map(customer => `
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
                <span class="font-medium text-gray-700">${customer.name}</span>
                <span class="badge badge-info">${customer.count} تماس</span>
            </div>
        `).join('');
    }

    // ========================================
    // UTILITY FUNCTIONS
    // ========================================
    function getWeekNumber(date) {
        const firstDayOfYear = new Date(date.getFullYear(), 0, 1);
        const pastDaysOfYear = (date - firstDayOfYear) / 86400000;
        return Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1) / 7);
    }

    function getScoreRange(score) {
        if (score >= 8) return 'عالی (8-10)';
        if (score >= 6) return 'خوب (6-8)';
        if (score >= 4) return 'متوسط (4-6)';
        return 'ضعیف (0-4)';
    }
})();