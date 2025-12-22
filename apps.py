import streamlit as st
import pandas as pd
import re
from io import BytesIO

# إعداد صفحة التطبيق
st.set_page_config(page_title="HCN Matcher", layout="wide")

st.title("🔍 HotelConf Matcher & Updater")
st.markdown("""
هذا التطبيق يستخرج الحجوزات التي لها رقم HotelConf في جود ولكنها ناقصة في ملف الشركة.
**يتم استبعاد القيم التي تحتوي على 'sent'.**
""")

# اختيار اسم الشركة
st.header("🏢 اختيار الشركة")
company_name = st.text_input("أدخل اسم الشركة:", placeholder="مثال: Almatar, EET Global, Traveasy, TDS, GTE, العطايا")

if not company_name:
    st.warning("⚠️ يرجى إدخال اسم الشركة أولاً")
    st.stop()

# ---------------------------------------------------------
# 1. تحميل الملفات
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.header(f"1. ملف {company_name}")
    file_almatar = st.file_uploader(f"ارفع ملف {company_name} (xlsx/csv)", type=['xlsx', 'csv'])

with col2:
    st.header("2. ملف جود (Jood)")
    file_jood = st.file_uploader("ارفع ملف Arrivals (csv)", type=['csv'])

# ---------------------------------------------------------
# 2. منطق المعالجة
# ---------------------------------------------------------
if file_almatar and file_jood:
    if st.button("🚀 بدء المعالجة"):
        try:
            # --- قراءة ملف الشركة (مع حذف أول سطرين) ---
            if file_almatar.name.endswith('.xlsx'):
                df_almatar = pd.read_excel(file_almatar, skiprows=2)
            else:
                df_almatar = pd.read_csv(file_almatar, skiprows=2)

            # --- قراءة ملف جود ---
            df_jood = pd.read_csv(file_jood)

            # --- تنظيف أسماء الأعمدة ---
            df_almatar.columns = df_almatar.columns.str.strip()
            df_jood.columns = df_jood.columns.str.strip()

            # تحديد الأعمدة
            col_booking_code = 'Booking code' 
            col_ext_ref = 'External reference (from the property)' 
            col_client_ref = 'ClientReference' 
            col_hotel_conf = 'HotelConf' 

            # --- التأكد من نوع البيانات (String) ---
            df_almatar[col_booking_code] = df_almatar[col_booking_code].astype(str).str.strip()
            df_jood[col_client_ref] = df_jood[col_client_ref].astype(str).str.strip()

            # تنظيف قيم HCN
            df_almatar[col_ext_ref] = df_almatar[col_ext_ref].fillna('').astype(str).str.strip()
            df_almatar[col_ext_ref] = df_almatar[col_ext_ref].apply(lambda x: x.replace('.0', '') if x.endswith('.0') else x)

            df_jood[col_hotel_conf] = df_jood[col_hotel_conf].fillna('').astype(str).str.strip()
            df_jood[col_hotel_conf] = df_jood[col_hotel_conf].apply(lambda x: x.replace('.0', '') if x.endswith('.0') else x)

            # --- دالة الفلترة (استبعاد sent) ---
            def is_valid_conf(val):
                if val == '' or val.lower() == 'nan':
                    return False
                if 'sent' in val.lower():
                    return False
                return True

            # --- تجميع بيانات جود ---
            jood_agg = df_jood.groupby(col_client_ref)[col_hotel_conf].apply(
                lambda x: set([i for i in x if is_valid_conf(i)])
            ).reset_index()
            jood_agg.rename(columns={col_hotel_conf: 'Jood_Confs_Set'}, inplace=True)

            # --- دمج الملفين ---
            merged_df = pd.merge(df_almatar, jood_agg, left_on=col_booking_code, right_on=col_client_ref, how='left')

            # --- استخراج النواقص ---
            missing_data = []

            for index, row in merged_df.iterrows():
                booking_code = row[col_booking_code]
                almatar_val_raw = row[col_ext_ref]
                
                # القيم الحالية في الشركة
                almatar_vals_set = set([x for x in re.split(r'[-,\s]+', almatar_val_raw) if x])
                
                # القيم الموجودة في جود
                jood_vals_set = row['Jood_Confs_Set']
                
                if isinstance(jood_vals_set, set):
                    # الفرق: موجود في جود وغير موجود في الشركة
                    missing_in_almatar = jood_vals_set - almatar_vals_set
                    
                    if len(missing_in_almatar) > 0:
                        for m in missing_in_almatar:
                            # إضافة العمودين المطلوبين فقط
                            missing_data.append({
                                f'Booking Code ({company_name})': booking_code,
                                'HotelConf(jood)': m
                            })

            # --- عرض النتائج وتحميل الملف ---
            if missing_data:
                result_df = pd.DataFrame(missing_data)
                
                st.success(f"تم العثور على {len(result_df)} حجز يحتاج لتحديث!")
                
                st.dataframe(result_df)

                csv = result_df.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="📥 تحميل ملف النتائج (CSV)",
                    data=csv,
                    file_name=f'{company_name.lower()}_missing_hotel_confs.csv',
                    mime='text/csv',
                )
            else:
                st.balloons()
                st.info("ممتاز! لا توجد أرقام ناقصة.")

        except Exception as e:
            st.error(f"حدث خطأ: {e}")

else:
    st.info("يرجى رفع الملفات للبدء.")