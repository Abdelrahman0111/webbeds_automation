// Content script للتفاعل مع صفحات WebBeds و Almatar
let automationData = [];
let currentIndex = 0;
let automationResults = [];
let currentPlatform = 'webbeds';

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'startAutomation') {
        automationData = request.data;
        currentPlatform = request.platform || 'webbeds';
        currentIndex = 0;
        automationResults = [];
        
        console.log('بدء الأتمتة مع', automationData.length, 'حجز على منصة', currentPlatform);
        
        if (currentPlatform === 'webbeds') {
            startWebBedsAutomation();
        } else {
            // جميع الشركات الأخرى تستخدم نفس نظام Almatar
            startAlmatarAutomation();
        }
        
        sendResponse({success: true});
    }
    return true;
});

// ===== WebBeds Automation =====
function startWebBedsAutomation() {
    if (window.location.href.includes('/bookings')) {
        setTimeout(() => processNextWebBedsBooking(), 1000);
    } else {
        window.location.href = 'https://extranet.webbeds.com/5520905/bookings';
    }
}

function processNextWebBedsBooking() {
    if (currentIndex >= automationData.length) {
        chrome.runtime.sendMessage({
            action: 'automationComplete',
            results: automationResults
        });
        return;
    }

    const booking = automationData[currentIndex];
    
    chrome.runtime.sendMessage({
        action: 'updateProgress',
        current: currentIndex + 1,
        total: automationData.length
    });

    searchWebBedsBooking(booking.bookingNumber)
        .then(() => addWebBedsSupplierReference(booking.hotelConf))
        .then((result) => {
            automationResults.push({
                bookingNumber: booking.bookingNumber,
                hotelConf: booking.hotelConf,
                success: result.success,
                message: result.message,
                timestamp: new Date().toISOString()
            });
            
            currentIndex++;
            setTimeout(processNextWebBedsBooking, 3000);
        })
        .catch((error) => {
            automationResults.push({
                bookingNumber: booking.bookingNumber,
                hotelConf: booking.hotelConf,
                success: false,
                message: error.message,
                timestamp: new Date().toISOString()
            });
            
            currentIndex++;
            setTimeout(processNextWebBedsBooking, 3000);
        });
}

function searchWebBedsBooking(bookingNumber) {
    return new Promise((resolve, reject) => {
        try {
            const allHotelsFilter = document.querySelector('span.hotel-filter[data-value="1"]');
            if (allHotelsFilter && !allHotelsFilter.classList.contains('active')) {
                allHotelsFilter.click();
                setTimeout(() => continueWebBedsSearch(), 1000);
            } else {
                continueWebBedsSearch();
            }

            function continueWebBedsSearch() {
                const searchInput = document.getElementById('referenceNumber');
                if (searchInput) {
                    searchInput.value = '';
                    searchInput.focus();
                    
                    let i = 0;
                    const typeInterval = setInterval(() => {
                        if (i < bookingNumber.length) {
                            searchInput.value += bookingNumber[i];
                            searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                            i++;
                        } else {
                            clearInterval(typeInterval);
                            
                            setTimeout(() => {
                                const searchButton = document.getElementById('searchBookingsButton');
                                if (searchButton) {
                                    searchButton.click();
                                    setTimeout(() => resolve(), 3000);
                                } else {
                                    reject(new Error('لم يتم العثور على زر البحث'));
                                }
                            }, 500);
                        }
                    }, 100);
                } else {
                    reject(new Error('لم يتم العثور على حقل البحث'));
                }
            }
        } catch (error) {
            reject(error);
        }
    });
}

function addWebBedsSupplierReference(hotelConf) {
    return new Promise((resolve, reject) => {
        try {
            const addRefButton = document.querySelector('button.add-reference-button');
            
            if (addRefButton) {
                addRefButton.click();
                
                setTimeout(() => {
                    const refInput = document.getElementById('referenceNumberPopup');
                    if (refInput) {
                        refInput.value = hotelConf;
                        refInput.dispatchEvent(new Event('input', { bubbles: true }));
                        
                        setTimeout(() => {
                            const saveButton = document.querySelector('button.save-button');
                            if (saveButton) {
                                saveButton.click();
                                setTimeout(() => {
                                    resolve({
                                        success: true,
                                        message: 'تم إضافة المرجع بنجاح'
                                    });
                                }, 2000);
                            } else {
                                reject(new Error('لم يتم العثور على زر الحفظ'));
                            }
                        }, 500);
                    } else {
                        reject(new Error('لم يتم العثور على حقل إدخال المرجع'));
                    }
                }, 1000);
            } else {
                const pageText = document.body.innerText;
                if (pageText.includes(hotelConf)) {
                    resolve({
                        success: true,
                        message: 'تم اضافتها مسبقا'
                    });
                } else {
                    resolve({
                        success: true,
                        message: 'تم اضافتها مسبقا'
                    });
                }
            }
        } catch (error) {
            reject(error);
        }
    });
}

// ===== Almatar Automation =====
function startAlmatarAutomation() {
    // التحقق من وجود صفحة عدم الإذن
    if (window.location.href.includes('sinPermiso.aspx')) {
        alert('لا يوجد إذن للوصول. يرجى تسجيل الدخول أولاً.');
        return;
    }
    
    // تحديد الرابط حسب المنصة
    let targetUrl = getTargetUrlForPlatform();
    
    if (!window.location.href.includes('listadoReservas.aspx')) {
        window.location.href = targetUrl;
        return;
    }
    
    setTimeout(() => processNextAlmatarBooking(), 2000);
}

function getTargetUrlForPlatform() {
    const platformUrls = {
        'almatar': 'https://portal.arabiabeds.com/extranet/alojamiento/listadoReservas.aspx?alojamiento=587&idcco=707&verVigente=1',
        'eet': 'https://www.eetglobal.com/Extranet/alojamiento/listadoReservas.aspx?alojamiento=14759&idcco=60451&verVigente=1',
        'traveasy': 'https://hotels.holidayme.com/extranet/alojamiento/listadoReservas.aspx?alojamiento=288&idcco=2510&verVigente=1',
        'tds': 'https://go.tdstravel.com/extranet/alojamiento/listadoReservas.aspx?alojamiento=24411&idcco=2308&verVigente=1',
        'gte': 'https://www.gte.travel/extranet/alojamiento/listadoReservas.aspx?alojamiento=3166&idcco=12017&verVigente=1',
        'alataya': 'https://www.attaya.travel/extranet/alojamiento/listadoReservas.aspx?alojamiento=452&idcco=576&verVigente=1'
    };
    
    return platformUrls[currentPlatform] || platformUrls['almatar'];
}



function processNextAlmatarBooking() {
    if (currentIndex >= automationData.length) {
        chrome.runtime.sendMessage({
            action: 'automationComplete',
            results: automationResults
        });
        return;
    }

    const booking = automationData[currentIndex];
    
    chrome.runtime.sendMessage({
        action: 'updateProgress',
        current: currentIndex + 1,
        total: automationData.length
    });

    searchAlmatarBooking(booking.bookingNumber)
        .then(() => addAlmatarHotelConf(booking.hotelConf))
        .then((result) => {
            automationResults.push({
                bookingNumber: booking.bookingNumber,
                hotelConf: booking.hotelConf,
                success: result.success,
                message: result.message,
                timestamp: new Date().toISOString()
            });
            
            currentIndex++;
            setTimeout(processNextAlmatarBooking, 4000);
        })
        .catch((error) => {
            automationResults.push({
                bookingNumber: booking.bookingNumber,
                hotelConf: booking.hotelConf,
                success: false,
                message: error.message,
                timestamp: new Date().toISOString()
            });
            
            currentIndex++;
            setTimeout(processNextAlmatarBooking, 4000);
        });
}

function searchAlmatarBooking(bookingCode) {
    return new Promise((resolve, reject) => {
        try {
            // البحث عن حقل البحث
            const searchInput = document.getElementById('localizador-inputEl');
            if (!searchInput) {
                reject(new Error('لم يتم العثور على حقل البحث'));
                return;
            }

            // مسح الحقل وإدخال رقم الحجز
            searchInput.value = '';
            searchInput.focus();
            
            // كتابة رقم الحجز
            let i = 0;
            const typeInterval = setInterval(() => {
                if (i < bookingCode.length) {
                    searchInput.value += bookingCode[i];
                    searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                    i++;
                } else {
                    clearInterval(typeInterval);
                    
                    // الضغط على زر Filter
                    setTimeout(() => {
                        const filterButton = document.getElementById('botonBuscar-btnInnerEl');
                        if (filterButton) {
                            filterButton.click();
                            
                            // انتظار النتائج
                            setTimeout(() => {
                                resolve();
                            }, 3000);
                        } else {
                            reject(new Error('لم يتم العثور على زر Filter'));
                        }
                    }, 500);
                }
            }, 100);
            
        } catch (error) {
            reject(error);
        }
    });
}

function addAlmatarHotelConf(hotelConf) {
    return new Promise((resolve, reject) => {
        try {
            // البحث عن زر المعلومات
            const infoButton = document.querySelector('img[src="/extranet/images/alojamiento/information.png"]');
            
            if (!infoButton) {
                reject(new Error('لم يتم العثور على زر المعلومات'));
                return;
            }

            // استخراج onclick من الزر
            const onclickAttr = infoButton.getAttribute('onclick');
            if (!onclickAttr) {
                reject(new Error('لم يتم العثور على onclick'));
                return;
            }

            // استخراج المعاملات من onclick
            const match = onclickAttr.match(/mostrarBono\("([^"]+)","([^"]+)"\)/);
            if (!match) {
                reject(new Error('لم يتم استخراج معاملات الرابط'));
                return;
            }

            const params = match[1]; // مثل: "38295#37596"
            const [idres, idlre] = params.split('#');
            
            // بناء الرابط الجديد حسب المنصة الحالية
            const currentDomain = window.location.hostname;
            const newUrl = `https://${currentDomain}/extranet/alojamiento/datosLineaReservaALO.aspx?idres=${idres}&idlre=${idlre}&pintarCoste=true`;
            
            // فتح النافذة الجديدة
            const newWindow = window.open(newUrl, '_blank');
            
            if (!newWindow) {
                reject(new Error('فشل في فتح النافذة الجديدة'));
                return;
            }

            // انتظار تحميل الصفحة الجديدة
            setTimeout(() => {
                try {
                    // البحث عن حقل localizadorHotel في النافذة الجديدة
                    const hotelInput = newWindow.document.getElementById('localizadorHotel');
                    if (!hotelInput) {
                        newWindow.close();
                        reject(new Error('لم يتم العثور على حقل localizadorHotel'));
                        return;
                    }

                    // إدخال HotelConf
                    hotelInput.value = hotelConf;
                    hotelInput.dispatchEvent(new Event('input', { bubbles: true }));
                    hotelInput.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    // البحث عن زر Change
                    setTimeout(() => {
                        const changeButton = newWindow.document.getElementById('button-1010-btnEl');
                        if (!changeButton) {
                            newWindow.close();
                            reject(new Error('لم يتم العثور على زر Change'));
                            return;
                        }

                        changeButton.click();
                        
                        // إغلاق النافذة والعودة
                        setTimeout(() => {
                            newWindow.close();
                            resolve({
                                success: true,
                                message: 'تم إضافة HotelConf بنجاح'
                            });
                        }, 2000);
                    }, 1000);
                    
                } catch (error) {
                    newWindow.close();
                    reject(new Error('خطأ في معالجة النافذة الجديدة: ' + error.message));
                }
            }, 3000); // زيادة وقت الانتظار
            
        } catch (error) {
            reject(error);
        }
    });
}
