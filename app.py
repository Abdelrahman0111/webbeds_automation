import streamlit as st
import pandas as pd
import numpy as np
import re
from io import BytesIO
import openpyxl

# إعداد الصفحة
st.set_page_config(
    page_title="أتمتة إضافة مراجع WebBeds",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "تطبيق أتمتة إضافة مراجع WebBeds - الإصدار 1.0"
    }
)

# إضافة شعار WebBeds وتنسيق CSS
st.markdown("""
<style>
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin-bottom: 30px;
    }
    .logo-section {
        text-align: center;
    }
    .logo-section img {
        max-width: 150px;
        height: auto;
    }
    .title-section h1 {
        color: #d32f2f;
        text-align: center;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# عرض الشعار والعنوان
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div class="header-container">
        <div class="logo-section">
            <img src="data:image/png;base64,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" alt="WebBeds Logo" style="max-width: 150px;">
        </div>
    </div>
    """, unsafe_allow_html=True)
    
st.markdown("<h1 style='text-align: center; color: #d32f2f;'>🤖 أتمتة إضافة مراجع WebBeds</h1>", unsafe_allow_html=True)

def load_excel(file, sheet_name=None):
    """تحميل ملف Excel أو CSV"""
    try:
        # التحقق من نوع الملف
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        else:
            if sheet_name:
                return pd.read_excel(file, sheet_name=sheet_name)
            else:
                return pd.read_excel(file)
    except Exception as e:
        st.error(f"خطأ في تحميل الملف: {str(e)}")
        return None

def get_sheet_names(file):
    """الحصول على أسماء الأوراق في ملف Excel (CSV ليس له أوراق)"""
    try:
        if file.name.endswith('.csv'):
            return ['Sheet1']  # CSV ملف واحد فقط
        xl_file = pd.ExcelFile(file)
        return xl_file.sheet_names
    except:
        return []

def extract_booking_number(webbeds_booking):
    """استخراج رقم الحجز من WebBeds Booking Number"""
    if pd.isna(webbeds_booking):
        return ""
    booking_str = str(webbeds_booking)
    number = re.sub(r'HTL-WBD-', '', booking_str)
    return number.strip()

def is_valid_supplier_reference(ref):
    """التحقق من صحة Supplier Reference"""
    if pd.isna(ref) or ref == "" or str(ref).strip() == "":
        return False
    try:
        float(str(ref))
        return True
    except:
        return False

def compare_files(webbeds_df, jood_df):
    """مقارنة ملفات WebBeds مع جود وإرجاع الحجوزات التي تحتاج مراجع"""
    
    # التحقق من الأعمدة المطلوبة
    required_webbeds = ['WebBeds Booking Number', 'Supplier reference']
    required_jood = ['ClientReference', 'HotelConf']
    
    missing_wb = [col for col in required_webbeds if col not in webbeds_df.columns]
    missing_jood = [col for col in required_jood if col not in jood_df.columns]
    
    if missing_wb:
        st.error(f"أعمدة مفقودة في ملف WebBeds: {', '.join(missing_wb)}")
        return None, None
    
    if missing_jood:
        st.error(f"أعمدة مفقودة في ملف جود: {', '.join(missing_jood)}")
        return None, None
    
    # استخراج أرقام الحجز
    webbeds_df = webbeds_df.copy()
    webbeds_df['BookingNumber'] = webbeds_df['WebBeds Booking Number'].apply(extract_booking_number)
    
    # تحويل ClientReference إلى نص
    jood_df = jood_df.copy()
    jood_df['ClientReference'] = jood_df['ClientReference'].astype(str)
    
    results = []
    automation_data = []
    
    for idx, wb_row in webbeds_df.iterrows():
        booking_number = wb_row['BookingNumber']
        supplier_ref = wb_row['Supplier reference']
        
        # البحث عن المطابقة في ملف جود
        jood_match = jood_df[jood_df['ClientReference'] == booking_number]
        
        if not jood_match.empty:
            jood_row = jood_match.iloc[0]
            hotel_conf = jood_row['HotelConf']
            
            # التحقق من حالة Supplier Reference
            needs_reference = not is_valid_supplier_reference(supplier_ref)
            
            result = {
                'WebBeds_Booking_Number': wb_row['WebBeds Booking Number'],
                'Booking_Number': booking_number,
                'Current_Supplier_Reference': supplier_ref,
                'Supplier_Reference_Valid': is_valid_supplier_reference(supplier_ref),
                'Jood_Match': 'موجود',
                'HotelConf': hotel_conf,
                'Action_Needed': 'يحتاج إضافة مرجع' if needs_reference else 'موجود بالفعل',
                'Status': 'يحتاج إجراء' if needs_reference else 'مكتمل'
            }
            
            # إضافة للأتمتة إذا كان يحتاج مرجع
            if needs_reference:
                automation_data.append({
                    'ClientReference': booking_number,
                    'HotelConf': hotel_conf
                })
        else:
            result = {
                'WebBeds_Booking_Number': wb_row['WebBeds Booking Number'],
                'Booking_Number': booking_number,
                'Current_Supplier_Reference': supplier_ref,
                'Supplier_Reference_Valid': is_valid_supplier_reference(supplier_ref),
                'Jood_Match': 'لا يوجد',
                'HotelConf': '',
                'Action_Needed': 'غير موجود في جود',
                'Status': 'لا يحتاج إجراء'
            }
        
        results.append(result)
    
    return pd.DataFrame(results), pd.DataFrame(automation_data)

def export_excel(dict_of_dfs):
    """تصدير عدة DataFrames إلى ملف Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in dict_of_dfs.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()

# واجهة المستخدم
st.markdown("---")

# قسم رفع الملفات
st.header("📁 رفع الملفات")

col1, col2 = st.columns(2)

with col1:
    st.subheader("ملف WebBeds")
    webbeds_file = st.file_uploader("webbeds_sheet.xlsx", type=['xlsx', 'csv'], key="webbeds")
    webbeds_sheet = None
    if webbeds_file:
        sheets = get_sheet_names(webbeds_file)
        if len(sheets) > 1:
            webbeds_sheet = st.selectbox("اختر الورقة:", sheets, key="wb_sheet")
        else:
            webbeds_sheet = sheets[0] if sheets else None

with col2:
    st.subheader("ملف جود (arrivals_jood_webbeds)")
    jood_file = st.file_uploader("arrivals_jood_webbeds.xlsx", type=['xlsx', 'csv'], key="jood")
    jood_sheet = None
    if jood_file:
        sheets = get_sheet_names(jood_file)
        if len(sheets) > 1:
            jood_sheet = st.selectbox("اختر الورقة:", sheets, key="jood_sheet")
        else:
            jood_sheet = sheets[0] if sheets else None

st.markdown("---")

# زر المقارنة
if st.button("🔍 مقارنة الملفات", type="primary"):
    if not all([webbeds_file, jood_file]):
        st.error("يرجى رفع كلا الملفين")
    else:
        with st.spinner("جاري مقارنة الملفات..."):
            webbeds_df = load_excel(webbeds_file, webbeds_sheet)
            jood_df = load_excel(jood_file, jood_sheet)
            
            if all([df is not None for df in [webbeds_df, jood_df]]):
                comparison_results, automation_data = compare_files(webbeds_df, jood_df)
                
                if comparison_results is not None:
                    st.session_state['comparison_results'] = comparison_results
                    st.session_state['automation_data'] = automation_data
                    st.session_state['audit_completed'] = True
                    st.success("✅ تمت المقارنة بنجاح!")

# عرض النتائج
if st.session_state.get('audit_completed', False):
    st.markdown("---")
    st.header("📊 نتائج المقارنة")
    
    comparison_results = st.session_state['comparison_results']
    automation_data = st.session_state['automation_data']
    
    # إحصائيات سريعة
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_bookings = len(comparison_results)
        st.metric("إجمالي الحجوزات", total_bookings)
    
    with col2:
        matched_bookings = len(comparison_results[comparison_results['Jood_Match'] == 'موجود'])
        st.metric("الحجوزات المطابقة", matched_bookings)
    
    with col3:
        need_action = len(comparison_results[comparison_results['Status'] == 'يحتاج إجراء'])
        st.metric("يحتاج إضافة مرجع", need_action)
    
    with col4:
        completed = len(comparison_results[comparison_results['Status'] == 'مكتمل'])
        st.metric("مكتمل", completed)
    
    # عرض الجدول مع فلترة
    st.subheader("تفاصيل المقارنة")
    
    filter_option = st.selectbox("عرض:", ["الكل", "يحتاج إضافة مرجع", "مكتمل", "غير موجود في جود"])
    
    if filter_option == "يحتاج إضافة مرجع":
        filtered_results = comparison_results[comparison_results['Status'] == 'يحتاج إجراء']
    elif filter_option == "مكتمل":
        filtered_results = comparison_results[comparison_results['Status'] == 'مكتمل']
    elif filter_option == "غير موجود في جود":
        filtered_results = comparison_results[comparison_results['Jood_Match'] == 'لا يوجد']
    else:
        filtered_results = comparison_results
    
    st.dataframe(filtered_results, use_container_width=True)
    
    # قسم التحميل
    st.markdown("---")
    st.header("📥 تحميل النتائج")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # تحميل نتائج المقارنة
        comparison_excel = export_excel({
            'comparison_results': comparison_results,
            'need_action': comparison_results[comparison_results['Status'] == 'يحتاج إجراء'],
            'completed': comparison_results[comparison_results['Status'] == 'مكتمل']
        })
        
        st.download_button(
            label="📥 تحميل نتائج المقارنة",
            data=comparison_excel,
            file_name="webbeds_comparison_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col2:
        # تحميل ملف الأتمتة (ClientReference + HotelConf فقط)
        if not automation_data.empty:
            # تحميل CSV (أبسط للقراءة)
            csv_data = automation_data.to_csv(index=False)
            
            st.download_button(
                label="📄 تحميل ملف الأتمتة (CSV)",
                data=csv_data,
                file_name="automation_data.csv",
                mime="text/csv"
            )
            
            automation_excel = export_excel({
                'automation_data': automation_data
            })
            
            st.download_button(
                label="📥 تحميل ملف الأتمتة (Excel)",
                data=automation_excel,
                file_name="automation_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.success(f"✅ ملف الأتمتة يحتوي على {len(automation_data)} حجز")
        else:
            st.info("لا توجد حجوزات تحتاج إضافة مراجع")

# معلومات إضافية
st.markdown("---")
st.markdown("""
### 📋 تعليمات الاستخدام:

1. **رفع الملفات**:
   - ملف WebBeds (يحتوي على WebBeds Booking Number و Supplier reference)
   - ملف جود arrivals_jood_webbeds (يحتوي على ClientReference و HotelConf)

2. **المقارنة**:
   - يستخرج الأرقام من WebBeds Booking Number (يزيل HTL-WBD-)
   - يطابق مع ClientReference في ملف جود
   - يتحقق من وجود Supplier Reference صحيح

3. **التحميل**:
   - ملف نتائج المقارنة الكامل
   - ملف الأتمتة يحتوي على ClientReference و HotelConf فقط للحجوزات التي تحتاج مراجع

### 🤖 استخدام ملف الأتمتة:
- حمل ملف "automation_data.xlsx"
- استخدمه في Chrome Extension للأتمتة
- يحتوي على ClientReference (للبحث) و HotelConf (للإضافة)
""")
