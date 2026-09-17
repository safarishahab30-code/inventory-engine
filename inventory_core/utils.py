import arabic_reshaper
from bidi.algorithm import get_display

def farsi(text: str) -> str:
    if not text:
        return ""
    # ۱. چسباندن فرم حروف
    reshaped_text = arabic_reshaper.reshape(str(text))
    # ۲. تنظیم جهت دیداری
    return get_display(reshaped_text)
