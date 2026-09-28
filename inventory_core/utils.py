import arabic_reshaper
from bidi.algorithm import get_display
def farsi(text):
    # ۱. اتصال حروف (Reshaping)
    reshaped_text = arabic_reshaper.reshape(text)
    # ۲. مرتب‌سازی جهت متن برای نمایش در ترمینال LTR (Bidi)
    bidi_text = get_display(reshaped_text)
    return bidi_text

def get_input_with_cancel(prompt):
    user_input = input(f"{prompt} (برای بازگشت 'back' را وارد کن): ")
    if user_input.lower() in ['back', 'b', 'بازگشت']:
        return None  # سیگنال بازگشت
    return user_input
