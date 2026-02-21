// ========================================
// REFERRAL ANALYZER - MAIN JS
// Version: 1.0
// ========================================

let selectedFile = null;
let analysisData = null;
let currentTab = 'overview';
let charts = {};

// ========================================
// INITIALIZATION
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    initializeUploadArea();
    initializeAnalyzeButton();
    
    // اضافه کردن event listener برای دکمه�های تب
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const tabName = this.getAttribute('data-tab');
            showTab(tabName, e);
        });
    });
});

function initializeUploadArea() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');

    if (!uploadArea || !fileInput) return;

    uploadArea.addEventListener('click', () => fileInput.click());

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) handleFile(files[0]);
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleFile(e.target.files[0]);
    });
}

function initializeAnalyzeButton() {
    const analyzeBtn = document.getElementById('analyze-btn');
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', analyzeFile);
    }
}

// ========================================
// FILE HANDLING
// ========================================
function handleFile(file) {
    selectedFile = file;
    document.getElementById('file-name').textContent = file.name;
    document.getElementById('file-size').textContent = formatFileSize(file.size);
    document.getElementById('file-info').classList.remove('hidden');
    document.getElementById('analyze-btn').classList.remove('hidden');
}

function removeFile() {
    selectedFile = null;
    document.getElementById('file-input').value = '';
    document.getElementById('file-info').classList.add('hidden');
    document.getElementById('analyze-btn').classList.add('hidden');
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

// ========================================
// ANALYSIS
// ========================================
async function analyzeFile() {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);

    document.getElementById('upload-section').classList.add('hidden');
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');

    try {
        const response = await fetch('/api/analyze-referral', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('خطا در تحلیل فایل');
        }

        analysisData = await response.json();

        if (analysisData.error) {
            alert(analysisData.message);
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('upload-section').classList.remove('hidden');
            return;
        }

        console.log('✅ داده دریافتی:', analysisData);

        document.getElementById('loading').classList.add('hidden');
        document.getElementById('results').classList.remove('hidden');
        showTab('overview');

    } catch (error) {
        console.error('❌ خطا:', error);
        alert('خطا در تحلیل فایل: ' + error.message);
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('upload-section').classList.remove('hidden');
    }
}

// ========================================
// TAB MANAGEMENT
// ========================================
function showTab(tabName, event) {
    currentTab = tabName;

    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active', 'bg-purple-600', 'text-white');
        btn.classList.add('bg-transparent', 'text-gray-700');
    });
    
    if (event) {
        event.target.classList.add('active', 'bg-purple-600', 'text-white');
        event.target.classList.remove('bg-transparent', 'text-gray-700');
    }

    // Destroy existing charts
    Object.values(charts).forEach(chart => {
        if (chart) chart.destroy();
    });
    charts = {};

    // Render tab content
    const content = document.getElementById('tab-content');
    if (!content) return;
    
    switch (tabName) {
        case 'overview':
            content.innerHTML = renderOverview();
            setTimeout(createOverviewCharts, 100);
            break;
        case 'status':
            content.innerHTML = renderStatusAnalysis();
            setTimeout(createStatusCharts, 100);
            break;
        case 'subjects':
            content.innerHTML = renderSubjectAnalysis();
            break;
        case 'units':
            content.innerHTML = renderUnitAnalysis();
            break;
        case 'customers':
            content.innerHTML = renderCustomerAnalysis();
            break;
        case 'insights':
            content.innerHTML = renderInsights();
            break;
    }
}

// ========================================
// RENDER FUNCTIONS
// ========================================

function renderOverview() {
    const status = analysisData?.status_analysis || {};
    const insights = analysisData?.comprehensive_insights || {};
    const dist = status.status_distribution || {};
    
    return `
        <div class="grid md:grid-cols-4 gap-6 mb-6">
            <div class="bg-purple-50 rounded-xl p-6 text-center stat-card">
                <i class="fas fa-clock text-4xl text-purple-600 mb-3"></i>
                <div class="text-3xl font-bold text-purple-600">${dist['بررسی نشده'] || 0}</div>
                <div class="text-gray-600">بررسی نشده</div>
                <div class="text-sm text-gray-500 mt-2">${status.percent_pending?.toFixed(1) || 0}%</div>
            </div>
            <div class="bg-blue-50 rounded-xl p-6 text-center stat-card">
                <i class="fas fa-spinner text-4xl text-blue-600 mb-3"></i>
                <div class="text-3xl font-bold text-blue-600">${dist['درحال پیگیری'] || 0}</div>
                <div class="text-gray-600">در حال پیگیری</div>
            </div>
            <div class="bg-green-50 rounded-xl p-6 text-center stat-card">
                <i class="fas fa-check-circle text-4xl text-green-600 mb-3"></i>
                <div class="text-3xl font-bold text-green-600">${dist['اتمام کار'] || 0}</div>
                <div class="text-gray-600">اتمام یافته</div>
                <div class="text-sm text-gray-500 mt-2">${status.percent_completed?.toFixed(1) || 0}%</div>
            </div>
            <div class="bg-orange-50 rounded-xl p-6 text-center stat-card">
                <i class="fas fa-exclamation-triangle text-4xl text-orange-600 mb-3"></i>
                <div class="text-3xl font-bold text-orange-600">${status.worst_sender_pending?.count || 0}</div>
                <div class="text-gray-600">گلوگاه فعال</div>
                <div class="text-sm text-gray-500 mt-2">${status.worst_sender_pending?.unit || '—'}</div>
            </div>
        </div>

        <div class="bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-2xl p-8 mb-6">
            <h3 class="text-2xl font-bold mb-4 flex items-center">
                <i class="fas fa-robot ml-3 text-3xl"></i>
                خلاصه هوشمند
            </h3>
            <p class="text-lg leading-relaxed mb-6 opacity-90">${insights.summary_fa || 'تحلیل با موفقیت انجام شد. برای دیدن جزئیات بیشتر به تب‌های دیگر مراجعه کنید.'}</p>
            
            ${insights.recommendations_fa ? `
                <h4 class="font-bold text-xl mb-3 flex items-center">
                    <i class="fas fa-lightbulb ml-2"></i>
                    توصیه‌های عملی:
                </h4>
                <ul class="space-y-2">
                    ${insights.recommendations_fa.map(rec => `
                        <li class="flex items-start bg-white bg-opacity-20 rounded-lg p-3">
                            <i class="fas fa-check-circle mt-1 ml-3 text-green-300"></i>
                            <span>${rec}</span>
                        </li>
                    `).join('')}
                </ul>
            ` : ''}
        </div>

        <div class="grid md:grid-cols-2 gap-6">
            <div class="glass-card rounded-2xl p-6">
                <h4 class="font-bold text-lg mb-4">📊 توزیع وضعیت‌ها</h4>
                <canvas id="status-pie-chart" style="max-height: 300px;"></canvas>
            </div>
            <div class="glass-card rounded-2xl p-6">
                <h4 class="font-bold text-lg mb-4">📈 روند روزانه</h4>
                <canvas id="daily-trend-chart" style="max-height: 300px;"></canvas>
            </div>
        </div>
    `;
}

function renderStatusAnalysis() {
    const status = analysisData?.status_analysis || {};
    const dist = status.status_distribution || {};
    
    const total = Object.values(dist).reduce((a, b) => a + b, 0);
    
    return `
        <div class="grid md:grid-cols-2 gap-6">
            <div class="space-y-4">
                <h3 class="text-xl font-bold mb-4">📋 جزئیات وضعیت‌ها</h3>
                ${Object.entries(dist).map(([key, value]) => `
                    <div class="bg-gray-50 rounded-lg p-4">
                        <div class="flex justify-between items-center mb-2">
                            <span class="font-semibold">${key}</span>
                            <span class="bg-purple-600 text-white px-3 py-1 rounded-full text-sm">${value}</span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-3">
                            <div class="bg-purple-600 h-3 rounded-full progress-bar" style="width: ${(value/total*100).toFixed(1)}%"></div>
                        </div>
                        <div class="text-left text-sm text-gray-500 mt-1">${(value/total*100).toFixed(1)}%</div>
                    </div>
                `).join('')}
            </div>
            
            <div class="bg-purple-50 rounded-xl p-6">
                <h3 class="text-xl font-bold mb-4">🔍 تحلیل گلوگاه‌ها</h3>
                <div class="space-y-4">
                    <div class="bg-white rounded-lg p-4">
                        <div class="text-sm text-gray-600 mb-1">⏱️ میانگین زمان در بررسی نشده</div>
                        <div class="text-2xl font-bold text-purple-600">${status.avg_days_pending || 0} روز</div>
                    </div>
                    <div class="bg-white rounded-lg p-4">
                        <div class="text-sm text-gray-600 mb-1">⚠️ واحد با بیشترین کار مانده</div>
                        <div class="text-xl font-bold text-red-600">${status.worst_sender_pending?.unit || '—'}</div>
                        <div class="text-sm text-gray-500">${status.worst_sender_pending?.count || 0} کار بررسی نشده</div>
                    </div>
                    <div class="bg-white rounded-lg p-4">
                        <div class="text-sm text-gray-600 mb-1">📥 گیرنده با بیشترین کار در حال پیگیری</div>
                        <div class="text-xl font-bold text-blue-600">${status.receiver_with_most_in_progress?.receiver || '—'}</div>
                        <div class="text-sm text-gray-500">${status.receiver_with_most_in_progress?.count || 0} کار</div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderSubjectAnalysis() {
    const subject = analysisData?.subject_analysis || {};
    const subjects = subject.subject_pending || {};
    const responseTimes = subject.subject_response_time || {};
    
    return `
        <div class="grid md:grid-cols-2 gap-6">
            <div>
                <h3 class="text-xl font-bold mb-4">📌 موضوعات پرتکرار</h3>
                <div class="bg-purple-50 rounded-xl p-4 mb-4">
                    <div class="text-lg mb-2">🏆 پرتکرارترین:</div>
                    <div class="bg-white rounded-lg p-4 flex justify-between items-center">
                        <span class="font-bold">${subject.most_frequent_subject || '—'}</span>
                        <span class="bg-purple-600 text-white px-4 py-2 rounded-full">${subject.subject_frequency || 0} بار</span>
                    </div>
                </div>
                
                <h4 class="font-bold mb-3">⏱️ میانگین زمان پاسخگویی</h4>
                <div class="space-y-3">
                    ${Object.entries(responseTimes).map(([subj, time]) => `
                        <div class="bg-gray-50 rounded-lg p-3 flex justify-between items-center">
                            <span>${subj}</span>
                            <span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full">${time} روز</span>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div>
                <h3 class="text-xl font-bold mb-4">⏳ موضوعات با کار مانده</h3>
                <div class="space-y-4">
                    ${Object.entries(subjects).map(([subj, count]) => `
                        <div class="bg-orange-50 rounded-lg p-4">
                            <div class="flex justify-between items-center mb-2">
                                <span class="font-semibold">${subj}</span>
                                <span class="bg-orange-600 text-white px-3 py-1 rounded-full text-sm">${count} مانده</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

function renderUnitAnalysis() {
    const senderReceiver = analysisData?.sender_receiver_analysis || {};
    
    return `
        <div class="grid md:grid-cols-2 gap-6">
            <div class="bg-blue-50 rounded-xl p-6">
                <h3 class="text-xl font-bold mb-4 flex items-center">
                    <i class="fas fa-paper-plane text-blue-600 ml-2"></i>
                    پرکارترین فرستنده‌ها
                </h3>
                <div class="space-y-3">
                    ${(senderReceiver.top_senders || []).map(s => `
                        <div class="bg-white rounded-lg p-4 flex justify-between items-center">
                            <span class="font-semibold">${s.sender}</span>
                            <span class="bg-blue-600 text-white px-3 py-1 rounded-full">${s.count} ارجاع</span>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="bg-green-50 rounded-xl p-6">
                <h3 class="text-xl font-bold mb-4 flex items-center">
                    <i class="fas fa-inbox text-green-600 ml-2"></i>
                    پرکارترین گیرنده‌ها
                </h3>
                <div class="space-y-3">
                    ${(senderReceiver.top_receivers || []).map(r => `
                        <div class="bg-white rounded-lg p-4 flex justify-between items-center">
                            <span class="font-semibold">${r.receiver}</span>
                            <span class="bg-green-600 text-white px-3 py-1 rounded-full">${r.count} ارجاع</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>

        <div class="mt-6 bg-purple-50 rounded-xl p-6">
            <h3 class="text-xl font-bold mb-4">🔄 الگوهای همکاری</h3>
            <div class="grid md:grid-cols-2 gap-4">
                ${(senderReceiver.common_pairs || []).map(p => `
                    <div class="bg-white rounded-lg p-4 flex items-center justify-between">
                        <div class="flex items-center">
                            <span class="font-bold text-purple-600">${p.from}</span>
                            <i class="fas fa-arrow-left mx-3 text-gray-400"></i>
                            <span class="font-bold text-indigo-600">${p.to}</span>
                        </div>
                        <span class="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">${p.count} بار</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function renderCustomerAnalysis() {
    const institution = analysisData?.institution_analysis || {};
    
    return `
        <div class="grid md:grid-cols-2 gap-6">
            <div class="bg-yellow-50 rounded-xl p-6">
                <h3 class="text-xl font-bold mb-4">🏢 مشتریان فعال</h3>
                <div class="space-y-4">
                    ${(institution.top_institutions || []).map(inst => `
                        <div class="bg-white rounded-lg p-4">
                            <div class="flex justify-between items-center mb-2">
                                <span class="font-bold">${inst.name}</span>
                                <span class="bg-yellow-600 text-white px-3 py-1 rounded-full text-sm">${inst.count} ارجاع</span>
                            </div>
                            <div class="text-sm text-gray-600">اشتراک: ${inst.subs || '—'}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="bg-indigo-50 rounded-xl p-6">
                <h3 class="text-xl font-bold mb-4">📊 تحلیل اشتراک</h3>
                <div class="bg-white rounded-lg p-6 text-center">
                    <div class="text-5xl font-bold text-indigo-600 mb-2">${institution.subscription_correlation || 0}</div>
                    <div class="text-gray-600">همبستگی اشتراک و تعداد ارجاع</div>
                    <div class="mt-4 text-sm text-gray-500">
                        ${institution.subscription_correlation > 0.5 ? 'همبستگی مثبت قوی' : 'همبستگی ضعیف'}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderInsights() {
    const insights = analysisData?.comprehensive_insights || {};
    
    return `
        <div class="space-y-6">
            <div class="bg-yellow-50 rounded-xl p-8 border-r-4 border-yellow-500">
                <h3 class="text-xl font-bold mb-4 flex items-center">
                    <i class="fas fa-lightbulb text-3xl text-yellow-600 ml-3"></i>
                    بینش‌های کلیدی
                </h3>
                <ul class="space-y-4">
                    ${(insights.recurring_patterns || []).map(p => `
                        <li class="flex items-start bg-white rounded-lg p-4">
                            <span class="bg-yellow-200 text-yellow-800 px-3 py-1 rounded-full text-sm ml-3 font-bold">${p.frequency}</span>
                            <span class="text-gray-700">${p.pattern}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>

            <div class="grid md:grid-cols-2 gap-6">
                <div class="bg-green-50 rounded-xl p-6">
                    <h3 class="text-xl font-bold mb-4 flex items-center">
                        <i class="fas fa-check-circle text-green-600 ml-2"></i>
                        عوامل موفقیت
                    </h3>
                    <div class="space-y-3">
                        ${(insights.completion_factors || []).map(f => `
                            <div class="bg-white rounded-lg p-3 flex items-center">
                                <i class="fas fa-check text-green-600 ml-2"></i>
                                <span>${f}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="bg-purple-50 rounded-xl p-6">
                    <h3 class="text-xl font-bold mb-4 flex items-center">
                        <i class="fas fa-handshake text-purple-600 ml-2"></i>
                        واحدهای همکار
                    </h3>
                    <div class="space-y-3">
                        ${(insights.collaborating_units || []).map(c => `
                            <div class="bg-white rounded-lg p-4">
                                <div class="flex items-center justify-between">
                                    <div class="flex items-center">
                                        <i class="fas fa-exchange-alt text-purple-600 ml-3"></i>
                                        <span class="font-semibold">${c.units?.join(' ← ') || ''}</span>
                                    </div>
                                    <span class="bg-purple-600 text-white px-3 py-1 rounded-full text-sm">
                                        ${((c.success_rate || 0) * 100).toFixed(0)}%
                                    </span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>

            <div class="bg-blue-50 rounded-xl p-6">
                <h3 class="text-xl font-bold mb-4">📈 تأثیر توضیحات</h3>
                <div class="flex items-center justify-between">
                    <span class="text-lg">آیا توضیحات کامل‌تر باعث اتمام سریع‌تر می‌شود؟</span>
                    <span class="bg-blue-600 text-white px-6 py-3 rounded-full font-bold">
                        ${insights.description_impact ? '✅ بله' : '❌ خیر'}
                    </span>
                </div>
            </div>
        </div>
    `;
}

// ========================================
// CHART FUNCTIONS
// ========================================

function createOverviewCharts() {
    const status = analysisData?.status_analysis || {};
    const dist = status.status_distribution || {};
    
    // Pie Chart
    const pieCtx = document.getElementById('status-pie-chart');
    if (pieCtx && Object.keys(dist).length > 0) {
        charts.statusPie = new Chart(pieCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(dist),
                datasets: [{
                    data: Object.values(dist),
                    backgroundColor: [
                        '#ef4444', '#f59e0b', '#3b82f6', '#10b981', '#8b5cf6'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom', labels: { font: { family: 'Vazir' } } }
                }
            }
        });
    }

    // Trend Chart
    const trendCtx = document.getElementById('daily-trend-chart');
    if (trendCtx) {
        const dailyCounts = status.daily_counts || {};
        
        if (Object.keys(dailyCounts).length > 0) {
            charts.dailyTrend = new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: Object.keys(dailyCounts),
                    datasets: [{
                        label: 'تعداد ارجاع',
                        data: Object.values(dailyCounts),
                        borderColor: '#8b5cf6',
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
                }
            });
        } else {
            // نمایش پیام جایگزین
            trendCtx.parentNode.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <i class="fas fa-chart-line text-4xl mb-3 opacity-50"></i>
                    <p>داده‌ای برای نمایش روند روزانه وجود ندارد</p>
                </div>
            `;
        }
    }
}

function createStatusCharts() {
    // می‌تونید چارت‌های دیگه رو هم اینجا اضافه کنید
}