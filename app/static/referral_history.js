// static/referral_history.js
(function() {
    if (window.__referralHistoryLoaded) return;
    window.__referralHistoryLoaded = true;
    
    console.log('✅ referral_history.js لود شد - مسیر:', window.location.pathname);
    
    if (!window.location.pathname.includes('/referral-history')) {
        console.log('⏭️ صفحه referral-history نیست، خروج...');
        return;
    }

    let currentPage = 1;
    let totalPages = 1;
    let analyses = [];
    let allAnalyses = [];

    // ========================================
    // INITIALIZATION
    // ========================================
    document.addEventListener('DOMContentLoaded', function() {
        console.log('📊 آماده‌سازی صفحه تاریخچه ارجاعیات...');
        loadHistory();
        
        // Event listeners برای فیلترها
        const searchInput = document.getElementById('search-input');
        if (searchInput) searchInput.addEventListener('input', filterTable);
        
        const successFilter = document.getElementById('success-rate-filter');
        if (successFilter) successFilter.addEventListener('change', filterTable);
        
        const bottleneckFilter = document.getElementById('bottleneck-filter');
        if (bottleneckFilter) bottleneckFilter.addEventListener('change', filterTable);
        
        const dateFrom = document.getElementById('date-from');
        if (dateFrom) dateFrom.addEventListener('change', filterTable);
        
        const dateTo = document.getElementById('date-to');
        if (dateTo) dateTo.addEventListener('change', filterTable);
        
        const prevBtn = document.getElementById('prev-page');
        if (prevBtn) prevBtn.addEventListener('click', () => changePage(currentPage - 1));
        
        const nextBtn = document.getElementById('next-page');
        if (nextBtn) nextBtn.addEventListener('click', () => changePage(currentPage + 1));
    });

    // ========================================
    // LOAD DATA
    // ========================================
    async function loadHistory() {
        try {
            console.log('📡 در حال دریافت داده‌ها از سرور...');
            
            const loadingEl = document.getElementById('loading');
            const tableContainer = document.getElementById('table-container');
            const emptyState = document.getElementById('empty-state');
            
            if (loadingEl) loadingEl.classList.remove('hidden');
            if (tableContainer) tableContainer.classList.add('hidden');
            if (emptyState) emptyState.classList.add('hidden');
            
            const response = await fetch('/api/referral-history');
            
            if (!response.ok) {
                throw new Error('خطا در دریافت داده‌ها');
            }
            
            allAnalyses = await response.json();
            analyses = [...allAnalyses];
            
            console.log(`✅ ${allAnalyses.length} رکورد دریافت شد:`, allAnalyses);
            
            if (loadingEl) loadingEl.classList.add('hidden');
            
            if (allAnalyses.length === 0) {
                if (emptyState) emptyState.classList.remove('hidden');
            } else {
                calculateOverallStats();
                renderTable();
                if (tableContainer) tableContainer.classList.remove('hidden');
            }
            
        } catch (error) {
            console.error('❌ خطا:', error);
            
            const loadingEl = document.getElementById('loading');
            const emptyState = document.getElementById('empty-state');
            
            if (loadingEl) loadingEl.classList.add('hidden');
            if (emptyState) {
                emptyState.classList.remove('hidden');
                emptyState.innerHTML = `
                    <div class="icon-box w-24 h-24 mx-auto mb-6">
                        <i class="fas fa-exclamation-triangle text-5xl text-red-500"></i>
                    </div>
                    <h3 class="text-2xl font-bold text-gray-800 mb-2">خطا در بارگذاری</h3>
                    <p class="text-gray-600 mb-8">${error.message}</p>
                    <button onclick="location.reload()" class="btn-primary px-8 py-4 rounded-xl">
                        تلاش مجدد
                    </button>
                `;
            }
        }
    }

    // ========================================
    // STATISTICS
    // ========================================
    function calculateOverallStats() {
        const totalAnalyses = allAnalyses.length;
        const totalReferrals = allAnalyses.reduce((sum, a) => sum + (a.total_referrals || 0), 0);
        const totalCompleted = allAnalyses.reduce((sum, a) => sum + (a.completed_count || 0), 0);
        const totalPending = allAnalyses.reduce((sum, a) => sum + (a.pending_count || 0), 0);
        
        // واحدهای گلوگاه پرتکرار
        const bottlenecks = allAnalyses.map(a => a.bottleneck_unit).filter(Boolean);
        const topBottleneck = getMostFrequent(bottlenecks);
        
        const statsContainer = document.getElementById('overall-stats');
        if (!statsContainer) return;
        
        statsContainer.innerHTML = `
            <div class="stat-card bg-purple-50 rounded-xl p-4">
                <i class="fas fa-chart-bar text-2xl text-purple-600 mb-2"></i>
                <div class="text-2xl font-bold text-purple-600">${totalAnalyses}</div>
                <div class="text-sm text-gray-600">کل تحلیل‌ها</div>
            </div>
            <div class="stat-card bg-blue-50 rounded-xl p-4">
                <i class="fas fa-phone-alt text-2xl text-blue-600 mb-2"></i>
                <div class="text-2xl font-bold text-blue-600">${totalReferrals}</div>
                <div class="text-sm text-gray-600">کل ارجاعات</div>
            </div>
            <div class="stat-card bg-green-50 rounded-xl p-4">
                <i class="fas fa-check-circle text-2xl text-green-600 mb-2"></i>
                <div class="text-2xl font-bold text-green-600">${totalCompleted}</div>
                <div class="text-sm text-gray-600">اتمام یافته</div>
            </div>
            <div class="stat-card bg-yellow-50 rounded-xl p-4">
                <i class="fas fa-clock text-2xl text-yellow-600 mb-2"></i>
                <div class="text-2xl font-bold text-yellow-600">${totalPending}</div>
                <div class="text-sm text-gray-600">بررسی نشده</div>
            </div>
            <div class="stat-card bg-red-50 rounded-xl p-4">
                <i class="fas fa-exclamation-triangle text-2xl text-red-600 mb-2"></i>
                <div class="text-2xl font-bold text-red-600">${topBottleneck || '—'}</div>
                <div class="text-sm text-gray-600">گلوگاه اصلی</div>
            </div>
        `;
    }

    function getMostFrequent(arr) {
        if (!arr.length) return null;
        const counts = arr.reduce((acc, val) => {
            acc[val] = (acc[val] || 0) + 1;
            return acc;
        }, {});
        return Object.keys(counts).reduce((a, b) => counts[a] > counts[b] ? a : b);
    }

    // ========================================
    // TABLE RENDERING
    // ========================================
    function renderTable() {
        const tbody = document.getElementById('history-table-body');
        if (!tbody) return;
        
        const filtered = filterAnalyses();
        
        totalPages = Math.ceil(filtered.length / 10);
        const start = (currentPage - 1) * 10;
        const end = start + 10;
        const pageData = filtered.slice(start, end);
        
        if (pageData.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="11" class="text-center py-8 text-gray-500">
                        <i class="fas fa-inbox text-4xl mb-3 opacity-50"></i>
                        <p>هیچ داده‌ای یافت نشد</p>
                    </td>
                </tr>
            `;
        } else {
            tbody.innerHTML = pageData.map((item, index) => {
                const successRate = item.completion_rate || 0;
                const rateClass = successRate >= 70 ? 'bg-green-100 text-green-800' : 
                                 successRate >= 50 ? 'bg-yellow-100 text-yellow-800' : 
                                 'bg-red-100 text-red-800';
                
                return `
                    <tr class="border-b table-row-hover hover:bg-gray-50">
                        <td class="p-4">${start + index + 1}</td>
                        <td class="p-4 font-semibold">
                            <i class="fas fa-file-excel text-green-600 ml-2"></i>
                            ${item.file_name}
                        </td>
                        <td class="p-4">${formatDate(item.analyzed_at)}</td>
                        <td class="p-4 text-center font-bold">${item.total_referrals}</td>
                        <td class="p-4 text-center font-bold text-green-600">${item.completed_count}</td>
                        <td class="p-4 text-center">
                            <span class="px-3 py-1 rounded-full text-sm font-bold ${rateClass}">
                                ${successRate}%
                            </span>
                        </td>
                        <td class="p-4 text-center font-bold text-red-600">${item.pending_count}</td>
                        <td class="p-4 text-center">
                            ${item.bottleneck_unit ? 
                                `<span class="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm">
                                    ${item.bottleneck_unit}
                                </span>` : 
                                '<span class="text-gray-400">—</span>'
                            }
                        </td>
                        <td class="p-4 text-center">
                            <span class="px-3 py-1 ${getHealthClass(item.health_score)} rounded-full text-sm font-bold">
                                ${item.health_score || '—'}
                            </span>
                        </td>
                        <td class="p-4 text-center">
                            ${item.risk_count > 0 ? 
                                `<span class="px-3 py-1 ${getRiskClass(item.risk_count)} text-white rounded-full text-sm font-bold">
                                    ${item.risk_count} ریسک
                                </span>` : 
                                '<span class="text-gray-400">—</span>'
                            }
                        </td>
                        <td class="p-4 text-center">
                            <button onclick="showDetails(${item.id})" class="action-btn text-purple-600 hover:text-purple-800 ml-2" title="مشاهده جزئیات">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button onclick="downloadReport(${item.id})" class="action-btn text-green-600 hover:text-green-800 ml-2" title="دانلود گزارش">
                                <i class="fas fa-download"></i>
                            </button>
                            <button onclick="confirmDelete(${item.id})" class="action-btn text-red-600 hover:text-red-800 ml-2" title="حذف">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');
        }
        
        updatePagination(filtered.length);
    }

    function formatDate(dateString) {
        if (!dateString) return '—';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('fa-IR', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (e) {
            return dateString;
        }
    }

    function getHealthClass(score) {
        if (!score) return 'bg-gray-100 text-gray-800';
        if (score >= 80) return 'bg-green-100 text-green-800';
        if (score >= 60) return 'bg-yellow-100 text-yellow-800';
        return 'bg-red-100 text-red-800';
    }

    function getRiskClass(count) {
        if (count > 2) return 'bg-red-600';
        if (count > 0) return 'bg-orange-600';
        return 'bg-gray-400';
    }

    // ========================================
    // FILTERING
    // ========================================
    function filterAnalyses() {
        const search = document.getElementById('search-input')?.value.toLowerCase() || '';
        const successRate = document.getElementById('success-rate-filter')?.value || 'all';
        const bottleneck = document.getElementById('bottleneck-filter')?.value || 'all';
        const from = document.getElementById('date-from')?.value || '';
        const to = document.getElementById('date-to')?.value || '';
        
        return allAnalyses.filter(a => {
            if (search && !a.file_name.toLowerCase().includes(search)) return false;
            
            const rate = a.completion_rate || 0;
            if (successRate === 'high' && rate < 70) return false;
            if (successRate === 'medium' && (rate < 50 || rate >= 70)) return false;
            if (successRate === 'low' && rate >= 50) return false;
            
            if (bottleneck === 'has-bottleneck' && !a.bottleneck_unit) return false;
            if (bottleneck === 'no-bottleneck' && a.bottleneck_unit) return false;
            
            const date = new Date(a.analyzed_at);
            if (from && date < new Date(from)) return false;
            if (to && date > new Date(to)) return false;
            
            return true;
        });
    }

    function filterTable() {
        currentPage = 1;
        renderTable();
    }

    // ========================================
    // PAGINATION
    // ========================================
    function updatePagination(totalItems) {
        const paginationInfo = document.getElementById('pagination-info');
        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');
        
        if (paginationInfo) {
            const start = (currentPage - 1) * 10 + 1;
            const end = Math.min(currentPage * 10, totalItems);
            paginationInfo.textContent = totalItems > 0 
                ? `نمایش ${start} تا ${end} از ${totalItems} رکورد`
                : 'هیچ رکوردی یافت نشد';
        }
        
        if (prevBtn) prevBtn.disabled = currentPage === 1;
        if (nextBtn) nextBtn.disabled = currentPage >= Math.ceil(totalItems / 10);
    }

    function changePage(newPage) {
        const totalItems = filterAnalyses().length;
        const maxPage = Math.ceil(totalItems / 10);
        
        if (newPage >= 1 && newPage <= maxPage) {
            currentPage = newPage;
            renderTable();
        }
    }

    // ========================================
    // DELETE FUNCTIONS
    // ========================================
    function confirmDelete(id) {
        if (confirm('آیا از حذف این رکورد اطمینان دارید؟ این عمل قابل بازگشت نیست.')) {
            deleteAnalysis(id);
        }
    }

    async function deleteAnalysis(id) {
        try {
            console.log('🗑️ در حال حذف تحلیل ارجاعیات:', id);
            
            const deleteBtn = document.querySelector(`button[onclick*="confirmDelete(${id})"]`);
            if (deleteBtn) {
                deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                deleteBtn.disabled = true;
            }
            
            const response = await fetch(`/api/referral-analysis/${id}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error('خطا در حذف رکورد');
            }
            
            allAnalyses = allAnalyses.filter(a => a.id !== id);
            
            calculateOverallStats();
            
            const filtered = filterAnalyses();
            const maxPage = Math.ceil(filtered.length / 10);
            if (currentPage > maxPage) {
                currentPage = maxPage || 1;
            }
            
            renderTable();
            alert('✅ رکورد با موفقیت حذف شد');
            
        } catch (error) {
            console.error('❌ خطا در حذف:', error);
            alert('خطا در حذف رکورد');
            
            const deleteBtn = document.querySelector(`button[onclick*="confirmDelete(${id})"]`);
            if (deleteBtn) {
                deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
                deleteBtn.disabled = false;
            }
        }
    }

    // ========================================
    // DETAILS MODAL
    // ========================================
    async function showDetails(id) {
        try {
            console.log('📡 دریافت جزئیات تحلیل:', id);
            
            const modal = document.getElementById('detail-modal');
            const content = document.getElementById('modal-content');
            
            if (!modal || !content) return;
            
            content.innerHTML = `
                <div class="text-center py-12">
                    <div class="loader mx-auto mb-4"></div>
                    <p class="text-gray-600">در حال دریافت اطلاعات...</p>
                </div>
            `;
            
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            
            const response = await fetch(`/api/referral-analysis/${id}`);
            
            if (!response.ok) {
                throw new Error('خطا در دریافت جزئیات');
            }
            
            const data = await response.json();
            content.innerHTML = renderDetailedAnalysis(data);
            
        } catch (error) {
            console.error('❌ خطا:', error);
            alert('خطا در دریافت جزئیات');
            
            const modal = document.getElementById('detail-modal');
            if (modal) {
                modal.classList.add('hidden');
                modal.classList.remove('flex');
            }
        }
    }

    function renderDetailedAnalysis(data) {
        const full = data.full_analysis || {};
        const status = full.status_analysis || {};
        const insights = full.comprehensive_insights || {};
        
        return `
            <div class="space-y-6">
                <!-- ردیف اول: آمار کلی -->
                <div class="grid grid-cols-5 gap-4">
                    <div class="bg-purple-50 p-4 rounded-xl text-center">
                        <i class="fas fa-chart-bar text-2xl text-purple-600 mb-2"></i>
                        <div class="text-2xl font-bold text-purple-600">${data.total_referrals}</div>
                        <div class="text-sm">کل ارجاعات</div>
                    </div>
                    <div class="bg-green-50 p-4 rounded-xl text-center">
                        <i class="fas fa-check-circle text-2xl text-green-600 mb-2"></i>
                        <div class="text-2xl font-bold text-green-600">${data.completed_count}</div>
                        <div class="text-sm">اتمام یافته</div>
                    </div>
                    <div class="bg-red-50 p-4 rounded-xl text-center">
                        <i class="fas fa-clock text-2xl text-red-600 mb-2"></i>
                        <div class="text-2xl font-bold text-red-600">${data.pending_count}</div>
                        <div class="text-sm">بررسی نشده</div>
                    </div>
                    <div class="bg-yellow-50 p-4 rounded-xl text-center">
                        <i class="fas fa-percent text-2xl text-yellow-600 mb-2"></i>
                        <div class="text-2xl font-bold text-yellow-600">${data.completion_rate}%</div>
                        <div class="text-sm">نرخ موفقیت</div>
                    </div>
                    <div class="bg-indigo-50 p-4 rounded-xl text-center">
                        <i class="fas fa-heartbeat text-2xl text-indigo-600 mb-2"></i>
                        <div class="text-2xl font-bold text-indigo-600">${insights.workflow_health_score || '—'}</div>
                        <div class="text-sm">امتیاز سلامت</div>
                    </div>
                </div>

                <!-- توزیع وضعیت‌ها -->
                <div class="bg-gray-50 p-6 rounded-xl">
                    <h4 class="font-bold text-lg mb-4">📊 توزیع وضعیت‌ها</h4>
                    <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
                        ${Object.entries(status.status_distribution || {}).map(([key, value]) => `
                            <div class="bg-white p-3 rounded-lg text-center">
                                <div class="font-semibold text-sm mb-1">${key}</div>
                                <div class="text-xl font-bold text-purple-600">${value}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- بینش‌ها و توصیه‌ها -->
                <div class="bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-6 rounded-xl">
                    <h4 class="text-xl font-bold mb-4">💡 بینش‌های هوشمند</h4>
                    <p class="text-lg leading-relaxed mb-4 opacity-90">${insights.summary_fa || ''}</p>
                    
                    ${insights.recommendations_fa ? `
                        <h5 class="font-bold text-lg mb-3">توصیه‌ها:</h5>
                        <ul class="space-y-2">
                            ${insights.recommendations_fa.map(rec => `
                                <li class="flex items-start gap-2 bg-white bg-opacity-20 rounded-lg p-3">
                                    <i class="fas fa-check-circle text-green-300 mt-1"></i>
                                    <span>${rec}</span>
                                </li>
                            `).join('')}
                        </ul>
                    ` : ''}
                </div>
            </div>
        `;
    }

    function closeModal() {
        const modal = document.getElementById('detail-modal');
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }
    }

    async function downloadReport(id) {
        window.location.href = `/api/referral-report/${id}`;
    }

    function refreshData() {
        loadHistory();
    }

    function exportAllData() {
        window.location.href = '/api/referral-export-all';
    }

    // ========================================
    // EXPORT TO WINDOW
    // ========================================
    window.showDetails = showDetails;
    window.closeModal = closeModal;
    window.downloadReport = downloadReport;
    window.refreshData = refreshData;
    window.exportAllData = exportAllData;
    window.confirmDelete = confirmDelete;
})();