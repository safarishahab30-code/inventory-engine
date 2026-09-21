import arabic_reshaper
from bidi.algorithm import get_display

def farsi(text: str) -> str:
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)
