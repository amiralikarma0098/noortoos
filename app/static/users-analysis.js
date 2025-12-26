// ========================================
// USERS ANALYSIS - MAIN JS
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

    const html = `
        <div class="glass-card rounded-xl p-6 text-center stat-card">
            <i class="fas fa-users text-4xl text-blue-600 mb-3"></i>
            <div class="text-4xl font-bold text-blue-600">${activeUsers}</div>
            <div class="text-sm text-gray-600 mt-1">کارشناس فعال</div>
        </div>
        
        <div class="glass-card rounded-xl p-6 text-center stat-card">
            <i class="fas fa-phone text-4xl text-purple-600 mb-3"></i>
            <div class="text-4xl font-bold text-purple-600">${totalCalls}</div>
            <div class="text-sm text-gray-600 mt-1">کل تماس‌ها</div>
        </div>
        
        <div class="glass-card rounded-xl p-6 text-center stat-card">
            <i class="fas fa-check-circle text-4xl text-green-600 mb-3"></i>
            <div class="text-4xl font-bold text-green-600">${successCalls}</div>
            <div class="text-sm text-gray-600 mt-1">تماس موفق</div>
        </div>
        
        <div class="glass-card rounded-xl p-6 text-center stat-card">
            <i class="fas fa-chart-line text-4xl text-orange-600 mb-3"></i>
            <div class="text-4xl font-bold text-orange-600">${((successCalls/totalCalls)*100).toFixed(0)}%</div>
            <div class="text-sm text-gray-600 mt-1">نرخ موفقیت</div>
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
            <button onclick="showUser('${userName}')" class="user-tab ${isActive} px-6 py-4 rounded-xl font-semibold text-right">
                <div class="flex items-center justify-between">
                    <div>
                        <div class="font-bold text-lg">${userName}</div>
                        <div class="text-xs opacity-75">${callCount} تماس</div>
                    </div>
                    <i class="fas fa-user-circle text-2xl"></i>
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
        document.getElementById('user-content').innerHTML = '<p class="text-center text-gray-600">کاربر یافت نشد</p>';
        return;
    }

    const stats = analysisData.آمار || {};
    const totalCalls = stats.تعداد_کل_تماس_ها || 1;
    const userCalls = user.تعداد_تماس || 0;
    const userPercentage = ((userCalls / totalCalls) * 100).toFixed(1);

    const html = `
        <!-- User Header -->
        <div class="glass-card rounded-2xl p-8 mb-6 bg-gradient-to-br from-purple-50 to-indigo-50">
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-6">
                    <div class="bg-gradient-to-br from-purple-500 to-indigo-600 p-6 rounded-full">
                        <i class="fas fa-user text-4xl text-white"></i>
                    </div>
                    <div>
                        <h2 class="text-3xl font-bold gradient-text mb-2">${userName}</h2>
                        <p class="text-gray-600">${user.یادداشت_عملکرد || 'کارشناس پشتیبانی'}</p>
                    </div>
                </div>
                <div class="text-left">
                    <div class="text-5xl font-bold text-purple-600">${userCalls}</div>
                    <div class="text-sm text-gray-600">تماس انجام شده</div>
                    <div class="text-sm text-purple-600 font-semibold mt-1">${userPercentage}% از کل</div>
                </div>
            </div>
        </div>

        <!-- Performance Metrics -->
        <div class="grid md:grid-cols-4 gap-6 mb-6">
            ${renderUserMetric('تعداد تماس', userCalls, 'fas fa-phone', 'blue')}
            ${renderUserMetric('سهم از کل', userPercentage + '%', 'fas fa-chart-pie', 'purple')}
            ${renderUserMetric('رتبه', getUserRank(userName), 'fas fa-trophy', 'yellow')}
            ${renderUserMetric('وضعیت', getUserStatus(userCalls, totalCalls/users.length), 'fas fa-signal', 'green')}
        </div>

        <!-- Charts Section -->
        <div class="grid md:grid-cols-2 gap-6 mb-6">
            <!-- Call Distribution -->
            <div class="glass-card rounded-2xl p-6">
                <h3 class="text-xl font-bold mb-4 flex items-center">
                    <i class="fas fa-chart-pie text-purple-600 ml-3"></i>
                    توزیع تماس‌ها
                </h3>
                <canvas id="user-calls-pie"></canvas>
            </div>

            <!-- Performance Comparison -->
            <div class="glass-card rounded-2xl p-6">
                <h3 class="text-xl font-bold mb-4 flex items-center">
                    <i class="fas fa-chart-bar text-blue-600 ml-3"></i>
                    مقایسه با سایرین
                </h3>
                <canvas id="user-comparison-bar"></canvas>
            </div>
        </div>

        <!-- Detailed Stats -->
        <div class="glass-card rounded-2xl p-6 mb-6">
            <h3 class="text-xl font-bold mb-4 flex items-center">
                <i class="fas fa-list-check text-green-600 ml-3"></i>
                آمار تفصیلی
            </h3>
            <div class="grid md:grid-cols-3 gap-4">
                ${renderStatItem('میانگین تماس روزانه', Math.round(userCalls / 30), 'fas fa-calendar-day')}
                ${renderStatItem('بیشترین تماس', getMaxCalls(users), 'fas fa-arrow-up')}
                ${renderStatItem('کمترین تماس', getMinCalls(users), 'fas fa-arrow-down')}
            </div>
        </div>

        <!-- Strengths & Weaknesses -->
        <div class="grid md:grid-cols-2 gap-6 mb-6">
            <div class="glass-card rounded-2xl p-6 bg-green-50">
                <h3 class="text-xl font-bold mb-4 flex items-center text-green-700">
                    <i class="fas fa-thumbs-up ml-3"></i>
                    نقاط قوت
                </h3>
                <ul class="space-y-2">
                    ${getUserStrengths(userName, userCalls, totalCalls/users.length).map(s => `
                        <li class="flex items-start bg-white rounded-lg p-3">
                            <i class="fas fa-check-circle text-green-600 ml-2 mt-1"></i>
                            <span>${s}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>

            <div class="glass-card rounded-2xl p-6 bg-orange-50">
                <h3 class="text-xl font-bold mb-4 flex items-center text-orange-700">
                    <i class="fas fa-lightbulb ml-3"></i>
                    پیشنهادات بهبود
                </h3>
                <ul class="space-y-2">
                    ${getUserSuggestions(userName, userCalls, totalCalls/users.length).map(s => `
                        <li class="flex items-start bg-white rounded-lg p-3">
                            <i class="fas fa-arrow-right text-orange-600 ml-2 mt-1"></i>
                            <span>${s}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
        </div>

        <!-- Training Recommendations -->
        <div class="glass-card rounded-2xl p-6 bg-gradient-to-br from-yellow-50 to-orange-50 border-r-4 border-yellow-500">
            <h3 class="text-xl font-bold mb-4 flex items-center text-yellow-800">
                <i class="fas fa-graduation-cap ml-3"></i>
                پیشنهادات آموزشی
            </h3>
            <div class="grid md:grid-cols-2 gap-4">
                ${getTrainingRecommendations(userName, userCalls, totalCalls/users.length).map(t => `
                    <div class="bg-white rounded-lg p-4">
                        <div class="flex items-start gap-3">
                            <div class="bg-yellow-100 rounded-lg p-3">
                                <i class="${t.icon} text-2xl text-yellow-600"></i>
                            </div>
                            <div>
                                <div class="font-bold text-gray-800 mb-1">${t.title}</div>
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
function renderUserMetric(label, value, icon, color) {
    return `
        <div class="glass-card rounded-xl p-6 text-center">
            <i class="${icon} text-3xl text-${color}-600 mb-2"></i>
            <div class="text-3xl font-bold text-${color}-600">${value}</div>
            <div class="text-sm text-gray-600 mt-1">${label}</div>
        </div>
    `;
}

function renderStatItem(label, value, icon) {
    return `
        <div class="bg-white bg-opacity-50 rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
                <i class="${icon} text-2xl text-purple-600"></i>
                <span class="text-2xl font-bold text-purple-600">${value}</span>
            </div>
            <div class="text-sm text-gray-600">${label}</div>
        </div>
    `;
}

function getUserRank(userName) {
    const users = analysisData.آمار.کاربران_فعال || [];
    const sorted = users.sort((a, b) => (b.تعداد_تماس || 0) - (a.تعداد_تماس || 0));
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

function getMaxCalls(users) {
    return Math.max(...users.map(u => u.تعداد_تماس || 0));
}

function getMinCalls(users) {
    return Math.min(...users.map(u => u.تعداد_تماس || 0));
}

function getUserStrengths(userName, userCalls, avgCalls) {
    const strengths = [];
    
    if (userCalls > avgCalls * 1.2) {
        strengths.push('حجم تماس بالاتر از میانگین تیم');
    }
    
    if (userCalls > avgCalls) {
        strengths.push('فعالیت بیش از حد انتظار');
    }
    
    strengths.push('پشتکار و انگیزه بالا در انجام تماس‌ها');
    strengths.push('مشارکت فعال در تیم پشتیبانی');
    
    return strengths;
}

function getUserSuggestions(userName, userCalls, avgCalls) {
    const suggestions = [];
    
    if (userCalls < avgCalls * 0.8) {
        suggestions.push('افزایش تعداد تماس‌های روزانه');
        suggestions.push('بررسی موانع و چالش‌های موجود');
    } else if (userCalls < avgCalls) {
        suggestions.push('تمرکز بر افزایش کیفیت تماس‌ها');
    }
    
    suggestions.push('یادگیری تکنیک‌های جدید فروش و ارتباط');
    suggestions.push('مشارکت در جلسات آموزشی تیمی');
    
    return suggestions;
}

function getTrainingRecommendations(userName, userCalls, avgCalls) {
    const recommendations = [];
    
    if (userCalls < avgCalls * 0.8) {
        recommendations.push({
            icon: 'fas fa-phone-volume',
            title: 'آموزش مهارت‌های تماس',
            description: 'تکنیک‌های برقراری ارتباط موثر تلفنی'
        });
    }
    
    recommendations.push({
        icon: 'fas fa-comments',
        title: 'مهارت‌های ارتباطی',
        description: 'بهبود شنوندگی فعال و همدلی با مشتری'
    });
    
    recommendations.push({
        icon: 'fas fa-trophy',
        title: 'مدیریت زمان',
        description: 'افزایش بهره‌وری در تماس‌های روزانه'
    });
    
    recommendations.push({
        icon: 'fas fa-handshake',
        title: 'تکنیک‌های فروش',
        description: 'یادگیری استراتژی‌های بستن فروش'
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
                    'rgba(147, 51, 234, 0.8)',
                    'rgba(203, 213, 225, 0.8)'
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
                    position: 'bottom'
                }
            }
        }
    });
}

function createComparisonBarChart(userName) {
    const canvas = document.getElementById('user-comparison-bar');
    if (!canvas) return;
    
    const users = analysisData.آمار.کاربران_فعال || [];
    const sorted = users.sort((a, b) => (b.تعداد_تماس || 0) - (a.تعداد_تماس || 0));
    
    const labels = sorted.map(u => u.نام);
    const data = sorted.map(u => u.تعداد_تماس || 0);
    const colors = sorted.map(u => u.نام === userName ? 'rgba(147, 51, 234, 0.8)' : 'rgba(203, 213, 225, 0.8)');
    
    charts.userComparison = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'تعداد تماس',
                data: data,
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
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