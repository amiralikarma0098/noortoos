let analyses = [];

// بارگذاری لیست تحلیل‌ها
async function loadAnalyses() {
    try {
        const response = await fetch('/api/history');
        analyses = await response.json();

        document.getElementById('loading').classList.add('hidden');

        if (analyses.length === 0) {
            document.getElementById('empty-state').classList.remove('hidden');
        } else {
            renderTable();
            document.getElementById('table-container').classList.remove('hidden');
        }
    } catch (error) {
        console.error('خطا در بارگذاری:', error);
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('empty-state').classList.remove('hidden');
    }
}

// رندر جدول
function renderTable() {
    const tbody = document.getElementById('analyses-tbody');
    tbody.innerHTML = '';

    analyses.forEach((analysis, index) => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 cursor-pointer transition';
        row.onclick = () => showDetail(analysis.id);

        const date = new Date(analysis.created_at);
        const dateStr = date.toLocaleDateString('fa-IR', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${index + 1}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <i class="fas fa-file-alt text-purple-600 ml-2"></i>
                    <span class="text-sm font-medium text-gray-900">${analysis.file_name}</span>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${dateStr}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${analysis.seller_name || '—'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${analysis.customer_name || '—'}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-semibold rounded-full ${getScoreColor(analysis.score_total)}">
                    ${analysis.score_total || 0}/10
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                ${analysis.total_calls || 0} (${analysis.successful_calls || 0} موفق)
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                <button onclick="event.stopPropagation(); downloadFile(${analysis.id})" 
                        class="text-blue-600 hover:text-blue-800 ml-3">
                    <i class="fas fa-download"></i>
                </button>
                <button onclick="event.stopPropagation(); showDetail(${analysis.id})" 
                        class="text-green-600 hover:text-green-800">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        `;

        tbody.appendChild(row);
    });
}

function getScoreColor(score) {
    if (score >= 8) return 'bg-green-100 text-green-800';
    if (score >= 6) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
}

// نمایش جزئیات کامل
async function showDetail(id) {
    try {
        const response = await fetch(`/api/analysis/${id}`);
        const analysis = await response.json();

        // Parse JSON if needed
        let fullAnalysis = analysis.full_analysis;
        if (typeof fullAnalysis === 'string') {
            fullAnalysis = JSON.parse(fullAnalysis);
        }

        const content = document.getElementById('modal-content');
        content.innerHTML = renderCompleteAnalysis(analysis, fullAnalysis);

        document.getElementById('detail-modal').classList.remove('hidden');

    } catch (error) {
        console.error('خطا در بارگذاری جزئیات:', error);
        alert('خطا در بارگذاری جزئیات');
    }
}

function renderCompleteAnalysis(analysis, fullData) {
    const {
        فیلدهای_عددی: nums = {},
        فیلدهای_متنی: text = {},
        لیست_ها: lists = {},
        آمار: stats = {},
        بهترین_ها: best = {},
        دلایل_کاهش_امتیازها: reasons_dec = {},
        دلایل_کسب_امتیازها: reasons_inc = {}
    } = fullData || {};
    return `
        <div class="space-y-6">
            
            <!-- بخش 1: اطلاعات فایل -->
            <div class="modal-section">
                <h3 class="section-title">
                    <i class="fas fa-file-alt text-blue-600 ml-2"></i>
                    اطلاعات فایل و تماس
                </h3>
                <div class="grid md:grid-cols-2 gap-4">
                    <div class="data-row"><span class="data-label">نام فایل:</span><span class="data-value">${analysis.file_name}</span></div>
                    <div class="data-row"><span class="data-label">تاریخ تحلیل:</span><span class="data-value">${new Date(analysis.created_at).toLocaleString('fa-IR')}</span></div>
                    <div class="data-row"><span class="data-label">نام فروشنده:</span><span class="data-value">${text.نام_فروشنده || '—'}</span></div>
                    <div class="data-row"><span class="data-label">کد فروشنده:</span><span class="data-value">${text.کد_فروشنده || '—'}</span></div>
                    <div class="data-row"><span class="data-label">نام مشتری:</span><span class="data-value">${text.نام_مشتری || '—'}</span></div>
                    <div class="data-row"><span class="data-label">محصول/خدمت:</span><span class="data-value">${text.محصول || '—'}</span></div>
                    <div class="data-row"><span class="data-label">مدت تماس:</span><span class="data-value">${text.مدت_تماس || '—'}</span></div>
                    <div class="data-row"><span class="data-label">نوع تماس (جهت):</span><span class="data-value">${text.نوع_تماس_جهت || '—'}</span></div>
                    <div class="data-row"><span class="data-label">نوع تماس (مرحله):</span><span class="data-value">${text.نوع_تماس_مرحله || '—'}</span></div>
                    <div class="data-row"><span class="data-label">نوع تماس (گرمی):</span><span class="data-value">${text.نوع_تماس_گرمی || '—'}</span></div>
                    <div class="data-row"><span class="data-label">نوع تماس (ماهیت):</span><span class="data-value">${text.نوع_تماس_ماهیت || '—'}</span></div>
                    <div class="data-row"><span class="data-label">سطح فروشنده:</span><span class="data-value">${text.سطح_فروشنده || '—'}</span></div>
                </div>
            </div>

            <!-- بخش 2: امتیازها (10 تا) -->
            <div class="modal-section bg-gradient-to-r from-purple-50 to-blue-50">
                <h3 class="section-title">
                    <i class="fas fa-star text-purple-600 ml-2"></i>
                    امتیازهای جزئی (0-10)
                </h3>
                <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
                    ${renderScoreCard('امتیاز کل', nums.امتیاز_کل)}
                    ${renderScoreCard('برقراری ارتباط', nums.امتیاز_برقراری_ارتباط)}
                    ${renderScoreCard('نیازسنجی', nums.امتیاز_نیازسنجی)}
                    ${renderScoreCard('ارزش فروشی', nums.امتیاز_ارزش_فروشی)}
                    ${renderScoreCard('مدیریت اعتراض', nums.امتیاز_مدیریت_اعتراض)}
                    ${renderScoreCard('شفافیت قیمت', nums.امتیاز_شفافیت_قیمت)}
                    ${renderScoreCard('بستن فروش', nums.امتیاز_بستن_فروش)}
                    ${renderScoreCard('پیگیری', nums.امتیاز_پیگیری)}
                    ${renderScoreCard('همسویی احساسی', nums.امتیاز_همسویی_احساسی)}
                    ${renderScoreCard('شنوندگی', nums.امتیاز_شنوندگی)}
                </div>
            </div>

            <!-- بخش 3: فیلدهای عددی اضافی -->
            <div class="modal-section bg-gradient-to-r from-green-50 to-teal-50">
                <h3 class="section-title">
                    <i class="fas fa-chart-line text-green-600 ml-2"></i>
                    شاخص‌های عددی
                </h3>
                <div class="grid md:grid-cols-3 gap-4">
                    <div class="bg-white p-4 rounded shadow-sm">
                        <div class="text-xs text-gray-600 mb-1">کیفیت لید</div>
                        <div class="text-2xl font-bold text-green-600">${nums.کیفیت_لید_درصد || 0}%</div>
                    </div>
                    <div class="bg-white p-4 rounded shadow-sm">
                        <div class="text-xs text-gray-600 mb-1">تعداد سوالات باز</div>
                        <div class="text-2xl font-bold text-blue-600">${nums.تعداد_سوالات_باز || 0}</div>
                    </div>
                    <div class="bg-white p-4 rounded shadow-sm">
                        <div class="text-xs text-gray-600 mb-1">تعداد اعتراض</div>
                        <div class="text-2xl font-bold text-orange-600">${nums.تعداد_اعتراض || 0}</div>
                    </div>
                    <div class="bg-white p-4 rounded shadow-sm">
                        <div class="text-xs text-gray-600 mb-1">پاسخ موفق به اعتراض</div>
                        <div class="text-2xl font-bold text-green-600">${nums.درصد_پاسخ_موفق_به_اعتراض || 0}%</div>
                    </div>
                    <div class="bg-white p-4 rounded shadow-sm">
                        <div class="text-xs text-gray-600 mb-1">تلاش برای بستن</div>
                        <div class="text-2xl font-bold text-purple-600">${nums.تعداد_تلاش_برای_بستن || 0}</div>
                    </div>
                    <div class="bg-white p-4 rounded shadow-sm">
                        <div class="text-xs text-gray-600 mb-1">احساس مشتری</div>
                        <div class="text-2xl font-bold text-pink-600">${nums.امتیاز_احساس_مشتری || 0}/10</div>
                    </div>
                    <div class="bg-white p-4 rounded shadow-sm">
                        <div class="text-xs text-gray-600 mb-1">آمادگی بستن</div>
                        <div class="text-2xl font-bold text-green-600">${nums.آمادگی_بستن_درصد || 0}%</div>
                    </div>
                    <div class="bg-white p-4 rounded shadow-sm">
                        <div class="text-xs text-gray-600 mb-1">چگالی فنی فروشنده</div>
                        <div class="text-2xl font-bold text-indigo-600">${nums.چگالی_اطلاعات_فنی_فروشنده_درصد || 0}%</div>
                    </div>
                    <div class="bg-white p-4 rounded shadow-sm">
                        <div class="text-xs text-gray-600 mb-1">چگالی فنی مشتری</div>
                        <div class="text-2xl font-bold text-indigo-600">${nums.چگالی_اطلاعات_فنی_مشتری_درصد || 0}%</div>
                    </div>
                    <div class="bg-white p-4 rounded shadow-sm">
                        <div class="text-xs text-gray-600 mb-1">حساسیت قیمت</div>
                        <div class="text-2xl font-bold text-red-600">${nums.حساسیت_قیمت_مشتری_درصد || 0}%</div>
                    </div>
                    <div class="bg-white p-4 rounded shadow-sm">
                        <div class="text-xs text-gray-600 mb-1">حساسیت ریسک</div>
                        <div class="text-2xl font-bold text-red-600">${nums.حساسیت_ریسک_مشتری_درصد || 0}%</div>
                    </div>
                    <div class="bg-white p-4 rounded shadow-sm">
                        <div class="text-xs text-gray-600 mb-1">حساسیت زمان</div>
                        <div class="text-2xl font-bold text-red-600">${nums.حساسیت_زمان_مشتری_درصد || 0}%</div>
                    </div>
                    <div class="bg-white p-4 rounded shadow-sm">
                        <div class="text-xs text-gray-600 mb-1">تعداد بله پله‌ای</div>
                        <div class="text-2xl font-bold text-green-600">${nums.تعداد_بله_پله_ای || 0}</div>
                    </div>
                </div>
            </div>

            <!-- بخش 4: DISC -->
            <div class="modal-section bg-gradient-to-r from-yellow-50 to-orange-50">
                <h3 class="section-title">
                    <i class="fas fa-users text-orange-600 ml-2"></i>
                    تحلیل شخصیت DISC
                </h3>
                <div class="grid md:grid-cols-2 gap-6">
                    <div>
                        <div class="grid grid-cols-2 gap-3 mb-4">
                            ${renderDISCCard('D - قاطعیت', nums.disc_d, 'red')}
                            ${renderDISCCard('I - تعامل', nums.disc_i, 'yellow')}
                            ${renderDISCCard('S - ثبات', nums.disc_s, 'green')}
                            ${renderDISCCard('C - دقت', nums.disc_c, 'blue')}
                        </div>
                        <div class="bg-white p-4 rounded">
                            <div class="text-sm font-medium mb-2">تیپ غالب: <span class="text-lg font-bold text-purple-600">${text.disc_تیپ || '—'}</span></div>
                        </div>
                    </div>
                    <div class="space-y-3">
                        <div class="bg-white p-4 rounded">
                            <div class="text-sm font-bold mb-2">شواهد DISC:</div>
                            <ul class="text-sm space-y-1">
                                ${(text.disc_شواهد || []).map(s => `<li>• ${s}</li>`).join('') || '<li class="text-gray-500">شواهدی ثبت نشده</li>'}
                            </ul>
                        </div>
                        <div class="bg-white p-4 rounded">
                            <div class="text-sm font-bold mb-2">راهنمای تعامل:</div>
                            <p class="text-sm">${text.disc_راهنما || '—'}</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- بخش 5: نسبت‌ها و ترجیحات -->
            <div class="modal-section">
                <h3 class="section-title">
                    <i class="fas fa-balance-scale text-indigo-600 ml-2"></i>
                    نسبت‌ها و ترجیحات
                </h3>
                <div class="grid md:grid-cols-2 gap-4">
                    <div class="data-row"><span class="data-label">نسبت زمان صحبت (مشتری:فروشنده):</span><span class="data-value">${text.نسبت_زمان_صحبت_مشتری_به_فروشنده || '—'}</span></div>
                    <div class="data-row"><span class="data-label">نسبت زمان صحبت (فروشنده:مشتری):</span><span class="data-value">${text.نسبت_زمان_صحبت_فروشنده_به_مشتری || '—'}</span></div>
                    <div class="data-row"><span class="data-label">ترجیح کانال:</span><span class="data-value">${text.ترجیح_کانال || '—'}</span></div>
                    <div class="data-row"><span class="data-label">سطح آگاهی مشتری:</span><span class="data-value">${text.سطح_آگاهی_مشتری || '—'}</span></div>
                </div>
            </div>

            <!-- بخش 6: تحلیل‌های متنی -->
            <div class="modal-section bg-gradient-to-r from-blue-50 to-cyan-50">
                <h3 class="section-title">
                    <i class="fas fa-brain text-blue-600 ml-2"></i>
                    تحلیل‌های عمیق
                </h3>
                <div class="space-y-4">
                    <div class="bg-white p-4 rounded">
                        <div class="text-sm font-bold mb-2">خلاصه:</div>
                        <p class="text-sm">${text.خلاصه || '—'}</p>
                    </div>
                    <div class="bg-white p-4 rounded">
                        <div class="text-sm font-bold mb-2">تحلیل شخصیت مشتری:</div>
                        <p class="text-sm whitespace-pre-line">${text.تحلیل_شخصیت_مشتری || '—'}</p>
                    </div>
                    <div class="bg-white p-4 rounded">
                        <div class="text-sm font-bold mb-2">ارزیابی عملکرد فردی فروشنده:</div>
                        <p class="text-sm whitespace-pre-line">${text.ارزیابی_عملکرد_فردی_فروشنده || '—'}</p>
                    </div>
                    <div class="bg-white p-4 rounded">
                        <div class="text-sm font-bold mb-2">تشخیص آمادگی:</div>
                        <p class="text-sm">${text.تشخیص_آمادگی || '—'}</p>
                    </div>
                    <div class="bg-white p-4 rounded border-r-4 border-yellow-500">
                        <div class="text-sm font-bold mb-2">اقدام بعدی:</div>
                        <p class="text-sm">${text.اقدام_بعدی || '—'}</p>
                    </div>
                </div>
            </div>

            <!-- بخش 7: دلایل امتیازها -->
            <div class="modal-section">
                <h3 class="section-title">
                    <i class="fas fa-list-check text-purple-600 ml-2"></i>
                    دلایل کسب و کاهش امتیازها
                </h3>
                <div class="grid md:grid-cols-2 gap-4">
                    ${renderReasonsList('برقراری ارتباط', reasons_inc.برقراری_ارتباط, reasons_dec.برقراری_ارتباط)}
                    ${renderReasonsList('نیازسنجی', reasons_inc.نیازسنجی, reasons_dec.نیازسنجی)}
                    ${renderReasonsList('ارزش فروشی', reasons_inc.ارزش_فروشی, reasons_dec.ارزش_فروشی)}
                    ${renderReasonsList('مدیریت اعتراض', reasons_inc.مدیریت_اعتراض, reasons_dec.مدیریت_اعتراض)}
                    ${renderReasonsList('شفافیت قیمت', reasons_inc.شفافیت_قیمت, reasons_dec.شفافیت_قیمت)}
                    ${renderReasonsList('بستن فروش', reasons_inc.بستن_فروش, reasons_dec.بستن_فروش)}
                    ${renderReasonsList('پیگیری', reasons_inc.پیگیری, reasons_dec.پیگیری)}
                    ${renderReasonsList('همسویی احساسی', reasons_inc.همسویی_احساسی, reasons_dec.همسویی_احساسی)}
                    ${renderReasonsList('شنوندگی', reasons_inc.شنوندگی, reasons_dec.شنوندگی)}
                </div>
            </div>

            <!-- بخش 8: لیست‌ها -->
            <div class="modal-section">
                <h3 class="section-title">
                    <i class="fas fa-clipboard-list text-green-600 ml-2"></i>
                    نقاط قوت، ضعف و موارد دیگر
                </h3>
                <div class="grid md:grid-cols-2 gap-4">
                    ${renderList('نقاط قوت', lists.نقاط_قوت, 'green')}
                    ${renderList('نقاط ضعف', lists.نقاط_ضعف, 'red')}
                    ${renderList('اعتراضات', lists.اعتراضات, 'orange')}
                    ${renderList('تکنیک‌ها', lists.تکنیکها, 'blue')}
                    ${renderList('ریسک‌ها', lists.ریسک_ها, 'red')}
                    ${renderList('پارامترهای رعایت نشده', lists.پارامترهای_رعایت_نشده, 'yellow')}
                    ${renderList('اشتباهات رایج', lists.اشتباهات_رایج, 'purple')}
                </div>
            </div>

            <!-- بخش 9: کلمات کلیدی -->
            <div class="modal-section">
                <h3 class="section-title">
                    <i class="fas fa-key text-yellow-600 ml-2"></i>
                    کلمات کلیدی
                </h3>
                <div class="grid md:grid-cols-2 gap-4">
                    <div>
                        <div class="text-sm font-medium mb-2 text-green-700">کلمات مثبت:</div>
                        <div class="flex flex-wrap gap-2">
                            ${(lists.کلمات_مثبت || []).map(w => `<span class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs">${w}</span>`).join('')}
                        </div>
                    </div>
                    <div>
                        <div class="text-sm font-medium mb-2 text-red-700">کلمات منفی:</div>
                        <div class="flex flex-wrap gap-2">
                            ${(lists.کلمات_منفی || []).map(w => `<span class="px-3 py-1 bg-red-100 text-red-800 rounded-full text-xs">${w}</span>`).join('')}
                        </div>
                    </div>
                </div>
            </div>

            <!-- بخش 10: آمار -->
            <div class="modal-section bg-gradient-to-r from-gray-50 to-slate-50">
                <h3 class="section-title">
                    <i class="fas fa-chart-bar text-gray-600 ml-2"></i>
                    آمار کلی
                </h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                    <div class="bg-white p-4 rounded text-center">
                        <div class="text-3xl font-bold text-blue-600">${stats.تعداد_کل_تماس_ها || 0}</div>
                        <div class="text-xs text-gray-600">کل تماس‌ها</div>
                    </div>
                    <div class="bg-white p-4 rounded text-center">
                        <div class="text-3xl font-bold text-green-600">${stats.تماس_های_موفق || 0}</div>
                        <div class="text-xs text-gray-600">موفق</div>
                    </div>
                    <div class="bg-white p-4 rounded text-center">
                        <div class="text-3xl font-bold text-red-600">${stats.تماس_های_بی_پاسخ || 0}</div>
                        <div class="text-xs text-gray-600">بی‌پاسخ</div>
                    </div>
                    <div class="bg-white p-4 rounded text-center">
                        <div class="text-3xl font-bold text-orange-600">${stats.تماس_های_ارجاعی || 0}</div>
                        <div class="text-xs text-gray-600">ارجاعی</div>
                    </div>
                </div>
                
                <div class="grid md:grid-cols-2 gap-4">
                    <div class="bg-white p-4 rounded">
                        <div class="text-sm font-bold mb-3">کاربران فعال:</div>
                        <div class="space-y-2">
                            ${(stats.کاربران_فعال || []).map(user => {
                                if (typeof user === 'object') {
                                    return `<div class="flex justify-between bg-blue-50 p-2 rounded text-sm">
                                        <span>${user.نام}</span>
                                        <span class="font-bold">${user.تعداد_تماس || 0}</span>
                                    </div>`;
                                }
                                return `<div class="bg-blue-50 p-2 rounded text-sm">${user}</div>`;
                            }).join('')}
                        </div>
                    </div>
                    
                    <div class="bg-white p-4 rounded">
                        <div class="text-sm font-bold mb-3">مشتریان پرتماس:</div>
                        <div class="space-y-2">
                            ${(stats.مشتریان_پرتماس || []).map(customer => {
                                if (typeof customer === 'object') {
                                    return `<div class="flex justify-between bg-green-50 p-2 rounded text-sm">
                                        <span>${customer.نام}</span>
                                        <span class="font-bold">${customer.تعداد_تماس || 0}</span>
                                    </div>`;
                                }
                                return `<div class="bg-green-50 p-2 rounded text-sm">${customer}</div>`;
                            }).join('')}
                        </div>
                    </div>
                </div>
            </div>

            <!-- بخش 11: بهترین‌ها -->
            <div class="modal-section bg-gradient-to-r from-yellow-50 to-amber-50">
                <h3 class="section-title">
                    <i class="fas fa-trophy text-yellow-600 ml-2"></i>
                    بهترین‌ها
                </h3>
                <div class="grid md:grid-cols-2 gap-4">
                    <div class="bg-white p-6 rounded-lg border-2 border-yellow-300">
                        <div class="flex items-center mb-3">
                            <i class="fas fa-award text-3xl text-yellow-500 ml-3"></i>
                            <div>
                                <div class="text-sm text-gray-600">بهترین فروشنده</div>
                                <div class="text-xl font-bold">${best.بهترین_فروشنده?.نام || '—'}</div>
                            </div>
                        </div>
                        <p class="text-sm text-gray-700">${best.بهترین_فروشنده?.دلیل || 'دلیلی ثبت نشده'}</p>
                    </div>
                    
                    <div class="bg-white p-6 rounded-lg border-2 border-green-300">
                        <div class="flex items-center mb-3">
                            <i class="fas fa-star text-3xl text-green-500 ml-3"></i>
                            <div>
                                <div class="text-sm text-gray-600">بهترین مشتری</div>
                                <div class="text-xl font-bold">${best.بهترین_مشتری?.نام || '—'}</div>
                            </div>
                        </div>
                        <p class="text-sm text-gray-700">${best.بهترین_مشتری?.دلیل || 'دلیلی ثبت نشده'}</p>
                    </div>
                </div>
            </div>

            <!-- دکمه دانلود -->
            <div class="flex justify-center pt-4">
                <button onclick="downloadFile(${analysis.id})" class="px-8 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">
                    <i class="fas fa-download ml-2"></i>
                    دانلود فایل اصلی
                </button>
            </div>
        </div>
    `;
}

// Helper functions
function renderScoreCard(label, value) {
    const v = value || 0;
    const color = v >= 8 ? 'green' : v >= 6 ? 'yellow' : 'red';
    return `
        <div class="bg-white p-3 rounded text-center">
            <div class="text-xs text-gray-600 mb-1">${label}</div>
            <div class="text-2xl font-bold text-${color}-600">${v}</div>
            <div class="text-xs text-gray-500">/10</div>
        </div>
    `;
}

function renderDISCCard(label, value, color) {
    const v = value || 0;
    return `
        <div class="bg-white p-3 rounded">
            <div class="text-xs mb-1">${label}</div>
            <div class="text-xl font-bold text-${color}-600">${v}/10</div>
            <div class="w-full bg-gray-200 rounded h-2 mt-1">
                <div class="bg-${color}-500 h-2 rounded" style="width: ${v * 10}%"></div>
            </div>
        </div>
    `;
}

function renderReasonsList(title, increase, decrease) {
    return `
        <div class="bg-white p-4 rounded">
            <div class="text-sm font-bold mb-2">${title}</div>
            ${(increase && increase.length > 0) ? `
                <div class="mb-2">
                    <div class="text-xs text-green-700 font-medium">✓ کسب:</div>
                    <ul class="text-xs text-gray-700 mr-4">
                        ${increase.map(r => `<li>• ${r}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            ${(decrease && decrease.length > 0) ? `
                <div>
                    <div class="text-xs text-red-700 font-medium">✗ کاهش:</div>
                    <ul class="text-xs text-gray-700 mr-4">
                        ${decrease.map(r => `<li>• ${r}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
    `;
}

function renderList(title, items, color) {
    return `
        <div class="bg-${color}-50 p-4 rounded border border-${color}-200">
            <div class="text-sm font-bold mb-2">${title}</div>
            <ul class="text-xs space-y-1">
                ${(items || []).map(item => `<li>• ${item}</li>`).join('') || '<li class="text-gray-500">موردی ثبت نشده</li>'}
            </ul>
        </div>
    `;
}

function closeModal() {
    document.getElementById('detail-modal').classList.add('hidden');
}

function downloadFile(id) {
    window.open(`/api/file/${id}`, '_blank');
}

// بارگذاری اولیه
loadAnalyses();