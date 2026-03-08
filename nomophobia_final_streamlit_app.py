# Nomophobia (NMP-Q) Streamlit App
# Arabic + English + CSV/TXT Download

from datetime import datetime
from io import StringIO
import csv
import streamlit as st


QUESTIONS_EN = [
    "1. I would feel uncomfortable without constant access to information through my smartphone.",
    "2. I would be annoyed if I could not look information up when I wanted to.",
    "3. Being unable to get the news would make me nervous.",
    "4. I would be annoyed if I could not use my smartphone when I wanted to.",
    "5. Running out of battery would scare me.",
    "6. If I ran out of data, I would panic.",
    "7. If I had no signal, I would constantly check for one.",
    "8. If I could not use my smartphone, I would fear getting stranded.",
    "9. If I could not check my smartphone, I would feel a desire to check it.",
    "10. If I did not have my smartphone with me, I would feel anxious.",
    "11. I would worry others couldn’t reach me.",
    "12. I would feel nervous not receiving messages.",
    "13. I would feel anxious not staying in touch.",
    "14. I would feel nervous not knowing if someone tried contacting me.",
    "15. I would feel anxious if my connection was broken.",
    "16. I would feel nervous being disconnected from my online identity.",
    "17. I would feel uncomfortable not accessing social media.",
    "18. I would feel awkward not checking notifications.",
    "19. I would feel anxious not checking email.",
    "20. I would feel weird not knowing what to do without my phone."
]

QUESTIONS_AR = [
    "1. سأشعر بعدم الارتياح إذا لم يكن لدي وصول مستمر للمعلومات عبر هاتفي.",
    "2. سأشعر بالانزعاج إذا لم أستطع البحث عن المعلومات عند الحاجة.",
    "3. عدم القدرة على متابعة الأخبار سيجعلني متوتراً.",
    "4. سأشعر بالانزعاج إذا لم أستطع استخدام هاتفي عند الرغبة.",
    "5. نفاد البطارية سيُخيفني.",
    "6. إذا نفدت البيانات فسأشعر بالهلع.",
    "7. إذا لم توجد إشارة فسأتحقق باستمرار منها.",
    "8. إذا لم أستطع استخدام هاتفي سأخاف من أن أعلق.",
    "9. إذا لم أستطع تفقد هاتفي سأشعر برغبة قوية في ذلك.",
    "10. إذا لم يكن هاتفي معي سأشعر بالقلق.",
    "11. سأقلق إذا لم يتمكن الآخرون من الوصول إلي.",
    "12. سأتوتر لعدم تلقي الرسائل.",
    "13. سأقلق لعدم بقائي على تواصل.",
    "14. سأتوتر لعدم معرفتي بمحاولات الاتصال.",
    "15. سأقلق لانقطاع اتصالي الدائم.",
    "16. سأتوتر لانفصالي عن هويتي الرقمية.",
    "17. سأشعر بعدم الارتياح لعدم متابعة الشبكات الاجتماعية.",
    "18. سأشعر بالحرج لعدم تفقد الإشعارات.",
    "19. سأقلق لعدم تفقد البريد الإلكتروني.",
    "20. سأشعر بغرابة لعدم معرفتي ماذا أفعل."
]

LIKERT = [1,2,3,4,5,6,7]


def classify(total):
    if total <= 20:
        return "Absent"
    if total < 60:
        return "Mild"
    if total < 100:
        return "Moderate"
    return "Severe"


def total_score(ans):
    return sum(ans.get(i,0) for i in range(1,21))


def make_csv(answers):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Item","Response"])
    for i in range(1,21):
        writer.writerow([i,answers.get(i)])
    writer.writerow([])
    writer.writerow(["Total",total_score(answers)])
    writer.writerow(["Severity",classify(total_score(answers))])
    return output.getvalue().encode()


def make_txt(answers):
    total = total_score(answers)
    return f"Total: {total}/140\nSeverity: {classify(total)}".encode()


def main():
    st.set_page_config(layout="centered")

    if "page" not in st.session_state:
        st.session_state.page = 1
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "lang" not in st.session_state:
        st.session_state.lang = "English"

    st.session_state.lang = st.selectbox("Language / اللغة",["English","العربية"])
    lang = st.session_state.lang
    questions = QUESTIONS_AR if lang=="العربية" else QUESTIONS_EN

    st.title("Nomophobia Screening Tool (NMP-Q)" if lang=="English" else "أداة فحص رهاب فقدان الهاتف")

    page = st.session_state.page
    start = (page-1)*5+1
    end = min(page*5,20)

    for i in range(start,end+1):
        if i not in st.session_state.answers:
            st.session_state.answers[i] = 4
        st.write(questions[i-1])
        st.session_state.answers[i] = st.radio("",LIKERT,index=LIKERT.index(st.session_state.answers[i]),key=f"q{i}")

    col1,col2,col3 = st.columns(3)

    if col1.button("Back" if lang=="English" else "رجوع"):
        if page>1:
            st.session_state.page-=1
            st.rerun()

    if col2.button("Next" if lang=="English" else "التالي"):
        if page<4:
            st.session_state.page+=1
            st.rerun()

    if col3.button("Submit" if lang=="English" else "إرسال"):
        st.session_state.page=5
        st.rerun()

    if page==5:
        total = total_score(st.session_state.answers)
        st.subheader("Results" if lang=="English" else "النتائج")
        st.write("Total:",total,"/140")
        st.write("Severity:",classify(total))

        st.download_button("Download CSV",make_csv(st.session_state.answers),"results.csv")
        st.download_button("Download TXT",make_txt(st.session_state.answers),"results.txt")


if __name__ == "__main__":
    main()
