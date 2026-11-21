import streamlit as st
from openai import OpenAI
import whois
from datetime import datetime
import base64
import json

st.set_page_config(page_title="درع الحقيقة الذكي", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    .main {direction: rtl; text-align: right;}
    h1, h2, h3, p, div {text-align: right;}
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ درع الحقيقة الذكي (Smart Truth Shield)")
st.subheader("نظام استباقي لكشف الاحتيال الإلكتروني وانتحال الهوية البصرية")

with st.sidebar:
    st.header("⚙️ الإعدادات")
    api_key = st.text_input("أدخل مفتاح OpenAI API Key:", type="password")
    st.info("يستخدم النظام نموذج GPT-4o-mini للرؤية الحاسوبية ومحرك WHOIS لفحص النطاقات.")

def check_domain_age(domain):
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date:
            age_days = (datetime.now() - creation_date).days
            return f"تاريخ الإنشاء: {creation_date.strftime('%Y-%m-%d')} (عمر النطاق: {age_days} يوم)"
        return "تعذر تحديد تاريخ إنشاء النطاق بدقة (قد يكون مخفياً)."
    except Exception:
        return "لم يتم العثور على سجل WHOIS واضح أو النطاق غير مسجل بشكل رسمي."

st.markdown("### 1️⃣ أدخل الرسالة أو ارفع لقطة شاشة للفحص:")
uploaded_file = st.file_uploader("ارفع لقطة شاشة (Screenshot) مشبوهة:", type=["png", "jpg", "jpeg"])
user_text = st.text_area("أو الصق نص الرسالة / الرابط المشبوه هنا:", height=120)

if st.button("🔍 ابدأ الفحص الفوري"):
    if not api_key:
        st.error("⚠️ يرجى إدخال OpenAI API Key في القائمة الجانبية أولاً.")
    elif not uploaded_file and not user_text.strip():
        st.warning("⚠️ يرجى رفع صورة أو كتابة نص/رابط للفحص.")
    else:
        with st.spinner("جاري التحليل البصري وفحص النطاقات والهندسة الاجتماعية..."):
            try:
                client = OpenAI(api_key=api_key)

                prompt = """
                أنت خبير أمن سيبراني في نظام 'درع الحقيقة الذكي'. حلل المحتوى المرفق (صورة أو نص) بدقة للكشف عن الاحتيال الإلكتروني (Phishing).
                استخرج:
                1. أي رابط إلكتروني (URL) موجود في النص أو مخفي داخل الصورة.
                2. النطاق الرئيسي فقط (Domain) مثل example.com بدون https أو مسارات (إذا وجد).
                3. هل يوجد انتحال لشعار أو اسم بنك أو جهة حكومية؟
                4. هل توجد أساليب هندسة اجتماعية (استعجال، تهديد، طلب رمز OTP أو بيانات بنكية)؟
                5. نسبة الخطورة من 0 إلى 100.
                6. ملخص واضح ومبسط للمستخدم العادي يشرح الأسباب والتوصية.

                أرجع النتيجة بصيغة JSON فقط بهذا الشكل:
                {
                    "extracted_url": "الرابط المستخرج أو لا يوجد",
                    "domain": "النطاق فقط أو none",
                    "impersonation": "تفاصيل انتحال الهوية",
                    "social_engineering": "تفاصيل الهندسة الاجتماعية",
                    "risk_score": 85,
                    "verdict": "خطير / مشبوه / آمن",
                    "explanation": "الشرح المبسط والتوصية للمستخدم"
                }
                """

                messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]

                if user_text.strip():
                    messages[0]["content"].append({"type": "text", "text": f"النص المرفق:\n{user_text}"})

                if uploaded_file:
                    image_bytes = uploaded_file.read()
                    base64_image = base64.b64encode(image_bytes).decode("utf-8")
                    messages[0]["content"].append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    })

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    response_format={"type": "json_object"},
                    max_tokens=600
                )

                result = json.loads(response.choices[0].message.content)

                domain = result.get("domain", "none")
                whois_info = "لا يوجد نطاق لفحصه."
                if domain and domain.lower() != "none" and "." in domain:
                    whois_info = check_domain_age(domain)

                st.divider()
                st.markdown("## 📊 تقرير الفحص الأمني")

                risk = result.get("risk_score", 0)
                if risk >= 70:
                    st.error(f"🚨 النتيجة: {result.get('verdict')} — نسبة الخطورة: {risk}%")
                elif risk >= 35:
                    st.warning(f"⚠️ النتيجة: {result.get('verdict')} — نسبة الخطورة: {risk}%")
                else:
                    st.success(f"✅ النتيجة: {result.get('verdict')} — نسبة الخطورة: {risk}%")

                st.markdown(f"**🔗 الرابط المستخرج:** `{result.get('extracted_url')}`")
                st.markdown(f"**🌐 فحص النطاق (WHOIS):** {whois_info}")
                st.markdown(f"**🎭 انتحال الهوية:** {result.get('impersonation')}")
                st.markdown(f"**🧠 الهندسة الاجتماعية:** {result.get('social_engineering')}")
                st.info(f"**💡 التوصية والشرح المبسط:**\n\n{result.get('explanation')}")

            except Exception as e:
                st.error(f"حدث خطأ أثناء الفحص: {e}")
