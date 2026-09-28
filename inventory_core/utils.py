import arabic_reshaper
from bidi.algorithm import get_display

def farsi(text: str) -> str:
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)
def get_input_with_cancel(prompt):
    user_input = input(f"{prompt} (برای بازگشت 'back' را وارد کن): ")
    if user_input.lower() in ['back', 'b', 'بازگشت']:
        return None  # سیگنال بازگشت
    return user_input
