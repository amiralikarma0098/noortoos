// ========================================
// USERS ANALYSIS - PROFESSIONAL VERSION
// ========================================

let analysisData = null;
let currentUser = null;
let charts = {};

// ========================================
// INITIALIZATION
// ========================================
document.addEventListener('DOMContentLoaded', async function() {
    await loadLatestAnalysis();
});

async function loadLatestAnalysis() {
    try {
        const response = await fetch('/api/analysis/latest');

        if (!response.ok) {
            showNoData();
            return;
        }

        const data = await response.json();

        if (!data || !data.آمار || !data.آمار.کاربران_فعال || data.آمار.کاربران_فعال.length === 0) {
            showNoData();
            return;
        }

        analysisData = data;
        console.log('✅ داده بارگذاری شد:', analysisData);

        renderContent();

    } catch (error) {
        console.error('❌ خطا:', error);
        showNoData();
    }
}

function showNoData() {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('no-data').classList.remove('hidden');
}

// ========================================
// RENDER MAIN CONTENT
// ========================================
function renderContent() {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('content').classList.remove('hidden');

    renderOverviewStats();
    renderUserTabs();

    // نمایش اولین کاربر
    const firstUser = analysisData.آمار.کاربران_فعال[0];
    showUser(firstUser.نام);
}

function renderOverviewStats() {
    const stats = analysisData.آمار || {};
    const users = stats.کاربران_فعال || [];

    const totalCalls = stats.تعداد_کل_تماس_ها || 0;
    const successCalls = stats.تماس_های_موفق || 0;
    const failedCalls = stats.تماس_های_بی_پاسخ || 0;
    const activeUsers = users.length;
    const successRate = totalCalls > 0 ? ((successCalls / totalCalls) * 100).toFixed(0) : 0;

    const html = `
        <div class="pro-card rounded-xl p-6 text-center stat-card">
            <div class="icon-box info w-12 h-12 mx-auto mb-3">
                <i class="fas fa-users text-2xl"></i>
            </div>
            <div class="text-4xl font-bold text-blue-600 mb-2">${activeUsers}</div>
            <div class="text-sm text-gray-600">کارشناس فعال</div>
        </div>
        
        <div class="pro-card rounded-xl p-6 text-center stat-card">
            <div class="icon-box w-12 h-12 mx-auto mb-3">
                <i class="fas fa-phone text-2xl"></i>
            </div>
            <div class="text-4xl font-bold text-blue-700 mb-2">${totalCalls}</div>
            <div class="text-sm text-gray-600">کل تماس‌ها</div>
        </div>
        
        <div class="pro-card rounded-xl p-6 text-center stat-card">
            <div class="icon-box success w-12 h-12 mx-auto mb-3">
                <i class="fas fa-check-circle text-2xl"></i>
            </div>
            <div class="text-4xl font-bold text-green-600 mb-2">${successCalls}</div>
            <div class="text-sm text-gray-600">تماس موفق</div>
        </div>
        
        <div class="pro-card rounded-xl p-6 text-center stat-card">
            <div class="icon-box warning w-12 h-12 mx-auto mb-3">
                <i class="fas fa-chart-line text-2xl"></i>
            </div>
            <div class="text-4xl font-bold text-orange-600 mb-2">${successRate}%</div>
            <div class="text-sm text-gray-600">نرخ موفقیت</div>
        </div>
    `;

    document.getElementById('overview-stats').innerHTML = html;
}

function renderUserTabs() {
    const users = analysisData.آمار.کاربران_فعال || [];

    const html = users.map((user, index) => {
        const userName = user.نام;
        const callCount = user.تعداد_تماس || 0;
        const isActive = index === 0 ? 'active' : '';

        return `
            <button onclick="showUser('${userName}')" class="user-tab ${isActive} px-5 py-4 rounded-xl font-medium text-right">
                <div class="flex items-center justify-between gap-3">
                    <div class="flex-1">
                        <div class="font-semibold text-base mb-1">${userName}</div>
                        <div class="text-xs opacity-75">${callCount} تماس</div>
                    </div>
                    <div class="icon-box ${isActive ? 'bg-white bg-opacity-20' : ''} w-10 h-10">
                        <i class="fas fa-user text-lg"></i>
                    </div>
                </div>
            </button>
        `;
    }).join('');

    document.getElementById('user-tabs').innerHTML = html;
}

// ========================================
// SHOW USER ANALYSIS
// ========================================
function showUser(userName) {
    console.log('📊 نمایش تحلیل کاربر:', userName);

    currentUser = userName;

    // Update active tab
    document.querySelectorAll('.user-tab').forEach(tab => {
        tab.classList.remove('active');
        if (tab.textContent.includes(userName)) {
            tab.classList.add('active');
        }
    });

    // Destroy existing charts
    Object.values(charts).forEach(chart => chart.destroy());
    charts = {};

    // Render user content
    renderUserAnalysis(userName);

    // Initialize charts
    setTimeout(() => initializeCharts(userName), 100);
}

function renderUserAnalysis(userName) {
    const users = analysisData.آمار.کاربران_فعال || [];
    const user = users.find(u => u.نام === userName);

    if (!user) {
        document.getElementById('user-content').innerHTML = `
            <div class="pro-card rounded-xl p-8 text-center">
                <p class="text-gray-600">کاربر یافت نشد</p>
            </div>
        `;
        return;
    }

    const stats = analysisData.آمار || {};
    const totalCalls = stats.تعداد_کل_تماس_ها || 1;
    const userCalls = user.تعداد_تماس || 0;
    const userPercentage = ((userCalls / totalCalls) * 100).toFixed(1);

    const html = `
        <!-- User Profile Header -->
        <div class="pro-card rounded-xl p-8 mb-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-r-4 border-blue-600">
            <div class="flex flex-col md:flex-row items-center md:items-start justify-between gap-6">
                <div class="flex items-center gap-6">
                    <div class="bg-gradient-to-br from-blue-600 to-blue-800 p-6 rounded-2xl shadow-lg">
                        <i class="fas fa-user-tie text-4xl text-white"></i>
                    </div>
                    <div>
                        <h2 class="text-3xl font-bold text-gray-800 mb-2">${userName}</h2>
                        <p class="text-gray-600 mb-2">${user.یادداشت_عملکرد || 'کارشناس پشتیبانی'}</p>
                        <div class="flex items-center gap-2">
                            <span class="${getUserStatusBadgeClass(userCalls, totalCalls/users.length)}">${getUserStatus(userCalls, totalCalls/users.length)}</span>
                            <span class="badge badge-info">رتبه ${getUserRank(userName)}</span>
                        </div>
                    </div>
                </div>
                <div class="text-center md:text-left bg-white rounded-xl p-6 shadow-sm">
                    <div class="text-5xl font-bold text-blue-600 mb-1">${userCalls}</div>
                    <div class="text-sm text-gray-600 mb-2">تماس انجام شده</div>
                    <div class="progress-bar mb-2">
                        <div class="progress-fill" style="width: ${userPercentage}%"></div>
                    </div>
                    <div class="text-sm text-blue-600 font-semibold">${userPercentage}% از کل</div>
                </div>
            </div>
        </div>

        <!-- Key Metrics -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            ${renderUserMetric('تعداد تماس', userCalls, 'fas fa-phone', 'info')}
            ${renderUserMetric('سهم از کل', userPercentage + '%', 'fas fa-chart-pie', 'primary')}
            ${renderUserMetric('رتبه', getUserRank(userName), 'fas fa-trophy', 'warning')}
            ${renderUserMetric('میانگین روزانه', Math.round(userCalls / 30), 'fas fa-calendar-day', 'success')}
        </div>

        <!-- Charts Section -->
        <div class="grid md:grid-cols-2 gap-6 mb-6">
            <!-- Call Distribution Chart -->
            <div class="pro-card rounded-xl p-6">
                <h3 class="text-lg font-semibold mb-4 flex items-center gap-2 text-gray-800">
                    <div class="icon-box w-8 h-8">
                        <i class="fas fa-chart-pie text-sm"></i>
                    </div>
                    توزیع تماس‌ها
                </h3>
                <div class="chart-container">
                    <canvas id="user-calls-pie"></canvas>
                </div>
            </div>

            <!-- Performance Comparison Chart -->
            <div class="pro-card rounded-xl p-6">
                <h3 class="text-lg font-semibold mb-4 flex items-center gap-2 text-gray-800">
                    <div class="icon-box info w-8 h-8">
                        <i class="fas fa-chart-bar text-sm"></i>
                    </div>
                    مقایسه با سایر کارشناسان
                </h3>
                <div class="chart-container">
                    <canvas id="user-comparison-bar"></canvas>
                </div>
            </div>
        </div>

        <!-- Detailed Statistics -->
        <div class="pro-card rounded-xl p-6 mb-6">
            <h3 class="text-lg font-semibold mb-4 flex items-center gap-2 text-gray-800">
                <div class="icon-box success w-8 h-8">
                    <i class="fas fa-list-check text-sm"></i>
                </div>
                آمار تفصیلی عملکرد
            </h3>
            <div class="grid md:grid-cols-3 gap-4">
                ${renderStatItem('میانگین روزانه', Math.round(userCalls / 30), 'fas fa-calendar-day', 'info')}
                ${renderStatItem('بیشترین تماس', getMaxCalls(users), 'fas fa-arrow-up', 'success')}
                ${renderStatItem('کمترین تماس', getMinCalls(users), 'fas fa-arrow-down', 'warning')}
            </div>
        </div>

        <!-- Strengths & Improvement Areas -->
        <div class="grid md:grid-cols-2 gap-6 mb-6">
            <!-- Strengths -->
            <div class="pro-card rounded-xl p-6 border-r-4 border-green-500">
                <h3 class="text-lg font-semibold mb-4 flex items-center gap-2 text-green-700">
                    <div class="icon-box success w-8 h-8">
                        <i class="fas fa-thumbs-up text-sm"></i>
                    </div>
                    نقاط قوت
                </h3>
                <ul class="space-y-2">
                    ${getUserStrengths(userName, userCalls, totalCalls/users.length).map(s => `
                        <li class="flex items-start gap-3 list-item rounded-lg p-3 bg-green-50 border border-green-100">
                            <i class="fas fa-check-circle text-green-600 mt-1"></i>
                            <span class="text-gray-700 text-sm">${s}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>

            <!-- Improvement Suggestions -->
            <div class="pro-card rounded-xl p-6 border-r-4 border-orange-500">
                <h3 class="text-lg font-semibold mb-4 flex items-center gap-2 text-orange-700">
                    <div class="icon-box warning w-8 h-8">
                        <i class="fas fa-lightbulb text-sm"></i>
                    </div>
                    پیشنهادات بهبود
                </h3>
                <ul class="space-y-2">
                    ${getUserSuggestions(userName, userCalls, totalCalls/users.length).map(s => `
                        <li class="flex items-start gap-3 list-item rounded-lg p-3 bg-orange-50 border border-orange-100">
                            <i class="fas fa-arrow-circle-left text-orange-600 mt-1"></i>
                            <span class="text-gray-700 text-sm">${s}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
        </div>

        <!-- Training & Development -->
        <div class="pro-card rounded-xl p-6 bg-gradient-to-br from-yellow-50 to-orange-50 border-r-4 border-yellow-500">
            <h3 class="text-lg font-semibold mb-4 flex items-center gap-2 text-yellow-800">
                <div class="icon-box bg-yellow-100 w-8 h-8">
                    <i class="fas fa-graduation-cap text-sm text-yellow-700"></i>
                </div>
                برنامه آموزشی پیشنهادی
            </h3>
            <div class="grid md:grid-cols-2 gap-4">
                ${getTrainingRecommendations(userName, userCalls, totalCalls/users.length).map(t => `
                    <div class="bg-white rounded-lg p-4 border border-yellow-200">
                        <div class="flex items-start gap-3">
                            <div class="icon-box bg-yellow-100 w-10 h-10">
                                <i class="${t.icon} text-lg text-yellow-700"></i>
                            </div>
                            <div class="flex-1">
                                <div class="font-semibold text-gray-800 mb-1">${t.title}</div>
                                <div class="text-sm text-gray-600">${t.description}</div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    document.getElementById('user-content').innerHTML = html;
}

// ========================================
// HELPER FUNCTIONS
// ========================================
function renderUserMetric(label, value, icon, colorClass) {
    const colorMap = {
        'primary': 'text-blue-700',
        'info': 'text-blue-600',
        'success': 'text-green-600',
        'warning': 'text-orange-600',
        'danger': 'text-red-600'
    };
    
    const color = colorMap[colorClass] || 'text-blue-600';
    
    return `
        <div class="pro-card rounded-xl p-5 text-center">
            <i class="${icon} text-3xl ${color} mb-2"></i>
            <div class="text-3xl font-bold ${color} mb-1">${value}</div>
            <div class="text-xs text-gray-600">${label}</div>
        </div>
    `;
}

function renderStatItem(label, value, icon, colorClass) {
    const colorMap = {
        'info': 'text-blue-600',
        'success': 'text-green-600',
        'warning': 'text-orange-600'
    };
    
    const color = colorMap[colorClass] || 'text-blue-600';
    
    return `
        <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div class="flex items-center justify-between mb-2">
                <i class="${icon} text-2xl ${color}"></i>
                <span class="text-2xl font-bold ${color}">${value}</span>
            </div>
            <div class="text-sm text-gray-600">${label}</div>
        </div>
    `;
}

function getUserRank(userName) {
    const users = analysisData.آمار.کاربران_فعال || [];
    const sorted = [...users].sort((a, b) => (b.تعداد_تماس || 0) - (a.تعداد_تماس || 0));
    const rank = sorted.findIndex(u => u.نام === userName) + 1;
    return `${rank} از ${users.length}`;
}

function getUserStatus(userCalls, avgCalls) {
    const ratio = userCalls / avgCalls;
    if (ratio >= 1.5) return 'عالی';
    if (ratio >= 1.0) return 'خوب';
    if (ratio >= 0.7) return 'متوسط';
    return 'نیاز به بهبود';
}

function getUserStatusBadgeClass(userCalls, avgCalls) {
    const ratio = userCalls / avgCalls;
    if (ratio >= 1.5) return 'badge badge-success';
    if (ratio >= 1.0) return 'badge badge-info';
    if (ratio >= 0.7) return 'badge badge-warning';
    return 'badge badge-danger';
}

function getMaxCalls(users) {
    return Math.max(...users.map(u => u.تعداد_تماس || 0));
}

function getMinCalls(users) {
    return Math.min(...users.map(u => u.تعداد_تماس || 0));
}

function getUserStrengths(userName, userCalls, avgCalls) {
    const strengths = [];
    
    if (userCalls > avgCalls * 1.5) {
        strengths.push('عملکرد بسیار بالا و قابل تقدیر');
        strengths.push('حجم تماس به مراتب بیشتر از میانگین تیم');
    } else if (userCalls > avgCalls * 1.2) {
        strengths.push('حجم تماس بالاتر از میانگین تیم');
        strengths.push('عملکرد مطلوب و قابل توجه');
    } else if (userCalls > avgCalls) {
        strengths.push('فعالیت بیش از حد انتظار');
    }
    
    strengths.push('مشارکت فعال در اهداف تیمی');
    strengths.push('انگیزه و پشتکار در انجام وظایف محوله');
    
    return strengths;
}

function getUserSuggestions(userName, userCalls, avgCalls) {
    const suggestions = [];
    
    if (userCalls < avgCalls * 0.7) {
        suggestions.push('افزایش قابل توجه تعداد تماس‌های روزانه');
        suggestions.push('بررسی دقیق موانع و چالش‌های موجود');
        suggestions.push('مشاوره با مدیر تیم برای بهبود عملکرد');
    } else if (userCalls < avgCalls) {
        suggestions.push('افزایش تدریجی تعداد تماس‌ها');
        suggestions.push('تمرکز بر بهبود کیفیت تعاملات');
    }
    
    suggestions.push('یادگیری تکنیک‌های پیشرفته ارتباط با مشتری');
    suggestions.push('شرکت منظم در جلسات آموزشی و کارگاه‌ها');
    
    return suggestions;
}

function getTrainingRecommendations(userName, userCalls, avgCalls) {
    const recommendations = [];
    
    if (userCalls < avgCalls * 0.8) {
        recommendations.push({
            icon: 'fas fa-phone-volume',
            title: 'مهارت‌های تماس تلفنی',
            description: 'آموزش تکنیک‌های برقراری ارتباط موثر و حرفه‌ای'
        });
    }
    
    recommendations.push({
        icon: 'fas fa-comments',
        title: 'مهارت‌های ارتباطی پیشرفته',
        description: 'شنوندگی فعال، همدلی و مدیریت گفتگو'
    });
    
    recommendations.push({
        icon: 'fas fa-clock',
        title: 'مدیریت زمان و بهره‌وری',
        description: 'بهینه‌سازی فرآیند تماس و افزایش کارایی'
    });
    
    recommendations.push({
        icon: 'fas fa-handshake',
        title: 'تکنیک‌های فروش حرفه‌ای',
        description: 'استراتژی‌های جذب، متقاعدسازی و بستن فروش'
    });
    
    return recommendations;
}

// ========================================
// CHART FUNCTIONS
// ========================================
function initializeCharts(userName) {
    createCallsPieChart(userName);
    createComparisonBarChart(userName);
}

function createCallsPieChart(userName) {
    const canvas = document.getElementById('user-calls-pie');
    if (!canvas) return;
    
    const users = analysisData.آمار.کاربران_فعال || [];
    const user = users.find(u => u.نام === userName);
    const userCalls = user?.تعداد_تماس || 0;
    const totalCalls = analysisData.آمار.تعداد_کل_تماس_ها || 1;
    const otherCalls = totalCalls - userCalls;
    
    charts.userPie = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: [userName, 'سایر کارشناسان'],
            datasets: [{
                data: [userCalls, otherCalls],
                backgroundColor: [
                    'rgba(30, 64, 175, 0.8)',
                    'rgba(226, 232, 240, 0.8)'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: {
                            family: 'IBM Plex Sans Arabic',
                            size: 12
                        },
                        padding: 15
                    }
                }
            }
        }
    });
}

function createComparisonBarChart(userName) {
    const canvas = document.getElementById('user-comparison-bar');
    if (!canvas) return;
    
    const users = analysisData.آمار.کاربران_فعال || [];
    const sorted = [...users].sort((a, b) => (b.تعداد_تماس || 0) - (a.تعداد_تماس || 0));
    
    const labels = sorted.map(u => u.نام);
    const data = sorted.map(u => u.تعداد_تماس || 0);
    const colors = sorted.map(u => u.نام === userName ? 'rgba(30, 64, 175, 0.8)' : 'rgba(203, 213, 225, 0.6)');
    
    charts.userComparison = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'تعداد تماس',
                data: data,
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace('0.8', '1').replace('0.6', '0.8')),
                borderWidth: 1,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        font: {
                            family: 'IBM Plex Sans Arabic',
                            size: 11
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            family: 'IBM Plex Sans Arabic',
                            size: 11
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}