// ========================================
// ENTERPRISE CRM ANALYZER - MAIN JS
// Version: 2.0 - Complete Edition
// ========================================

// let selectedFile = null; // این خط رو کامنت کن
//let analysisData = null;
let currentTab = 'overview';
let charts = {};

// ========================================
// INITIALIZATION
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    initializeUploadArea();
    initializeAnalyzeButton();
});

function initializeUploadArea() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');

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
    document.getElementById('analyze-btn').addEventListener('click', analyzeFile);
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
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('خطا در تحلیل فایل');
        }

        let data = await response.json();

        console.log('✅ داده دریافت شد:', data);

        if (data.error) {
            console.error('❌ خطا در سرور:', data.message);
            alert(data.message);
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('upload-section').classList.remove('hidden');
            return;
        }

        console.log('🔄 تبدیل ساختار...');
        analysisData = convertNewToOldStructure(data);
        console.log('✅ ساختار تبدیل شد:', analysisData);

        console.log('🎭 پنهان کردن loading...');
        document.getElementById('loading').classList.add('hidden');

        console.log('🎬 نمایش results...');
        document.getElementById('results').classList.remove('hidden');

        console.log('📊 نمایش تب overview...');
        showTab('overview');

    } catch (error) {
        console.error('❌ خطای جاوااسکریپت:', error);
        console.error('Stack:', error.stack);
        alert('خطا در تحلیل فایل: ' + error.message);
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('upload-section').classList.remove('hidden');
    }
}

// ========================================
// DATA CONVERTER - CRITICAL FUNCTION
// ========================================

function convertNewToOldStructure(data) {
    // اگر ساختار قدیمی است، همون رو برگردون
    if (data.امتیازها) {
        return data;
    }

    // تبدیل ساختار جدید به قدیم
    const nums = data.فیلدهای_عددی || {};
    const text = data.فیلدهای_متنی || {};
    const lists = data.لیست_ها || {};
    const stats = data.آمار || {};
    const best = data.بهترین_ها || {};
    const reasons_dec = data.دلایل_کاهش_امتیازها || {};
    const reasons_inc = data.دلایل_کسب_امتیازها || {};

    return {
        // امتیازها (10 تا)
        امتیازها: {
            امتیاز_کل: nums.امتیاز_کل || 0,
            برقراری_ارتباط: nums.امتیاز_برقراری_ارتباط || 0,
            نیازسنجی: nums.امتیاز_نیازسنجی || 0,
            ارزش_فروشی: nums.امتیاز_ارزش_فروشی || 0,
            مدیریت_اعتراض: nums.امتیاز_مدیریت_اعتراض || 0,
            شفافیت_قیمت: nums.امتیاز_شفافیت_قیمت || 0,
            بستن_فروش: nums.امتیاز_بستن_فروش || 0,
            پیگیری: nums.امتیاز_پیگیری || 0,
            همسویی_احساسی: nums.امتیاز_همسویی_احساسی || 0,
            شنوندگی: nums.امتیاز_شنوندگی || 0
        },

        // DISC (4 تا)
        DISC: {
            disc_d: nums.disc_d || 0,
            disc_i: nums.disc_i || 0,
            disc_s: nums.disc_s || 0,
            disc_c: nums.disc_c || 0
        },

        // فیلدهای عددی اضافی (17 تا)
        فیلدهای_عددی: {
            امتیاز_کل: nums.امتیاز_کل || 0,
            امتیاز_برقراری_ارتباط: nums.امتیاز_برقراری_ارتباط || 0,
            امتیاز_نیازسنجی: nums.امتیاز_نیازسنجی || 0,
            امتیاز_ارزش_فروشی: nums.امتیاز_ارزش_فروشی || 0,
            امتیاز_مدیریت_اعتراض: nums.امتیاز_مدیریت_اعتراض || 0,
            امتیاز_شفافیت_قیمت: nums.امتیاز_شفافیت_قیمت || 0,
            امتیاز_بستن_فروش: nums.امتیاز_بستن_فروش || 0,
            امتیاز_پیگیری: nums.امتیاز_پیگیری || 0,
            امتیاز_همسویی_احساسی: nums.امتیاز_همسویی_احساسی || 0,
            امتیاز_شنوندگی: nums.امتیاز_شنوندگی || 0,
            کیفیت_لید_درصد: nums.کیفیت_لید_درصد || 0,
            تعداد_سوالات_باز: nums.تعداد_سوالات_باز || 0,
            تعداد_اعتراض: nums.تعداد_اعتراض || 0,
            درصد_پاسخ_موفق_به_اعتراض: nums.درصد_پاسخ_موفق_به_اعتراض || 0,
            تعداد_تلاش_برای_بستن: nums.تعداد_تلاش_برای_بستن || 0,
            امتیاز_احساس_مشتری: nums.امتیاز_احساس_مشتری || 0,
            آمادگی_بستن_درصد: nums.آمادگی_بستن_درصد || 0,
            چگالی_اطلاعات_فنی_فروشنده_درصد: nums.چگالی_اطلاعات_فنی_فروشنده_درصد || 0,
            چگالی_اطلاعات_فنی_مشتری_درصد: nums.چگالی_اطلاعات_فنی_مشتری_درصد || 0,
            disc_d: nums.disc_d || 0,
            disc_i: nums.disc_i || 0,
            disc_s: nums.disc_s || 0,
            disc_c: nums.disc_c || 0,
            حساسیت_قیمت_مشتری_درصد: nums.حساسیت_قیمت_مشتری_درصد || 0,
            حساسیت_ریسک_مشتری_درصد: nums.حساسیت_ریسک_مشتری_درصد || 0,
            حساسیت_زمان_مشتری_درصد: nums.حساسیت_زمان_مشتری_درصد || 0,
            تعداد_بله_پله_ای: nums.تعداد_بله_پله_ای || 0
        },

        // متنی (21 تا)
        فیلدهای_متنی: {

            نام_فروشنده: text.نام_فروشنده || '—',
            کد_فروشنده: text.کد_فروشنده || '—',
            نام_مشتری: text.نام_مشتری || '—',
            مدت_تماس: text.مدت_تماس || '—',
            نوع_تماس_جهت: text.نوع_تماس_جهت || '—',
            نوع_تماس_مرحله: text.نوع_تماس_مرحله || '—',
            نوع_تماس_گرمی: text.نوع_تماس_گرمی || '—',
            نوع_تماس_ماهیت: text.نوع_تماس_ماهیت || '—',
            نوع_تماس: text.نوع_تماس_ماهیت || '—',
            محصول: text.محصول || '—',
            سطح_فروشنده: text.سطح_فروشنده || '—',
            disc_تیپ: text.disc_تیپ || '—',
            disc_شواهد: text.disc_شواهد || [],
            disc_راهنما: text.disc_راهنما || '—',
            ترجیح_کانال: text.ترجیح_کانال || '—',
            سطح_آگاهی_مشتری: text.سطح_آگاهی_مشتری || '—',
            نسبت_زمان_صحبت_مشتری_به_فروشنده: text.نسبت_زمان_صحبت_مشتری_به_فروشنده || '—',
            نسبت_زمان_صحبت_فروشنده_به_مشتری: text.نسبت_زمان_صحبت_فروشنده_به_مشتری || '—',
            خلاصه: text.خلاصه || 'خلاصه‌ای در دسترس نیست',
            تحلیل_شخصیت_مشتری: text.تحلیل_شخصیت_مشتری || 'تحلیلی در دسترس نیست',
            ارزیابی_عملکرد_فردی_فروشنده: text.ارزیابی_عملکرد_فردی_فروشنده || 'ارزیابی‌ای در دسترس نیست',
            تشخیص_آمادگی: text.تشخیص_آمادگی || 'تشخیصی در دسترس نیست',
            اقدام_بعدی: text.اقدام_بعدی || 'اقدامی مشخص نشده'
        },

        // فیلدهای متنی کامل
        فیلدهای_متنی: {
            نام_فروشنده: text.نام_فروشنده || '—',
            کد_فروشنده: text.کد_فروشنده || '—',
            نام_مشتری: text.نام_مشتری || '—',
            مدت_تماس: text.مدت_تماس || '—',
            نوع_تماس_جهت: text.نوع_تماس_جهت || '—',
            نوع_تماس_مرحله: text.نوع_تماس_مرحله || '—',
            نوع_تماس_گرمی: text.نوع_تماس_گرمی || '—',
            نوع_تماس_ماهیت: text.نوع_تماس_ماهیت || '—',
            محصول: text.محصول || '—',
            سطح_فروشنده: text.سطح_فروشنده || '—',
            disc_تیپ: text.disc_تیپ || '—',
            disc_شواهد: text.disc_شواهد || [],
            disc_راهنما: text.disc_راهنما || '—',
            ترجیح_کانال: text.ترجیح_کانال || '—',
            سطح_آگاهی_مشتری: text.سطح_آگاهی_مشتری || '—',
            نسبت_زمان_صحبت_مشتری_به_فروشنده: text.نسبت_زمان_صحبت_مشتری_به_فروشنده || '—',
            نسبت_زمان_صحبت_فروشنده_به_مشتری: text.نسبت_زمان_صحبت_فروشنده_به_مشتری || '—',
            خلاصه: text.خلاصه || 'خلاصه‌ای در دسترس نیست',
            تحلیل_شخصیت_مشتری: text.تحلیل_شخصیت_مشتری || 'تحلیلی در دسترس نیست',
            ارزیابی_عملکرد_فردی_فروشنده: text.ارزیابی_عملکرد_فردی_فروشنده || 'ارزیابی‌ای در دسترس نیست',
            تشخیص_آمادگی: text.تشخیص_آمادگی || 'تشخیصی در دسترس نیست',
            اقدام_بعدی: text.اقدام_بعدی || 'اقدامی مشخص نشده'
        },

        // لیست‌ها (9 تا)
        'لیست‌ها': {
            نقاط_قوت: lists.نقاط_قوت || [],
            نقاط_ضعف: lists.نقاط_ضعف || [],
            اعتراضات: lists.اعتراضات || [],
            تکنیکها: lists.تکنیکها || [],
            کلمات_مثبت: lists.کلمات_مثبت || [],
            کلمات_منفی: lists.کلمات_منفی || [],
            ریسک_ها: lists.ریسک_ها || [],
            پارامترهای_رعایت_نشده: lists.پارامترهای_رعایت_نشده || [],
            اشتباهات_رایج: lists.اشتباهات_رایج || []
        },

        // آمار
        آمار: {
            تعداد_کل_تماس_ها: stats.تعداد_کل_تماس_ها || 0,
            تماس_های_موفق: stats.تماس_های_موفق || 0,
            تماس_های_بی_پاسخ: stats.تماس_های_بی_پاسخ || 0,
            تماس_های_ارجاعی: stats.تماس_های_ارجاعی || 0,
            کاربران_فعال: stats.کاربران_فعال || [],
            مشتریان_پرتماس: stats.مشتریان_پرتماس || [],
            انواع_تماس: stats.انواع_تماس || {}
        },

        // بهترین‌ها
        'بهترین_ها': {
            بهترین_فروشنده: best.بهترین_فروشنده || { نام: '—', دلیل: 'تعیین نشده' },
            بهترین_مشتری: best.بهترین_مشتری || { نام: '—', دلیل: 'تعیین نشده' }
        },

        // دلایل (18 تا - 9×2)
        دلایل_کاهش_امتیازها: {
            برقراری_ارتباط: reasons_dec.برقراری_ارتباط || [],
            نیازسنجی: reasons_dec.نیازسنجی || [],
            ارزش_فروشی: reasons_dec.ارزش_فروشی || [],
            مدیریت_اعتراض: reasons_dec.مدیریت_اعتراض || [],
            شفافیت_قیمت: reasons_dec.شفافیت_قیمت || [],
            بستن_فروش: reasons_dec.بستن_فروش || [],
            پیگیری: reasons_dec.پیگیری || [],
            همسویی_احساسی: reasons_dec.همسویی_احساسی || [],
            شنوندگی: reasons_dec.شنوندگی || []
        },

        دلایل_کسب_امتیازها: {
            برقراری_ارتباط: reasons_inc.برقراری_ارتباط || [],
            نیازسنجی: reasons_inc.نیازسنجی || [],
            ارزش_فروشی: reasons_inc.ارزش_فروشی || [],
            مدیریت_اعتراض: reasons_inc.مدیریت_اعتراض || [],
            شفافیت_قیمت: reasons_inc.شفافیت_قیمت || [],
            بستن_فروش: reasons_inc.بستن_فروش || [],
            پیگیری: reasons_inc.پیگیری || [],
            همسویی_احساسی: reasons_inc.همسویی_احساسی || [],
            شنوندگی: reasons_inc.شنوندگی || []
        }
    };
}

// ========================================
// TAB MANAGEMENT
// ========================================

function showTab(tabName) {
    console.log('🔄 showTab فراخوانی شد:', tabName);
    currentTab = tabName;

    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(tabName)) {
            btn.classList.add('active');
        }
    });

    console.log('🎨 شروع render:', tabName);

    // Destroy existing charts
    Object.values(charts).forEach(chart => chart.destroy());
    charts = {};

    // Render tab content
    const content = document.getElementById('tab-content');
    console.log('📦 Element tab-content:', content ? 'پیدا شد' : 'نیست!');

    if (!content) {
        console.error('❌ tab-content element not found!');
        return;
    }

    switch (tabName) {
        case 'overview':
            console.log('📊 renderOverview...');
            content.innerHTML = renderOverview();
            break;
        case 'scores':
            console.log('⭐ renderScores...');
            content.innerHTML = renderScores();
            break;
        case 'analysis':
            console.log('🧠 renderAnalysis...');
            content.innerHTML = renderAnalysis();
            break;
        case 'disc':
            console.log('👥 renderDISC...');
            content.innerHTML = renderDISC();
            break;
        case 'lists':
            console.log('📋 renderLists...');
            content.innerHTML = renderLists();
            break;
        case 'stats':
            console.log('📊 renderStats...');
            content.innerHTML = renderStats();
            break;
        case 'best':
            console.log('🏆 renderBest...');
            content.innerHTML = renderBest();
            break;
    }

    console.log('✅ محتوا رندر شد. طول:', content.innerHTML.length);

    // Initialize charts after rendering
    setTimeout(() => {
        console.log('📈 initializeCharts...');
        initializeCharts();
    }, 100);
}
// ========================================
// RENDER FUNCTIONS - TAB CONTENT
// ========================================

function renderOverview() {
    const scores = analysisData.امتیازها || {};
    const nums = analysisData.فیلدهای_عددی || {};
    const text = analysisData.فیلدهای_متنی || {};
    const stats = analysisData.آمار || {};

    const totalScore = scores.امتیاز_کل || 0;
    const successRate = stats.تماس_های_موفق / (stats.تعداد_کل_تماس_ها || 1) * 100;

    return `
        <!-- Hero Stats -->
        <div class="grid md:grid-cols-4 gap-6 mb-6">
            <div class="glass-card rounded-2xl p-6 text-center score-card">
                <div class="text-6xl font-bold gradient-text mb-2">${totalScore.toFixed(1)}</div>
                <div class="text-gray-600 font-semibold">امتیاز کلی</div>
                <div class="text-sm text-gray-500 mt-1">از 10</div>
                <div class="mt-3">
                    ${getScoreBadge(totalScore)}
                </div>
            </div>
            
            <div class="glass-card rounded-2xl p-6 text-center score-card">
                <div class="text-6xl font-bold text-blue-600 mb-2">${stats.تعداد_کل_تماس_ها || 0}</div>
                <div class="text-gray-600 font-semibold">کل تماس‌ها</div>
                <div class="text-sm text-gray-500 mt-1">مورد</div>
            </div>
            
            <div class="glass-card rounded-2xl p-6 text-center score-card">
                <div class="text-6xl font-bold text-green-600 mb-2">${stats.تماس_های_موفق || 0}</div>
                <div class="text-gray-600 font-semibold">تماس موفق</div>
                <div class="text-sm text-gray-500 mt-1">${successRate.toFixed(0)}% نرخ موفقیت</div>
            </div>
            
            <div class="glass-card rounded-2xl p-6 text-center score-card">
                <div class="text-6xl font-bold text-purple-600 mb-2">${nums.کیفیت_لید_درصد || 0}%</div>
                <div class="text-gray-600 font-semibold">کیفیت لید</div>
                <div class="text-sm text-gray-500 mt-1">درصد</div>
            </div>
        </div>

        <!-- Main Info Cards -->
        <div class="grid md:grid-cols-2 gap-6 mb-6">
            <!-- Seller Info -->
            <div class="glass-card rounded-2xl p-6">
                <h3 class="text-xl font-bold mb-4 flex items-center">
                    <i class="fas fa-user-tie text-blue-600 ml-3 text-2xl"></i>
                    اطلاعات فروشنده
                </h3>
                <div class="space-y-3">
                    <div class="flex justify-between py-2 border-b">
                        <span class="text-gray-600">نام:</span>
                        <span class="font-semibold">${text.نام_فروشنده}</span>
                    </div>
                    <div class="flex justify-between py-2 border-b">
                        <span class="text-gray-600">کد:</span>
                        <span class="font-semibold">${text.کد_فروشنده}</span>
                    </div>
                    <div class="flex justify-between py-2 border-b">
                        <span class="text-gray-600">سطح:</span>
                        <span class="font-semibold">${text.سطح_فروشنده}</span>
                    </div>
                    <div class="flex justify-between py-2">
                        <span class="text-gray-600">DISC:</span>
                        <span class="font-bold text-purple-600 text-lg">${text.disc_تیپ}</span>
                    </div>
                </div>
            </div>

            <!-- Customer Info -->
            <div class="glass-card rounded-2xl p-6">
                <h3 class="text-xl font-bold mb-4 flex items-center">
                    <i class="fas fa-building text-green-600 ml-3 text-2xl"></i>
                    اطلاعات مشتری
                </h3>
                <div class="space-y-3">
                    <div class="flex justify-between py-2 border-b">
                        <span class="text-gray-600">نام:</span>
                        <span class="font-semibold">${text.نام_مشتری}</span>
                    </div>
                    <div class="flex justify-between py-2 border-b">
                        <span class="text-gray-600">محصول:</span>
                        <span class="font-semibold">${text.محصول}</span>
                    </div>
                    <div class="flex justify-between py-2 border-b">
                        <span class="text-gray-600">آگاهی:</span>
                        <span class="font-semibold">${text.سطح_آگاهی_مشتری}</span>
                    </div>
                    <div class="flex justify-between py-2">
                        <span class="text-gray-600">کانال:</span>
                        <span class="font-semibold">${text.ترجیح_کانال}</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Call Details -->
        <div class="glass-card rounded-2xl p-6 mb-6">
            <h3 class="text-xl font-bold mb-4 flex items-center">
                <i class="fas fa-phone-volume text-indigo-600 ml-3 text-2xl"></i>
                جزئیات تماس
            </h3>
            <div class="grid md:grid-cols-4 gap-4">
                <div class="bg-white bg-opacity-50 rounded-xl p-4">
                    <div class="text-sm text-gray-600 mb-1">مدت تماس</div>
                    <div class="text-lg font-bold">${text.مدت_تماس}</div>
                </div>
                <div class="bg-white bg-opacity-50 rounded-xl p-4">
                    <div class="text-sm text-gray-600 mb-1">جهت</div>
                    <div class="text-lg font-bold">${text.نوع_تماس_جهت}</div>
                </div>
                <div class="bg-white bg-opacity-50 rounded-xl p-4">
                    <div class="text-sm text-gray-600 mb-1">مرحله</div>
                    <div class="text-lg font-bold">${text.نوع_تماس_مرحله}</div>
                </div>
                <div class="bg-white bg-opacity-50 rounded-xl p-4">
                    <div class="text-sm text-gray-600 mb-1">گرمی</div>
                    <div class="text-lg font-bold">${text.نوع_تماس_گرمی}</div>
                </div>
            </div>
        </div>

        <!-- Key Scores Chart -->
        <div class="glass-card rounded-2xl p-6 mb-6">
            <h3 class="text-xl font-bold mb-4">امتیازهای کلیدی</h3>
            <div class="grid md:grid-cols-2 gap-6">
                <canvas id="overview-radar-chart"></canvas>
                <div class="grid grid-cols-2 gap-3">
                    ${Object.entries(scores).filter(([k]) => k !== 'امتیاز_کل').map(([key, value]) => `
                        <div class="bg-white bg-opacity-50 rounded-lg p-3">
                            <div class="text-xs text-gray-600 mb-1">${key.replace('_', ' ')}</div>
                            <div class="text-2xl font-bold">${value}/10</div>
                            <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
                                <div class="h-2 rounded-full ${getScoreColor(value)}" style="width: ${value * 10}%"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>

        <!-- Summary -->
        <div class="glass-card rounded-2xl p-6">
            <h3 class="text-xl font-bold mb-4 flex items-center">
                <i class="fas fa-file-lines text-yellow-600 ml-3 text-2xl"></i>
                خلاصه تحلیل
            </h3>
            <p class="text-gray-700 leading-relaxed">${text.خلاصه}</p>
        </div>
    `;
}

function renderScores() {
    const scores = analysisData.امتیازها || {};
    const nums = analysisData.فیلدهای_عددی || {};
    const reasons_inc = analysisData.دلایل_کسب_امتیازها || {};
    const reasons_dec = analysisData.دلایل_کاهش_امتیازها || {};
    
    return `
        <!-- Scores Grid -->
        <div class="grid md:grid-cols-5 gap-4 mb-6">
            ${Object.entries(scores).map(([key, value]) => `
                <div class="glass-card rounded-xl p-4 text-center score-card">
                    <div class="text-3xl font-bold mb-2 ${getScoreColorText(value)}">${value}</div>
                    <div class="text-sm text-gray-600">${key.replace(/_/g, ' ')}</div>
                    <div class="mt-2">${getScoreBadge(value)}</div>
                </div>
            `).join('')}
        </div>

        <!-- Charts Section -->
        <div class="grid md:grid-cols-2 gap-6 mb-6">
            <!-- Radar Chart -->
            <div class="glass-card rounded-2xl p-6">
                <h3 class="text-lg font-bold mb-4">نمودار راداری امتیازها</h3>
                <canvas id="scores-radar-chart"></canvas>
            </div>

            <!-- Bar Chart -->
            <div class="glass-card rounded-2xl p-6">
                <h3 class="text-lg font-bold mb-4">مقایسه امتیازها</h3>
                <canvas id="scores-bar-chart"></canvas>
            </div>
        </div>

        <!-- Additional Metrics -->
        <div class="glass-card rounded-2xl p-6 mb-6">
            <h3 class="text-xl font-bold mb-4 flex items-center">
                <i class="fas fa-chart-line text-green-600 ml-3"></i>
                شاخص‌های تکمیلی
            </h3>
            <div class="grid md:grid-cols-4 gap-4">
                ${renderMetricCard('تعداد سوالات باز', nums.تعداد_سوالات_باز, 'fas fa-question-circle', 'blue')}
                ${renderMetricCard('تعداد اعتراض', nums.تعداد_اعتراض, 'fas fa-exclamation-triangle', 'orange')}
                ${renderMetricCard('پاسخ به اعتراض', nums.درصد_پاسخ_موفق_به_اعتراض + '%', 'fas fa-check-circle', 'green')}
                ${renderMetricCard('تلاش بستن', nums.تعداد_تلاش_برای_بستن, 'fas fa-handshake', 'purple')}
                ${renderMetricCard('احساس مشتری', nums.امتیاز_احساس_مشتری + '/10', 'fas fa-smile', 'pink')}
                ${renderMetricCard('آمادگی بستن', nums.آمادگی_بستن_درصد + '%', 'fas fa-rocket', 'indigo')}
                ${renderMetricCard('چگالی فنی فروشنده', nums.چگالی_اطلاعات_فنی_فروشنده_درصد + '%', 'fas fa-brain', 'teal')}
                ${renderMetricCard('چگالی فنی مشتری', nums.چگالی_اطلاعات_فنی_مشتری_درصد + '%', 'fas fa-lightbulb', 'cyan')}
            </div>
        </div>

        <!-- Reasons -->
        <div class="grid md:grid-cols-2 gap-6">
            <div class="glass-card rounded-2xl p-6">
                <h3 class="text-xl font-bold mb-4 flex items-center text-green-600">
                    <i class="fas fa-thumbs-up ml-3"></i>
                    دلایل کسب امتیاز
                </h3>
                <div class="space-y-4">
                    ${Object.entries(reasons_inc).map(([key, reasons]) => `
                        <div class="bg-green-50 rounded-lg p-4">
                            <div class="font-semibold text-green-800 mb-2">${key.replace(/_/g, ' ')}</div>
                            <ul class="text-sm space-y-1">
                                ${(reasons || []).map(r => `<li class="flex items-start"><i class="fas fa-check text-green-600 ml-2 mt-1"></i><span>${r}</span></li>`).join('')}
                            </ul>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="glass-card rounded-2xl p-6">
                <h3 class="text-xl font-bold mb-4 flex items-center text-red-600">
                    <i class="fas fa-thumbs-down ml-3"></i>
                    دلایل کاهش امتیاز
                </h3>
                <div class="space-y-4">
                    ${Object.entries(reasons_dec).map(([key, reasons]) => `
                        <div class="bg-red-50 rounded-lg p-4">
                            <div class="font-semibold text-red-800 mb-2">${key.replace(/_/g, ' ')}</div>
                            <ul class="text-sm space-y-1">
                                ${(reasons || []).map(r => `<li class="flex items-start"><i class="fas fa-times text-red-600 ml-2 mt-1"></i><span>${r}</span></li>`).join('')}
                            </ul>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

function renderAnalysis() {
    const text = analysisData.فیلدهای_متنی || {};

    const nums = analysisData.فیلدهای_عددی || {};
    
    return `
        <!-- Customer Personality -->
        <div class="glass-card rounded-2xl p-6 mb-6">
            <h3 class="text-xl font-bold mb-4 flex items-center">
                <i class="fas fa-user-circle text-blue-600 ml-3 text-2xl"></i>
                تحلیل شخصیت مشتری
            </h3>
            <p class="text-gray-700 leading-relaxed whitespace-pre-line">${text.تحلیل_شخصیت_مشتری}</p>
        </div>

        <!-- Seller Performance -->
        <div class="glass-card rounded-2xl p-6 mb-6">
            <h3 class="text-xl font-bold mb-4 flex items-center">
                <i class="fas fa-user-check text-green-600 ml-3 text-2xl"></i>
                ارزیابی عملکرد فروشنده
            </h3>
            <p class="text-gray-700 leading-relaxed whitespace-pre-line">${text.ارزیابی_عملکرد_فردی_فروشنده}</p>
        </div>

        <!-- Time Ratios -->
        <div class="glass-card rounded-2xl p-6 mb-6">
            <h3 class="text-xl font-bold mb-4 flex items-center">
                <i class="fas fa-clock text-purple-600 ml-3 text-2xl"></i>
                نسبت زمان صحبت
            </h3>
            <div class="grid md:grid-cols-2 gap-6">
                <div class="bg-white bg-opacity-50 rounded-xl p-6 text-center">
                    <div class="text-sm text-gray-600 mb-2">مشتری : فروشنده</div>
                    <div class="text-4xl font-bold text-blue-600">${text.نسبت_زمان_صحبت_مشتری_به_فروشنده}</div>
                </div>
                <div class="bg-white bg-opacity-50 rounded-xl p-6 text-center">
                    <div class="text-sm text-gray-600 mb-2">فروشنده : مشتری</div>
                    <div class="text-4xl font-bold text-green-600">${text.نسبت_زمان_صحبت_فروشنده_به_مشتری}</div>
                </div>
            </div>
        </div>

        <!-- Sensitivity Analysis -->
        <div class="glass-card rounded-2xl p-6 mb-6">
            <h3 class="text-xl font-bold mb-4 flex items-center">
                <i class="fas fa-heart-pulse text-red-600 ml-3 text-2xl"></i>
                تحلیل حساسیت مشتری
            </h3>
            <div class="grid md:grid-cols-3 gap-4">
                <div class="bg-red-50 rounded-xl p-6">
                    <div class="flex items-center justify-between mb-3">
                        <span class="text-sm font-semibold">حساسیت قیمت</span>
                        <i class="fas fa-dollar-sign text-2xl text-red-600"></i>
                    </div>
                    <div class="text-3xl font-bold text-red-600 mb-2">${nums.حساسیت_قیمت_مشتری_درصد}%</div>
                    <div class="w-full bg-red-200 rounded-full h-3">
                        <div class="bg-red-600 h-3 rounded-full" style="width: ${nums.حساسیت_قیمت_مشتری_درصد}%"></div>
                    </div>
                </div>
                
                <div class="bg-orange-50 rounded-xl p-6">
                    <div class="flex items-center justify-between mb-3">
                        <span class="text-sm font-semibold">حساسیت ریسک</span>
                        <i class="fas fa-shield-alt text-2xl text-orange-600"></i>
                    </div>
                    <div class="text-3xl font-bold text-orange-600 mb-2">${nums.حساسیت_ریسک_مشتری_درصد}%</div>
                    <div class="w-full bg-orange-200 rounded-full h-3">
                        <div class="bg-orange-600 h-3 rounded-full" style="width: ${nums.حساسیت_ریسک_مشتری_درصد}%"></div>
                    </div>
                </div>
                
                <div class="bg-yellow-50 rounded-xl p-6">
                    <div class="flex items-center justify-between mb-3">
                        <span class="text-sm font-semibold">حساسیت زمان</span>
                        <i class="fas fa-hourglass-half text-2xl text-yellow-600"></i>
                    </div>
                    <div class="text-3xl font-bold text-yellow-600 mb-2">${nums.حساسیت_زمان_مشتری_درصد}%</div>
                    <div class="w-full bg-yellow-200 rounded-full h-3">
                        <div class="bg-yellow-600 h-3 rounded-full" style="width: ${nums.حساسیت_زمان_مشتری_درصد}%"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Readiness & Next Action -->
        <div class="grid md:grid-cols-2 gap-6">
            <div class="glass-card rounded-2xl p-6">
                <h3 class="text-xl font-bold mb-4 flex items-center">
                    <i class="fas fa-flag-checkered text-indigo-600 ml-3"></i>
                    تشخیص آمادگی
                </h3>
                <p class="text-gray-700 leading-relaxed">${text.تشخیص_آمادگی}</p>
            </div>

            <div class="glass-card rounded-2xl p-6 bg-gradient-to-br from-yellow-50 to-orange-50 border-r-4 border-yellow-500">
                <h3 class="text-xl font-bold mb-4 flex items-center">
                    <i class="fas fa-forward text-yellow-600 ml-3"></i>
                    اقدام بعدی
                </h3>
                <p class="text-gray-700 leading-relaxed font-semibold">${text.اقدام_بعدی}</p>
            </div>
        </div>
    `;
}
// ========================================
// RENDER DISC TAB
// ========================================
function renderDISC() {
    const disc = analysisData.DISC || {};
    const text = analysisData.فیلدهای_متنی || {};

    
    return `
        <div class="grid md:grid-cols-2 gap-6 mb-6">
            <!-- DISC Scores -->
            <div class="glass-card rounded-2xl p-6">
                <h3 class="text-xl font-bold mb-4">امتیازات DISC</h3>
                <div class="space-y-4">
                    ${renderDISCBar('D - قاطعیت (Dominance)', disc.disc_d, 'red')}
                    ${renderDISCBar('I - تعامل (Influence)', disc.disc_i, 'yellow')}
                    ${renderDISCBar('S - ثبات (Steadiness)', disc.disc_s, 'green')}
                    ${renderDISCBar('C - دقت (Conscientiousness)', disc.disc_c, 'blue')}
                </div>
            </div>

            <!-- DISC Chart -->
            <div class="glass-card rounded-2xl p-6">
                <h3 class="text-xl font-bold mb-4">نمودار DISC</h3>
                <canvas id="disc-doughnut-chart"></canvas>
            </div>
        </div>

        <!-- DISC Type -->
        <div class="glass-card rounded-2xl p-8 mb-6 bg-gradient-to-br from-purple-50 to-indigo-50">
            <div class="text-center">
                <h3 class="text-2xl font-bold mb-4">تیپ شخصیتی غالب</h3>
                <div class="inline-block bg-white rounded-full px-12 py-6 shadow-lg">
                    <div class="text-6xl font-bold gradient-text">${text.disc_تیپ}</div>
                </div>
            </div>
        </div>

        <!-- Evidence & Guide -->
        <div class="grid md:grid-cols-2 gap-6">
            <div class="glass-card rounded-2xl p-6">
                <h3 class="text-xl font-bold mb-4 flex items-center">
                    <i class="fas fa-clipboard-list text-blue-600 ml-3"></i>
                    شواهد DISC
                </h3>
                <ul class="space-y-2">
                    ${(text.disc_شواهد || []).map(evidence => `
                        <li class="flex items-start list-item rounded-lg p-3">
                            <i class="fas fa-check-circle text-green-500 ml-2 mt-1"></i>
                            <span class="text-gray-700">${evidence}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>

            <div class="glass-card rounded-2xl p-6 bg-gradient-to-br from-green-50 to-teal-50">
                <h3 class="text-xl font-bold mb-4 flex items-center">
                    <i class="fas fa-lightbulb text-yellow-600 ml-3"></i>
                    راهنمای تعامل
                </h3>
                <p class="text-gray-700 leading-relaxed">${text.disc_راهنما}</p>
            </div>
        </div>
    `;
}

// ========================================
// RENDER LISTS TAB
// ========================================
function renderLists() {
    const lists = analysisData['لیست‌ها'] || {};
    
    return `
        <div class="grid md:grid-cols-2 gap-6 mb-6">
            <!-- Strengths -->
            ${renderListCard('نقاط قوت', lists.نقاط_قوت, 'fas fa-thumbs-up', 'green')}
            
            <!-- Weaknesses -->
            ${renderListCard('نقاط ضعف', lists.نقاط_ضعف, 'fas fa-thumbs-down', 'red')}
        </div>

        <div class="grid md:grid-cols-2 gap-6 mb-6">
            <!-- Objections -->
            ${renderListCard('اعتراضات', lists.اعتراضات, 'fas fa-exclamation-circle', 'orange')}
            
            <!-- Techniques -->
            ${renderListCard('تکنیک‌ها', lists.تکنیکها, 'fas fa-magic', 'purple')}
        </div>

        <div class="grid md:grid-cols-2 gap-6 mb-6">
            <!-- Risks -->
            ${renderListCard('ریسک‌ها', lists.ریسک_ها, 'fas fa-exclamation-triangle', 'red')}
            
            <!-- Missed Parameters -->
            ${renderListCard('پارامترهای رعایت نشده', lists.پارامترهای_رعایت_نشده, 'fas fa-times-circle', 'yellow')}
        </div>

        <div class="grid md:grid-cols-2 gap-6 mb-6">
            <!-- Common Mistakes -->
            ${renderListCard('اشتباهات رایج', lists.اشتباهات_رایج, 'fas fa-bug', 'pink')}
            
            <!-- Keywords -->
            <div class="glass-card rounded-2xl p-6">
                <h3 class="text-xl font-bold mb-4 flex items-center">
                    <i class="fas fa-key text-blue-600 ml-3"></i>
                    کلمات کلیدی
                </h3>
                <div class="space-y-4">
                    <div>
                        <div class="text-sm font-semibold text-green-700 mb-2">مثبت:</div>
                        <div class="flex flex-wrap gap-2">
                            ${(lists.کلمات_مثبت || []).map(word => `
                                <span class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                                    ${word}
                                </span>
                            `).join('')}
                        </div>
                    </div>
                    <div>
                        <div class="text-sm font-semibold text-red-700 mb-2">منفی:</div>
                        <div class="flex flex-wrap gap-2">
                            ${(lists.کلمات_منفی || []).map(word => `
                                <span class="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium">
                                    ${word}
                                </span>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// ========================================
// RENDER STATS TAB
// ========================================
function renderStats() {
    const stats = analysisData.آمار || {};
    
    return `
        <!-- Call Stats -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div class="glass-card rounded-xl p-6 text-center">
                <i class="fas fa-phone text-4xl text-blue-600 mb-3"></i>
                <div class="text-3xl font-bold text-blue-600">${stats.تعداد_کل_تماس_ها || 0}</div>
                <div class="text-sm text-gray-600 mt-1">کل تماس‌ها</div>
            </div>
            
            <div class="glass-card rounded-xl p-6 text-center">
                <i class="fas fa-check-circle text-4xl text-green-600 mb-3"></i>
                <div class="text-3xl font-bold text-green-600">${stats.تماس_های_موفق || 0}</div>
                <div class="text-sm text-gray-600 mt-1">موفق</div>
            </div>
            
            <div class="glass-card rounded-xl p-6 text-center">
                <i class="fas fa-phone-slash text-4xl text-red-600 mb-3"></i>
                <div class="text-3xl font-bold text-red-600">${stats.تماس_های_بی_پاسخ || 0}</div>
                <div class="text-sm text-gray-600 mt-1">بی‌پاسخ</div>
            </div>
            
            <div class="glass-card rounded-xl p-6 text-center">
                <i class="fas fa-share text-4xl text-orange-600 mb-3"></i>
                <div class="text-3xl font-bold text-orange-600">${stats.تماس_های_ارجاعی || 0}</div>
                <div class="text-sm text-gray-600 mt-1">ارجاعی</div>
            </div>
        </div>

        <div class="grid md:grid-cols-2 gap-6 mb-6">
            <!-- Active Users -->
            <div class="glass-card rounded-2xl p-6">
                <h3 class="text-xl font-bold mb-4 flex items-center">
                    <i class="fas fa-users text-blue-600 ml-3"></i>
                    کاربران فعال
                </h3>
                <div class="space-y-3">
                    ${(stats.کاربران_فعال || []).map(user => {
                        const userName = typeof user === 'object' ? user.نام : user;
                        const callCount = typeof user === 'object' ? user.تعداد_تماس : 0;
                        const note = typeof user === 'object' ? user.یادداشت_عملکرد : '';
                        return `
                            <div class="bg-blue-50 rounded-lg p-4">
                                <div class="flex items-center justify-between mb-2">
                                    <span class="font-semibold text-blue-900">${userName}</span>
                                    <span class="bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-bold">${callCount}</span>
                                </div>
                                ${note ? `<p class="text-sm text-gray-600">${note}</p>` : ''}
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>

            <!-- Top Customers -->
            <div class="glass-card rounded-2xl p-6">
                <h3 class="text-xl font-bold mb-4 flex items-center">
                    <i class="fas fa-building text-green-600 ml-3"></i>
                    مشتریان پرتماس
                </h3>
                <div class="space-y-3">
                    ${(stats.مشتریان_پرتماس || []).map(customer => {
                        const custName = typeof customer === 'object' ? customer.نام : customer;
                        const contactCount = typeof customer === 'object' ? customer.تعداد_تماس : 0;
                        const quality = typeof customer === 'object' ? customer.کیفیت_تعامل : '';
                        return `
                            <div class="bg-green-50 rounded-lg p-4">
                                <div class="flex items-center justify-between mb-2">
                                    <span class="font-semibold text-green-900">${custName}</span>
                                    <span class="bg-green-600 text-white px-3 py-1 rounded-full text-sm font-bold">${contactCount}</span>
                                </div>
                                ${quality ? `<p class="text-sm text-gray-600">کیفیت: ${quality}</p>` : ''}
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        </div>

        <!-- Call Types Chart -->
        <div class="glass-card rounded-2xl p-6">
            <h3 class="text-xl font-bold mb-4">انواع تماس</h3>
            <canvas id="call-types-chart"></canvas>
        </div>
    `;
}

// ========================================
// RENDER BEST TAB
// ========================================
function renderBest() {
    const best = analysisData['بهترین_ها'] || {};
    const seller = best.بهترین_فروشنده || {};
    const customer = best.بهترین_مشتری || {};
    
    return `
        <div class="grid md:grid-cols-2 gap-8">
            <!-- Best Seller -->
            <div class="glass-card rounded-2xl p-8 bg-gradient-to-br from-yellow-50 via-orange-50 to-red-50 border-2 border-yellow-300">
                <div class="text-center mb-6">
                    <i class="fas fa-trophy text-7xl text-yellow-500 mb-4"></i>
                    <h3 class="text-2xl font-bold text-gray-800 mb-2">بهترین فروشنده</h3>
                </div>
                
                <div class="bg-white rounded-xl p-6 shadow-lg">
                    <div class="flex items-center justify-center mb-4">
                        <div class="bg-yellow-100 rounded-full p-4">
                            <i class="fas fa-user-tie text-4xl text-yellow-600"></i>
                        </div>
                    </div>
                    <div class="text-center mb-4">
                        <div class="text-3xl font-bold gradient-text">${seller.نام || '—'}</div>
                    </div>
                    <div class="section-divider"></div>
                    <div class="mt-4">
                        <h4 class="font-semibold text-gray-700 mb-2">دلیل انتخاب:</h4>
                        <p class="text-gray-600 leading-relaxed">${seller.دلیل || 'دلیلی ثبت نشده'}</p>
                    </div>
                </div>
            </div>

            <!-- Best Customer -->
            <div class="glass-card rounded-2xl p-8 bg-gradient-to-br from-green-50 via-teal-50 to-cyan-50 border-2 border-green-300">
                <div class="text-center mb-6">
                    <i class="fas fa-star text-7xl text-green-500 mb-4"></i>
                    <h3 class="text-2xl font-bold text-gray-800 mb-2">بهترین مشتری</h3>
                </div>
                
                <div class="bg-white rounded-xl p-6 shadow-lg">
                    <div class="flex items-center justify-center mb-4">
                        <div class="bg-green-100 rounded-full p-4">
                            <i class="fas fa-building text-4xl text-green-600"></i>
                        </div>
                    </div>
                    <div class="text-center mb-4">
                        <div class="text-3xl font-bold text-green-600">${customer.نام || '—'}</div>
                    </div>
                    <div class="section-divider"></div>
                    <div class="mt-4">
                        <h4 class="font-semibold text-gray-700 mb-2">دلیل انتخاب:</h4>
                        <p class="text-gray-600 leading-relaxed">${customer.دلیل || 'دلیلی ثبت نشده'}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// ========================================
// HELPER FUNCTIONS
// ========================================
function getScoreBadge(score) {
    if (score >= 8) return '<span class="metric-badge badge-high">عالی</span>';
    if (score >= 6) return '<span class="metric-badge badge-medium">متوسط</span>';
    return '<span class="metric-badge badge-low">ضعیف</span>';
}

function getScoreColor(score) {
    if (score >= 8) return 'bg-green-500';
    if (score >= 6) return 'bg-yellow-500';
    return 'bg-red-500';
}

function getScoreColorText(score) {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    return 'text-red-600';
}

function renderMetricCard(label, value, icon, color) {
    return `
        <div class="bg-white bg-opacity-50 rounded-xl p-4">
            <div class="flex items-center justify-between mb-2">
                <i class="${icon} text-2xl text-${color}-600"></i>
                <span class="text-2xl font-bold text-${color}-600">${value}</span>
            </div>
            <div class="text-sm text-gray-600">${label}</div>
        </div>
    `;
}

function renderDISCBar(label, value, color) {
    return `
        <div class="bg-white bg-opacity-50 rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
                <span class="font-semibold">${label}</span>
                <span class="text-xl font-bold text-${color}-600">${value}/10</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-3">
                <div class="bg-${color}-500 h-3 rounded-full transition-all duration-500" style="width: ${value * 10}%"></div>
            </div>
        </div>
    `;
}

function renderListCard(title, items, icon, color) {
    return `
        <div class="glass-card rounded-2xl p-6">
            <h3 class="text-xl font-bold mb-4 flex items-center">
                <i class="${icon} text-${color}-600 ml-3"></i>
                ${title}
            </h3>
            <ul class="space-y-2">
                ${(items || []).map(item => `
                    <li class="flex items-start list-item rounded-lg p-3 bg-${color}-50">
                        <i class="fas fa-circle text-${color}-600 ml-2 mt-1 text-xs"></i>
                        <span class="text-gray-700">${item}</span>
                    </li>
                `).join('') || '<li class="text-gray-500 text-center py-4">موردی ثبت نشده</li>'}
            </ul>
        </div>
    `;
}

// ========================================
// CHART INITIALIZATION
// ========================================
function initializeCharts() {
    if (currentTab === 'overview') {
        createOverviewRadar();
    } else if (currentTab === 'scores') {
        createScoresRadar();
        createScoresBar();
    } else if (currentTab === 'disc') {
        createDISCDoughnut();
    } else if (currentTab === 'stats') {
        createCallTypesChart();
    }
}

function createOverviewRadar() {
    const canvas = document.getElementById('overview-radar-chart');
    if (!canvas) return;
    
    const scores = analysisData.امتیازها || {};
    const labels = Object.keys(scores).filter(k => k !== 'امتیاز_کل').map(k => k.replace(/_/g, ' '));
    const data = Object.values(scores).filter((v, i) => Object.keys(scores)[i] !== 'امتیاز_کل');
    
    charts.overviewRadar = new Chart(canvas, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'امتیازات',
                data: data,
                backgroundColor: 'rgba(102, 126, 234, 0.2)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(102, 126, 234, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 10,
                    ticks: { stepSize: 2 }
                }
            }
        }
    });
}

function createScoresRadar() {
    const canvas = document.getElementById('scores-radar-chart');
    if (!canvas) return;
    
    const scores = analysisData.امتیازها || {};
    const labels = Object.keys(scores).filter(k => k !== 'امتیاز_کل').map(k => k.replace(/_/g, ' '));
    const data = Object.values(scores).filter((v, i) => Object.keys(scores)[i] !== 'امتیاز_کل');
    
    charts.scoresRadar = new Chart(canvas, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'امتیازات',
                data: data,
                backgroundColor: 'rgba(16, 185, 129, 0.2)',
                borderColor: 'rgba(16, 185, 129, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 10
                }
            }
        }
    });
}

function createScoresBar() {
    const canvas = document.getElementById('scores-bar-chart');
    if (!canvas) return;
    
    const scores = analysisData.امتیازها || {};
    const labels = Object.keys(scores).map(k => k.replace(/_/g, ' '));
    const data = Object.values(scores);
    
    charts.scoresBar = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'امتیاز',
                data: data,
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10
                }
            }
        }
    });
}

function createDISCDoughnut() {
    const canvas = document.getElementById('disc-doughnut-chart');
    if (!canvas) return;
    
    const disc = analysisData.DISC || {};
    
    charts.discDoughnut = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: ['D - قاطعیت', 'I - تعامل', 'S - ثبات', 'C - دقت'],
            datasets: [{
                data: [disc.disc_d, disc.disc_i, disc.disc_s, disc.disc_c],
                backgroundColor: [
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(59, 130, 246, 0.8)'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true
        }
    });
}

function createCallTypesChart() {
    const canvas = document.getElementById('call-types-chart');
    if (!canvas) return;
    
    const stats = analysisData.آمار || {};
    const callTypes = stats.انواع_تماس || {};
    
    charts.callTypes = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: Object.keys(callTypes),
            datasets: [{
                label: 'تعداد',
                data: Object.values(callTypes),
                backgroundColor: 'rgba(147, 51, 234, 0.8)',
                borderColor: 'rgba(147, 51, 234, 1)',
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
            }
        }
    });
}