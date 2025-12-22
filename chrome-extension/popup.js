let processedData = null;
let automationResults = [];
let selectedPlatform = 'webbeds';

document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const processBtn = document.getElementById('processBtn');
    const startBtn = document.getElementById('startBtn');
    const status = document.getElementById('status');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const platformBtns = document.querySelectorAll('.platform-btn');
    const platformInfo = document.getElementById('platformInfo');

    // اختيار المنصة
    platformBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            platformBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            selectedPlatform = this.dataset.platform;
            updatePlatformInfo();
            resetForm();
        });
    });

    function updatePlatformInfo() {
        const platformInfos = {
            'webbeds': '<strong>WebBeds:</strong> تأكد من أنك في صفحة الحجوزات',
            'almatar': '<strong>Almatar:</strong> تأكد من أنك في صفحة قائمة الحجوزات',
            'eet': '<strong>EET Global:</strong> تأكد من أنك في صفحة قائمة الحجوزات',
            'traveasy': '<strong>Traveasy:</strong> تأكد من أنك في صفحة قائمة الحجوزات',
            'tds': '<strong>TDS:</strong> تأكد من أنك في صفحة قائمة الحجوزات',
            'gte': '<strong>GTE:</strong> تأكد من أنك في صفحة قائمة الحجوزات',
            'alataya': '<strong>العطايا:</strong> تأكد من أنك في صفحة قائمة الحجوزات'
        };
        platformInfo.innerHTML = platformInfos[selectedPlatform] || platformInfos['webbeds'];
    }

    function resetForm() {
        processedData = null;
        fileInfo.style.display = 'none';
        processBtn.disabled = true;
        startBtn.disabled = true;
        document.getElementById('results').style.display = 'none';
        document.getElementById('progressContainer').style.display = 'none';
        status.innerHTML = '';
    }

    // رفع الملف
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#d32f2f';
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = '#ccc';
    });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#ccc';
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    processBtn.addEventListener('click', processFile);
    startBtn.addEventListener('click', startAutomation);

    function handleFile(file) {
        if (!file.name.match(/\.csv$/)) {
            showStatus('يرجى اختيار ملف CSV صحيح', 'error');
            return;
        }

        fileName.textContent = file.name;
        fileInfo.style.display = 'block';
        processBtn.disabled = false;
        
        // حفظ الملف
        const reader = new FileReader();
        reader.onload = function(e) {
            chrome.storage.local.set({
                'uploadedFile': {
                    name: file.name,
                    data: e.target.result,
                    platform: selectedPlatform
                }
            });
        };
        reader.readAsText(file);
    }

    function processFile() {
        showStatus('جاري تحليل الملف...', 'info');
        processBtn.disabled = true;

        chrome.storage.local.get(['uploadedFile'], function(result) {
            if (result.uploadedFile) {
                setTimeout(() => {
                    parseCSVFile(result.uploadedFile.data);
                }, 1000);
            }
        });
    }
    
    function parseCSVFile(csvText) {
        try {
            console.log('CSV المقروء:', csvText);
            
            const lines = csvText.split('\n');
            const bookingsData = [];
            
            if (lines.length > 1) {
                const headers = lines[0].split(',').map(h => h.trim());
                console.log('Headers:', headers);
                
                let bookingIndex, hotelConfIndex;
                
                if (selectedPlatform === 'webbeds') {
                    bookingIndex = headers.findIndex(h => h.includes('ClientReference'));
                    hotelConfIndex = headers.findIndex(h => h.includes('HotelConf'));
                } else {
                    bookingIndex = headers.findIndex(h => h.includes('Booking Code'));
                    hotelConfIndex = headers.findIndex(h => h.includes('HotelConf'));
                }
                
                console.log('مؤشرات الأعمدة:', { bookingIndex, hotelConfIndex });
                
                if (bookingIndex === -1 || hotelConfIndex === -1) {
                    throw new Error('لم يتم العثور على الأعمدة المطلوبة في الملف');
                }
                
                for (let i = 1; i < lines.length; i++) {
                    const values = lines[i].split(',').map(v => v.trim());
                    if (values.length > Math.max(bookingIndex, hotelConfIndex)) {
                        const bookingCode = values[bookingIndex];
                        const hotelConf = values[hotelConfIndex];
                        
                        if (bookingCode && hotelConf && bookingCode !== '' && hotelConf !== '') {
                            bookingsData.push({
                                bookingNumber: bookingCode,
                                hotelConf: hotelConf,
                                platform: selectedPlatform
                            });
                        }
                    }
                }
            }
            
            console.log('بيانات CSV النهائية:', bookingsData);
            
            processedData = bookingsData;
            
            if (processedData && processedData.length > 0) {
                showStatus(`تم العثور على ${processedData.length} حجز جاهز للمعالجة`, 'success');
                startBtn.disabled = false;
            } else {
                showStatus('لم يتم العثور على بيانات صحيحة في الملف', 'error');
            }
            
            processBtn.disabled = false;
            
        } catch (error) {
            console.error('خطأ في تحليل CSV:', error);
            showStatus('خطأ في تحليل ملف CSV: ' + error.message, 'error');
            processBtn.disabled = false;
        }
    }

    function startAutomation() {
        if (!processedData || processedData.length === 0) {
            showStatus('لا توجد بيانات للمعالجة', 'error');
            return;
        }

        startBtn.disabled = true;
        document.getElementById('progressContainer').style.display = 'block';
        
        // إرسال البيانات إلى content script
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            if (tabs[0] && tabs[0].url) {
                const validDomains = {
                    'webbeds': 'extranet.webbeds.com',
                    'almatar': 'portal.arabiabeds.com',
                    'eet': 'www.eetglobal.com',
                    'traveasy': 'hotels.holidayme.com',
                    'tds': 'go.tdstravel.com',
                    'gte': 'www.gte.travel',
                    'alataya': 'www.attaya.travel'
                };
                
                const isValidUrl = tabs[0].url.includes(validDomains[selectedPlatform]);
                    
                if (isValidUrl) {
                    chrome.tabs.sendMessage(tabs[0].id, {
                        action: 'startAutomation',
                        data: processedData,
                        platform: selectedPlatform
                    }, function(response) {
                        if (chrome.runtime.lastError) {
                            showStatus('خطأ في الاتصال: ' + chrome.runtime.lastError.message, 'error');
                            startBtn.disabled = false;
                            return;
                        }
                        if (response && response.success) {
                            showStatus('بدأت عملية الأتمتة...', 'info');
                        } else {
                            showStatus('خطأ في بدء الأتمتة', 'error');
                            startBtn.disabled = false;
                        }
                    });
                } else {
                    const platformNames = {
                        'webbeds': 'WebBeds',
                        'almatar': 'Almatar',
                        'eet': 'EET Global',
                        'traveasy': 'Traveasy',
                        'tds': 'TDS',
                        'gte': 'GTE',
                        'alataya': 'العطايا'
                    };
                    showStatus(`يرجى الانتقال إلى صفحة ${platformNames[selectedPlatform]} أولاً`, 'error');
                    startBtn.disabled = false;
                }
            }
        });
    }

    function showStatus(message, type) {
        status.innerHTML = `<div class="status ${type}">${message}</div>`;
    }

    // استقبال النتائج من content script
    chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
        if (request.action === 'updateProgress') {
            const progress = (request.current / request.total) * 100;
            document.getElementById('progressBar').style.width = progress + '%';
            showStatus(`معالجة الحجز ${request.current} من ${request.total}`, 'info');
        } else if (request.action === 'automationComplete') {
            automationResults = request.results;
            showResults();
        }
    });

    function showResults() {
        const successCount = automationResults.filter(r => r.success).length;
        const failCount = automationResults.filter(r => !r.success).length;
        
        document.getElementById('successCount').textContent = successCount;
        document.getElementById('failCount').textContent = failCount;
        document.getElementById('results').style.display = 'block';
        document.getElementById('progressContainer').style.display = 'none';
        
        showStatus('تمت عملية الأتمتة بنجاح!', 'success');
        startBtn.disabled = false;
    }

    document.getElementById('downloadBtn').addEventListener('click', function() {
        const csvContent = generateCSVReport();
        const platformName = selectedPlatform === 'webbeds' ? 'webbeds' : 'almatar';
        downloadFile(csvContent, `${platformName}_automation_report.csv`);
    });

    function generateCSVReport() {
        let csv = 'Booking Number,Hotel Conf,Status,Message,Timestamp\n';
        automationResults.forEach(result => {
            csv += `${result.bookingNumber},${result.hotelConf},${result.success ? 'Success' : 'Failed'},${result.message},${result.timestamp}\n`;
        });
        return csv;
    }

    function downloadFile(content, filename) {
        const blob = new Blob([content], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }
});