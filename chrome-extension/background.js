// Background script للتعامل مع الأحداث
chrome.runtime.onInstalled.addListener(() => {
    console.log('WebBeds & Almatar Automation Extension installed');
});

// التعامل مع الرسائل بين popup و content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    // تمرير الرسائل بين popup و content script
    if (request.action === 'updateProgress' || request.action === 'automationComplete') {
        // إرسال الرسالة إلى popup
        chrome.runtime.sendMessage(request).catch(() => {
            // تجاهل الخطأ إذا لم يكن popup مفتوح
        });
    }
    return true;
});

// التعامل مع تحديث التبويبات
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        const supportedDomains = [
            'extranet.webbeds.com',
            'portal.arabiabeds.com',
            'www.eetglobal.com',
            'hotels.holidayme.com',
            'go.tdstravel.com',
            'www.gte.travel',
            'www.attaya.travel'
        ];
        
        if (supportedDomains.some(domain => tab.url.includes(domain))) {
            chrome.action.setBadgeText({
                text: '✓',
                tabId: tabId
            });
            chrome.action.setBadgeBackgroundColor({
                color: '#4CAF50',
                tabId: tabId
            });
        }
    }
});