import PIL.Image
from packaging import version

# Pillow library ke version 10+ mein ANTIALIAS ko Resampling.LANCZOS se badal diya gaya hai.
# Yeh code purana attribute wapas laata hai taaki flask-admin crash na ho.
if version.parse(PIL.__version__) >= version.parse("10.0.0"):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS