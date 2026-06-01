import os
import re

DOCS_DIR = "docs"
MIN_SCORE_TO_ANSWER = 2  # اگر امتیاز کمتر از این بود، می‌گوییم چیزی پیدا نشد


def read_all_docs(docs_dir):
    """
    همه فایل‌های داخل docs_dir را می‌خواند و برمی‌گرداند:
    لیستی از دیکشنری‌ها: {file, text}
    """
    items = []
    if not os.path.exists(docs_dir):
        return items

    for name in os.listdir(docs_dir):
        path = os.path.join(docs_dir, name)
        if os.path.isfile(path):
            # txt/md هر دو قابل قبول‌اند
            if name.lower().endswith((".txt", ".md")):
                with open(path, "r", encoding="utf-8") as f:
                    items.append({"file": name, "text": f.read()})
    return items


def split_to_paragraphs(text):
    """
    متن را با خط خالی به پاراگراف‌ها تقسیم می‌کند.
    (هر پاراگراف یک بخش پاسخ بالقوه است)
    """
    # تبدیل \r\n به \n برای سازگاری
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    parts = re.split(r"\n\s*\n", text)  # جدا کردن با خط خالی
    paragraphs = [p.strip() for p in parts if p.strip()]
    return paragraphs


def normalize_and_tokenize(s):
    """
    ساده‌سازی متن و تبدیل به لیست کلمات.
    - حروف کوچک
    - حذف علائم
    - جداسازی با فاصله
    """
    s = s.lower()
    # هرچیزی غیر از حروف/عدد/فاصله را با فاصله جایگزین کن
    s = re.sub(r"[^\w\s\u0600-\u06FF]", " ", s)  # پشتیبانی بهتر از فارسی
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return []
    return s.split(" ")


def score_paragraph(question_tokens, paragraph_text):
    """
    امتیازدهی خیلی ساده: تعداد کلمات مشترک (یونیک) بین سوال و پاراگراف.
    """
    p_tokens = normalize_and_tokenize(paragraph_text)
    if not p_tokens:
        return 0

    q_set = set(question_tokens)
    p_set = set(p_tokens)
    common = q_set.intersection(p_set)
    return len(common)


def find_best_answer(question, docs_items):
    """
    بین همه پاراگراف‌های همه فایل‌ها می‌گردد و بهترین نتیجه را برمی‌گرداند.
    خروجی: (best_score, best_file, best_paragraph)
    """
    q_tokens = normalize_and_tokenize(question)
    if not q_tokens:
        return 0, None, None

    best_score = 0
    best_file = None
    best_para = None

    for item in docs_items:
        paragraphs = split_to_paragraphs(item["text"])
        for para in paragraphs:
            sc = score_paragraph(q_tokens, para)
            if sc > best_score:
                best_score = sc
                best_file = item["file"]
                best_para = para

    return best_score, best_file, best_para


def main():
    print("Mini Company Knowledge Bot (Simple)")
    print("Type your question. Type 'exit' to quit.")
    print("-" * 50)

    docs_items = read_all_docs(DOCS_DIR)
    if not docs_items:
        print(f"ERROR: No .txt/.md files found in '{DOCS_DIR}/'")
        print("Create docs/ and add some .txt or .md files, then run again.")
        return

    while True:
        q = input("\nYou: ").strip()
        if not q:
            continue
        if q.lower() in ("exit", "quit", "q"):
            print("Bye.")
            break

        score, src_file, answer = find_best_answer(q, docs_items)

        if score < MIN_SCORE_TO_ANSWER or not answer:
            print("\nBot: متأسفم، در اسناد موجود چیزی مرتبط پیدا نکردم.")
            print("Bot: می‌توانید درباره مرخصی، محصول، پشتیبانی یا قوانین داخلی سوال بپرسید.")
            continue

        print("\nBot:", answer)
        print(f"Source: {DOCS_DIR}/{src_file} (score={score})")


if __name__ == "__main__":
    main()
