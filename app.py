import streamlit as st
import pandas as pd
import numpy as np
import re
from io import BytesIO
import openpyxl

# إعداد الصفحة
st.set_page_config(
    page_title="أتمتة إضافة المراجع - WebBeds & Almatar",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "تطبيق أتمتة إضافة المراجع - الإصدار 2.0"
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
            <img src="data:image/png;base64,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data:image/png;base64,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" alt="WebBeds Logo" style="max-width: 150px;">
        </div>
    </div>
    """, unsafe_allow_html=True)
    
st.markdown("<h1 style='text-align: center; color: #d32f2f;'>🤖 أتمتة إضافة المراجع</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #666;'>WebBeds & Almatar</h3>", unsafe_allow_html=True)

def load_excel(file, sheet_name=None):
    """تحميل ملف Excel أو CSV"""
    try:
        # التحقق من نوع الملف
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        elif file.name.endswith('.xls'):
            # استخدام xlrd لملفات Excel القديمة
            if sheet_name:
                return pd.read_excel(file, sheet_name=sheet_name, engine='xlrd')
            else:
                return pd.read_excel(file, engine='xlrd')
        elif file.name.endswith('.xlsx'):
            # استخدام openpyxl لملفات Excel الحديثة
            if sheet_name:
                return pd.read_excel(file, sheet_name=sheet_name, engine='openpyxl')
            else:
                return pd.read_excel(file, engine='openpyxl')
        else:
            st.error(f"نوع الملف غير مدعوم: {file.name}")
            return None
    except Exception as e:
        st.error(f"خطأ في تحميل الملف: {str(e)}")
        return None

def load_excel_almatar(file, sheet_name=None, skip_rows=0):
    """تحميل ملف Almatar مع تخطي صفوف معينة"""
    try:
        # التحقق من نوع الملف
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, skiprows=skip_rows)
        elif file.name.endswith('.xls'):
            if sheet_name:
                df = pd.read_excel(file, sheet_name=sheet_name, engine='xlrd', skiprows=skip_rows)
            else:
                df = pd.read_excel(file, engine='xlrd', skiprows=skip_rows)
        elif file.name.endswith('.xlsx'):
            if sheet_name:
                df = pd.read_excel(file, sheet_name=sheet_name, engine='openpyxl', skiprows=skip_rows)
            else:
                df = pd.read_excel(file, engine='openpyxl', skiprows=skip_rows)
        else:
            st.error(f"نوع الملف غير مدعوم: {file.name}")
            return None
            
        # التحقق من أن df هو DataFrame وليس dict
        if isinstance(df, dict):
            # إذا كان dict، اختر أول sheet
            df = list(df.values())[0]
            
        # إذا كان الصف الأول يحتوي على headers صحيحة، استخدمها
        if len(df) > 0:
            first_row = df.iloc[0]
            # إذا كان الصف الأول يحتوي على كلمات مثل "Booking" أو "External"
            if any(isinstance(val, str) and ('booking' in str(val).lower() or 'external' in str(val).lower() or 'reference' in str(val).lower()) for val in first_row):
                # استخدام الصف الأول كـ headers
                new_headers = [str(val).strip() for val in first_row]
                df.columns = new_headers
                df = df.iloc[1:].reset_index(drop=True)  # إزالة صف الـ headers
                
        return df
    except Exception as e:
        st.error(f"خطأ في تحميل الملف: {str(e)}")
        return None

def find_almatar_columns(df):
    """العثور على الأعمدة المطابقة في ملف Almatar بناءً على الأسماء"""
    booking_col = None
    external_ref_col = None
    
    for col in df.columns:
        col_lower = str(col).lower().strip()
        # البحث عن عمود رقم الحجز
        if 'booking' in col_lower or 'code' in col_lower or 'booking code' in col_lower:
            booking_col = col
        # البحث عن عمود المرجع الخارجي
        if 'external' in col_lower or 'reference' in col_lower or 'property' in col_lower:
            external_ref_col = col
    
    return booking_col, external_ref_col

def should_skip_row(booking_code):
    """التحقق إذا كان يجب تخطي هذا الصف (مثل SENT, sent، إلخ) - فقط إذا لم يكن به أرقام"""
    if pd.isna(booking_code):
        return True
    
    booking_str = str(booking_code).strip()
    
    # إذا كان يحتوي على أرقام والنص، احفظه
    has_digit = any(c.isdigit() for c in booking_str)
    if has_digit:
        return False
    
    # إذا كان نص فقط بدون أرقام، تحقق من الكلمات المفتاحية
    booking_str_upper = booking_str.upper()
    skip_keywords = ['SENT', 'SENDING', 'BLOCKED', 'CANCELLED', 'ERROR', 'TEST']
    
    for keyword in skip_keywords:
        if keyword in booking_str_upper:
            return True
    
    return False

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

def get_unique_companies(jood_df):
    """الحصول على قائمة الشركات الفريدة من جود"""
    if 'ClientName' in jood_df.columns:
        return sorted(jood_df['ClientName'].dropna().unique().tolist())
    return []

def filter_jood_by_company(jood_df, company_name):
    """تصفية ملف جود حسب اسم الشركة"""
    if 'ClientName' not in jood_df.columns:
        return jood_df
    return jood_df[jood_df['ClientName'] == company_name].reset_index(drop=True)

def clean_almatar_file(almatar_df):
    """إزالة أول صفين من ملف Almatar وتنظيف البيانات"""
    if len(almatar_df) > 2:
        almatar_df = almatar_df.iloc[2:].reset_index(drop=True)
    return almatar_df

def extract_hcn_numbers(hcn_str):
    """استخراج أرقام HCN من سترينج قد يكون مفصول بـ - أو , أو space"""
    if pd.isna(hcn_str) or str(hcn_str).strip() == '':
        return []
    
    hcn_str = str(hcn_str).strip()
    # محاولة الفصل بـ - أو , أو space
    if '-' in hcn_str:
        return [h.strip() for h in hcn_str.split('-')]
    elif ',' in hcn_str:
        return [h.strip() for h in hcn_str.split(',')]
    elif ' ' in hcn_str:
        return [h.strip() for h in hcn_str.split(' ') if h.strip()]
    return [hcn_str]

def format_multiple_hcn(hcn_list):
    """تنسيق أرقام HCN المتعددة بصيغة 1454830-1454831"""
    if not hcn_list:
        return ''
    hcn_list = [str(h).strip() for h in hcn_list if h]
    if len(hcn_list) == 1:
        return hcn_list[0]
    return '-'.join(hcn_list)

def compare_almatar_with_jood(almatar_df, jood_df):
    """مقارنة ملف Almatar مع جود وتحديد الحجوزات التي تحتاج HCN"""
    
    # التحقق من الأعمدة المطلوبة
    required_almatar = ['Booking code in the sheet Almatar', 'External reference (from the property)']
    required_jood = ['ClientReference', 'HotelConf']
    
    missing_almatar = [col for col in required_almatar if col not in almatar_df.columns]
    missing_jood = [col for col in required_jood if col not in jood_df.columns]
    
    if missing_almatar:
        st.error(f"أعمدة مفقودة في ملف Almatar: {', '.join(missing_almatar)}")
        return None, None
    
    if missing_jood:
        st.error(f"أعمدة مفقودة في ملف جود: {', '.join(missing_jood)}")
        return None, None
    
    # تشخيص البيانات
    st.write(f"عدد صفوف Almatar: {len(almatar_df)}")
    st.write(f"عدد صفوف جود: {len(jood_df)}")
    st.write(f"أعمدة Almatar: {list(almatar_df.columns)}")
    st.write(f"أعمدة جود: {list(jood_df.columns)}")
    
    # تنظيف أسماء الأعمدة
    almatar_df.columns = almatar_df.columns.str.strip()
    jood_df.columns = jood_df.columns.str.strip()
    
    col_booking_code = 'Booking code in the sheet Almatar'
    col_ext_ref = 'External reference (from the property)'
    col_client_ref = 'ClientReference'
    col_hotel_conf = 'HotelConf'
    
    # تجهيز البيانات
    almatar_df[col_booking_code] = almatar_df[col_booking_code].astype(str).str.strip()
    jood_df[col_client_ref] = jood_df[col_client_ref].astype(str).str.strip()
    
    # تنظيف أعمدة HCN
    almatar_df[col_ext_ref] = almatar_df[col_ext_ref].fillna('').astype(str).str.strip()
    almatar_df[col_ext_ref] = almatar_df[col_ext_ref].apply(lambda x: x.replace('.0', '') if x.endswith('.0') else x)
    
    jood_df[col_hotel_conf] = jood_df[col_hotel_conf].fillna('').astype(str).str.strip()
    jood_df[col_hotel_conf] = jood_df[col_hotel_conf].apply(lambda x: x.replace('.0', '') if x.endswith('.0') else x)
    
    # عينة من البيانات
    st.write("\nعينة من Almatar:")
    st.write(almatar_df[[col_booking_code, col_ext_ref]].head())
    st.write("\nعينة من جود:")
    st.write(jood_df[[col_client_ref, col_hotel_conf]].head())
    
    # تجميع بيانات جود (لحل مشكلة التكرار)
    jood_agg = jood_df.groupby(col_client_ref)[col_hotel_conf].apply(
        lambda x: set([i for i in x if i != '' and i != 'nan'])
    ).reset_index()
    jood_agg.rename(columns={col_hotel_conf: 'Jood_Confs_Set'}, inplace=True)
    
    st.write(f"عدد صفوف جود بعد التجميع: {len(jood_agg)}")
    st.write("عينة من جود المجمع:")
    st.write(jood_agg.head())
    
    # دمج الملفين
    merged_df = pd.merge(almatar_df, jood_agg, left_on=col_booking_code, right_on=col_client_ref, how='left')
    
    st.write(f"عدد صفوف بعد الدمج: {len(merged_df)}")
    st.write("عينة من المدمج:")
    st.write(merged_df[['Booking code in the sheet Almatar', 'External reference (from the property)', 'Jood_Confs_Set']].head())
    
    # منطق المقارنة واستخراج النواقص
    missing_hcn_rows = []
    results = []
    
    for index, row in merged_df.iterrows():
        booking_code = row[col_booking_code]
        almatar_val_raw = row[col_ext_ref]
        
        # استخراج الأرقام الموجودة حالياً في المطار
        almatar_vals_set = set([x for x in re.split(r'[-,\s]+', almatar_val_raw) if x])
        
        # الأرقام الموجودة في جود
        jood_vals_set = row['Jood_Confs_Set']
        
        if isinstance(jood_vals_set, set) and len(jood_vals_set) > 0:
            # ما هي الأرقام الموجودة في جود ولكنها غير موجودة في المطار؟
            missing_in_almatar = jood_vals_set - almatar_vals_set
            
            # إعداد نتيجة المقارنة
            expected_hcn = '-'.join(sorted(jood_vals_set))
            current_hcn = almatar_val_raw if almatar_val_raw else 'فارغ'
            
            result = {
                'Booking_Code': booking_code,
                'Current_External_Reference': current_hcn,
                'Expected_HCN_from_Jood': expected_hcn,
                'HCN_Match': 'مطابق' if len(missing_in_almatar) == 0 else 'غير مطابق',
                'Missing_Count': len(missing_in_almatar),
                'Status': 'مكتمل' if len(missing_in_almatar) == 0 else 'يحتاج إجراء'
            }
            results.append(result)
            
            # إضافة النواقص للقائمة
            if len(missing_in_almatar) > 0:
                for m in missing_in_almatar:
                    missing_hcn_rows.append({
                        'ClientReference': booking_code,
                        'HotelConf': m
                    })
    
    st.write(f"عدد النتائج: {len(results)}")
    st.write(f"عدد النواقص: {len(missing_hcn_rows)}")
    
    return pd.DataFrame(results), pd.DataFrame(missing_hcn_rows)

def compare_files(webbeds_df, jood_df):
    """مقارنة ملفات WebBeds مع جود وإرجاع الحجوزات التي تحتاج مراجع"""
    
    # التحقق من الأعمدة المطلوبة
    required_webbeds = ['WebBeds Booking Number', 'Supplier reference']
    required_jood = ['Client ref', 'HTL RSV #']
    
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
    
    # تحويل Client ref إلى نص
    jood_df = jood_df.copy()
    jood_df['Client_ref_clean'] = jood_df['Client ref'].astype(str)
    
    results = []
    automation_data = []
    
    for idx, wb_row in webbeds_df.iterrows():
        booking_number = wb_row['BookingNumber']
        supplier_ref = wb_row['Supplier reference']
        
        # البحث عن المطابقة في ملف جود
        jood_match = jood_df[jood_df['Client_ref_clean'] == booking_number]
        
        if not jood_match.empty:
            jood_row = jood_match.iloc[0]
            htel_rsv = jood_row['HTL RSV #']
            
            # التحقق من حالة Supplier Reference
            needs_reference = not is_valid_supplier_reference(supplier_ref)
            
            result = {
                'WebBeds_Booking_Number': wb_row['WebBeds Booking Number'],
                'Booking_Number': booking_number,
                'Current_Supplier_Reference': supplier_ref,
                'Supplier_Reference_Valid': is_valid_supplier_reference(supplier_ref),
                'Jood_Match': 'موجود',
                'HTL_RSV': htel_rsv,
                'Action_Needed': 'يحتاج إضافة مرجع' if needs_reference else 'موجود بالفعل',
                'Status': 'يحتاج إجراء' if needs_reference else 'مكتمل'
            }
            
            # إضافة للأتمتة إذا كان يحتاج مرجع
            if needs_reference:
                automation_data.append({
                    'ClientReference': booking_number,
                    'HotelConf': htel_rsv
                })
        else:
            result = {
                'WebBeds_Booking_Number': wb_row['WebBeds Booking Number'],
                'Booking_Number': booking_number,
                'Current_Supplier_Reference': supplier_ref,
                'Supplier_Reference_Valid': is_valid_supplier_reference(supplier_ref),
                'Jood_Match': 'لا يوجد',
                'HTL_RSV': '',
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

# قسم اختيار نوع الشركة
st.header("🏢 اختيار نوع الشركة")

company_type = st.selectbox(
    "اختر نوع الشركة للمعالجة:",
    ["اختر...", "WebBeds", "Almatar", "EET Global", "Traveasy", "TDS", "GTE", "العطايا (Alataya)"],
    key="company_type_select"
)

st.markdown("---")

if company_type != "اختر...":
    st.header(f"📁 رفع الملفات - {company_type}")
    
    # رفع ملف جود
    jood_file = st.file_uploader(
        "ملف جود (arrivals_jood)", 
        type=['xlsx', 'xls', 'csv'], 
        key="jood_main",
        help="ملف يحتوي على بيانات الحجوزات من جود"
    )
    
    jood_df_main = None
    selected_company = None
    company_list = []
    
    if jood_file:
        jood_df_main = load_excel(jood_file)
        
        if company_type == "Almatar" or company_type in ["EET Global", "Traveasy", "TDS", "GTE", "العطايا (Alataya)"]:
            # للـ Almatar والشركات الأخرى: اختيار شركة من القائمة
            company_list = get_unique_companies(jood_df_main)
            
            if company_list:
                st.success(f"تم العثور على {len(company_list)} شركة في الملف")
                selected_company = st.selectbox("اختر الشركة:", company_list, key="company_select")
                
                if selected_company:
                    company_jood_df = filter_jood_by_company(jood_df_main, selected_company)
                    st.info(f"✅ تم تصفية الملف للشركة: **{selected_company}** - عدد الحجوزات: {len(company_jood_df)}")
            else:
                st.warning("⚠️ لم يتم العثور على عمود ClientName في الملف")
        else:
            # للـ WebBeds: استخدام الملف كاملاً
            company_jood_df = jood_df_main
            selected_company = "WebBeds"
            st.success(f"✅ تم تحميل ملف جود - عدد الحجوزات: {len(company_jood_df)}")
    else:
        st.info("📁 الرجاء تحميل ملف جود أولاً")

    # رفع ملف الشركة
    if jood_file and (company_type == "WebBeds" or selected_company):
        st.markdown("---")
        
        if company_type == "Almatar" or company_type in ["EET Global", "Traveasy", "TDS", "GTE", "العطايا (Alataya)"]:
            st.subheader(f"📋 رفع ملف {selected_company}")
            company_file = st.file_uploader(
                f"ملف {selected_company}", 
                type=['xlsx', 'xls', 'csv'], 
                key="company_file",
                help="ملف يحتوي على بيانات الحجوزات من الشركة"
            )
            
            if company_file:
                # تحميل الملف بدون تخطي صفوف
                company_df = load_excel_almatar(company_file, skip_rows=0)
                if company_df is not None:
                    st.info(f"✅ تم تحميل الملف. عدد الصفوف: {len(company_df)}")
                    
                    # البحث التلقائي عن الأعمدة
                    booking_col, external_ref_col = find_almatar_columns(company_df)
                    
                    if booking_col and external_ref_col:
                        st.success(f"✅ تم العثور على الأعمدة تلقائياً:\n- رقم الحجز: **{booking_col}**\n- المرجع الخارجي: **{external_ref_col}**")
                        
                        # تصفية الصفوف غير المرغوبة
                        company_df_filtered = company_df[
                            ~company_df[booking_col].apply(should_skip_row)
                        ].reset_index(drop=True)
                        
                        skipped_count = len(company_df) - len(company_df_filtered)
                        if skipped_count > 0:
                            st.info(f"⚠️ تم تخطي {skipped_count} صفوف تحتوي على كلمات غير صالحة (SENT, TEST, إلخ)")
                        
                        st.info(f"📊 عدد الحجوزات الصحيحة للمعالجة: {len(company_df_filtered)}")
                        
                        # معالجة البيانات بالأعمدة المكتشفة
                        if st.button("🔍 بدء المقارنة والمعالجة", key="almatar_process"):
                            with st.spinner("جاري المقارنة والمعالجة..."):
                                # إعادة تسمية الأعمدة مؤقتاً
                                company_df_temp = company_df_filtered.copy()
                                company_df_temp = company_df_temp.rename(columns={
                                    booking_col: 'Booking code in the sheet Almatar',
                                    external_ref_col: 'External reference (from the property)'
                                })
                                
                                # مقارنة مع جود
                                comparison_results, to_add_data = compare_almatar_with_jood(company_df_temp, company_jood_df)
                                if comparison_results is not None:
                                    st.session_state['comparison_results'] = comparison_results
                                    st.session_state['automation_data'] = to_add_data
                                    st.session_state['company_type'] = 'almatar'
                                    st.session_state['selected_company'] = selected_company
                                    st.session_state['audit_completed'] = True
                                    st.success("✅ تمت المعالجة بنجاح!")
                    else:
                        st.error("❌ لم يتم العثور على الأعمدة المطلوبة. تأكد من أن الملف يحتوي على:")
                        st.write("- عمود يحتوي على كلمة 'booking' أو 'code'")
                        st.write("- عمود يحتوي على كلمة 'external' أو 'reference' أو 'property'")
        
        elif company_type == "WebBeds":
            st.subheader("📋 رفع ملف WebBeds")
            webbeds_file = st.file_uploader(
                "ملف WebBeds", 
                type=['xlsx', 'xls', 'csv'], 
                key="webbeds_file",
                help="ملف يحتوي على WebBeds Booking Number و Supplier reference"
            )
            
            if webbeds_file:
                # اختيار الورقة إذا كان ملف Excel
                webbeds_sheet = None
                sheets = get_sheet_names(webbeds_file)
                if len(sheets) > 1:
                    webbeds_sheet = st.selectbox("اختر الورقة:", sheets, key="wb_sheet")
                else:
                    webbeds_sheet = sheets[0] if sheets else None
                
                if st.button("🔍 بدء المقارنة والمعالجة", key="webbeds_process"):
                    with st.spinner("جاري المقارنة والمعالجة..."):
                        webbeds_df = load_excel(webbeds_file, webbeds_sheet)
                        
                        if webbeds_df is not None:
                            comparison_results, automation_data = compare_files(webbeds_df, company_jood_df)
                            
                            if comparison_results is not None:
                                st.session_state['comparison_results'] = comparison_results
                                st.session_state['automation_data'] = automation_data
                                st.session_state['company_type'] = 'webbeds'
                                st.session_state['selected_company'] = 'WebBeds'
                                st.session_state['audit_completed'] = True
                                st.success("✅ تمت المقارنة بنجاح!")
else:
    st.info("🔸 الرجاء اختيار نوع الشركة أولاً")



# عرض النتائج
if st.session_state.get('audit_completed', False):
    st.markdown("---")
    st.header("📊 نتائج المقارنة")
    
    comparison_results = st.session_state['comparison_results']
    automation_data = st.session_state['automation_data']
    
    # طباعة أسماء الأعمدة للتشخيص
    st.write("أعمدة النتائج:", list(comparison_results.columns))
    
    # إحصائيات سريعة
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_bookings = len(comparison_results)
        st.metric("إجمالي الحجوزات المطابقة", total_bookings)
    
    with col2:
        # للـ Almatar: جميع النتائج موجودة في جود
        if st.session_state.get('company_type') == 'almatar':
            matched_bookings = total_bookings
        else:
            # للـ WebBeds: استخدام العمود الأصلي
            if 'Jood_Match' in comparison_results.columns:
                matched_bookings = len(comparison_results[comparison_results['Jood_Match'] == 'موجود'])
            else:
                matched_bookings = total_bookings
        st.metric("الحجوزات الموجودة في جود", matched_bookings)
    
    with col3:
        # التحقق من وجود عمود Status
        if 'Status' in comparison_results.columns:
            need_action = len(comparison_results[comparison_results['Status'] == 'يحتاج إجراء'])
        else:
            need_action = 0
        st.metric("يحتاج إضافة مرجع", need_action)
    
    with col4:
        # التحقق من وجود عمود Status
        if 'Status' in comparison_results.columns:
            completed = len(comparison_results[comparison_results['Status'] == 'مكتمل'])
        else:
            completed = 0
        st.metric("مكتمل", completed)
    
    # عرض الجدول مع فلترة
    st.subheader("تفاصيل المقارنة")
    
    # التحقق من وجود عمود Status للفلترة
    if 'Status' in comparison_results.columns:
        filter_option = st.selectbox("عرض:", ["الكل", "يحتاج إضافة مرجع", "مكتمل"])
        
        if filter_option == "يحتاج إضافة مرجع":
            filtered_results = comparison_results[comparison_results['Status'] == 'يحتاج إجراء']
        elif filter_option == "مكتمل":
            filtered_results = comparison_results[comparison_results['Status'] == 'مكتمل']
        else:
            filtered_results = comparison_results
    else:
        filtered_results = comparison_results
    
    st.dataframe(filtered_results, use_container_width=True)
    
    # قسم التحميل
    st.markdown("---")
    st.header("📥 تحميل النتائج")
    
    # تحديد نوع التحميل حسب نوع الشركة
    company_type_session = st.session_state.get('company_type', '')
    selected_company_session = st.session_state.get('selected_company', '')
    
    if company_type_session == 'almatar':
        # لـ Almatar: تحميل CSV للحجوزات التي تحتاج HCN
        if not st.session_state['automation_data'].empty:
            csv_data = st.session_state['automation_data'].to_csv(index=False)
            
            st.download_button(
                label="📄 تحميل ملف الأتمتة (CSV)",
                data=csv_data,
                file_name=f"{selected_company_session}_automation_data.csv",
                mime="text/csv"
            )
            st.success(f"✅ ملف CSV جاهز للتحميل - يحتوي على {len(st.session_state['automation_data'])} حجز")
        else:
            st.info("ℹ️ جميع الحجوزات لديها HCN بالفعل - لا توجد حجوزات للإضافة")
    else:
        # الخيار الأصلي لـ WebBeds
        col1, col2 = st.columns(2)
        
        with col1:
            # تحميل نتائج المقارنة
            if 'Status' in comparison_results.columns:
                need_action_df = comparison_results[comparison_results['Status'] == 'يحتاج إجراء']
                completed_df = comparison_results[comparison_results['Status'] == 'مكتمل']
            else:
                need_action_df = comparison_results
                completed_df = pd.DataFrame()
                
            comparison_excel = export_excel({
                'comparison_results': comparison_results,
                'need_action': need_action_df,
                'completed': completed_df
            })
            
            st.download_button(
                label="📥 تحميل نتائج المقارنة",
                data=comparison_excel,
                file_name="webbeds_comparison_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col2:
            # تحميل ملف الأتمتة (ClientReference + HotelConf فقط)
            if not st.session_state['automation_data'].empty:
                # تحميل CSV (أبسط للقراءة)
                csv_data = st.session_state['automation_data'].to_csv(index=False)
                
                st.download_button(
                    label="📄 تحميل ملف الأتمتة (CSV)",
                    data=csv_data,
                    file_name="automation_data.csv",
                    mime="text/csv"
                )
                
                st.success(f"✅ ملف الأتمتة يحتوي على {len(st.session_state['automation_data'])} حجز")
            else:
                st.info("لا توجد حجوزات تحتاج إضافة مراجع")

# معلومات إضافية
st.markdown("---")
st.markdown("""
### 📋 تعليمات الاستخدام:

#### 🏢 **WebBeds**:
1. **رفع الملفات**:
   - ملف جود (يحتوي على ClientReference و HotelConf)
   - ملف WebBeds (يحتوي على WebBeds Booking Number و Supplier reference)

2. **المقارنة**:
   - يستخرج الأرقام من WebBeds Booking Number (يزيل HTL-WBD-)
   - يطابق مع ClientReference في ملف جود
   - يتحقق من وجود Supplier Reference صحيح

#### 🏢 **Almatar والشركات الأخرى (EET Global, Traveasy, TDS, GTE, العطايا)**:
1. **رفع الملفات**:
   - ملف جود (يحتوي على ClientReference و HotelConf)
   - اختيار الشركة من القائمة
   - ملف الشركة (يحتوي على Booking Code و External Reference)

2. **المقارنة**:
   - يطابق Booking Code مع ClientReference في ملف جود
   - يتحقق من وجود External Reference (HCN)
   - يحدد الحجوزات التي تحتاج إضافة HCN

#### 📥 **التحميل**:
- ملف نتائج المقارنة الكامل
- ملف CSV للأتمتة يحتوي على ClientReference و HotelConf

#### 🤖 **استخدام ملف الأتمتة**:
- حمل ملف CSV
- استخدمه في Chrome Extension للأتمتة
- يحتوي على ClientReference (للبحث) و HotelConf (للإضافة)
""")