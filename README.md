# Camera App (Flask + OpenCV)

## هدف پروژه (طبق خواسته‌ی استاد)
هدف این پروژه بازتولید اپلیکیشن معرفی‌شده در مقاله‌ی زیر است، با این تفاوت که کد و ساختار پروژه باید طوری نوشته شود که در آینده بتوانید خیلی راحت فیچرهای جدید به آن اضافه کنید:

- مقاله: `https://towardsdatascience.com/camera-app-with-flask-and-opencv-bd147f6c0eec/`
- خروجی نهایی: یک وب‌اپ Flask که استریم زنده‌ی وب‌کم را در مرورگر نشان می‌دهد و با دکمه‌ها می‌توان **عکس گرفت**، **ویدیو ضبط کرد** و **فیلترهای ساده** را روشن/خاموش کرد.

### قابلیت‌های اصلی (Minimum Viable Feature Set)
این‌ها همان قابلیت‌هایی هستند که در مقاله/ریفـرنس وجود دارد و استاد از شما انتظار دارد بازتولیدشان کنید:

- Live stream وب‌کم داخل صفحه‌ی وب (MJPEG stream)
- `Stop/Start` برای قطع/وصل استریم
- `Capture` برای ذخیره‌ی یک عکس در پوشه‌ی `shots/`
- `Start/Stop Recording` برای ضبط و ذخیره‌ی ویدیو (`vid_*.avi`)
- فیلترها (Toggle):
  - `Grey` (خاکستری)
  - `Negative` (نگاتیو)
  - `Face Only` (کراپ صورت با مدل تشخیص چهره‌ی OpenCV DNN)

## استاد دقیقاً چی می‌خواهد؟
متن استاد عملاً یعنی:

1. **همان اپ** را بسازید (از نظر فیچر و تجربه‌ی کاربری).
2. **از روز اول ساختار پروژه را تمیز بچینید** (Framework for extensions) تا بعداً اضافه کردن مواردی مثل فیلترهای AI، ذخیره‌سازی، UI بهتر، چند دوربین، API و… ساده باشد.
3. روند کار را مطابق این برنامه جلو ببرید (یا مشابه آن)، یعنی روزبه‌روز خروجی قابل تست داشته باشید:
   - Day 1: تعریف Canvas/Scope و لیست قابلیت‌ها
   - Day 2: ساخت HTML استاتیک (UI اولیه)
   - Day 3: پیاده‌سازی Flask back end
   - Day 4–5: اتصال OpenCV و پردازش تصویر
   - Day 6–9: تست، بهبود، تمیزکاری و آماده‌سازی ارائه/تحویل

## فایل‌های اضافی که استاد داده (۴ فایل بدون پسوند)
این ۴ فایل که در روت پروژه کپی کرده‌اید **PNG (آیکن UI)** هستند و برای کارکرد اصلی برنامه ضروری نیستند، ولی به درد **زیباتر کردن فرانت‌اند** می‌خورند:

- `0719115d-a5c8-4a6c-adb6-3cc7097ba1d6` (PNG، اندازه 40×40)
- `1c31d9d9-c49f-491c-ae3e-2778c921ce8b` (PNG، اندازه 96×96) — آیکن دوربین
- `d7c44ae8-81cf-497a-9bd6-2903d8286b60` (PNG، اندازه 96×96) — آیکن فایل/سند
- `d25b7bf2-4dcd-41eb-8a70-a4ceb4319479` (PNG، اندازه 260×60) — آیکن Share/Arrow

پیشنهاد: برای استفاده در HTML بهتر است آن‌ها را به فایل‌های معنادار با پسوند `.png` تبدیل کنید و داخل `static/` بگذارید (مثلاً `static/icons/camera.png`).

## نکته
این پروژه بر اساس ایده‌ی مقاله ساخته شده، ولی کد با ساختار ماژولار نوشته شده تا توسعه‌ی آینده راحت باشد.

## معماری پروژه (framework برای توسعه‌ی آینده)
این ریپو همین ساختار ماژولار را پیاده‌سازی می‌کند (قابل توسعه و نزدیک به برنامه‌ی استاد):

```
CameraApp/
  app/
    __init__.py        # create_app + config
    routes.py          # Flask routes (/, /video_feed, /actions)
    camera.py          # مدیریت VideoCapture + تولید فریم
    processing.py      # فیلترها و پردازش تصویر
    state.py           # وضعیت سوییچ‌ها (بدون globalهای پراکنده)
    recording.py       # ضبط ویدیو (VideoWriter + thread)
  templates/
    index.html
  static/
    css/
    icons/
  models/              # مدل تشخیص چهره (OpenCV DNN)
    deploy.prototxt.txt
    res10_300x300_ssd_iter_140000.caffemodel
  pyproject.toml       # dependencies برای uv
  requirements.txt     # (اختیاری) fallback برای pip
  run.py               # entrypoint اجرای اپ
  README.md
```

چرا این ساختار بهتر است؟

- UI از منطق پردازش جدا می‌شود.
- state و toggleها قابل تست/تغییر می‌شوند.
- اضافه کردن فیلتر جدید فقط یک تابع جدید در `processing.py` است.
- تغییر منبع دوربین (USB/IP/Video file) فقط در `camera.py` انجام می‌شود.

## اجرا با uv (پیشنهادی)
### 1) نصب uv (یکبار)
اگر `uv` روی سیستم شما نصب نیست:

```powershell
pip install uv
```

### 2) نصب وابستگی‌ها
از روت پروژه:

```powershell
uv venv
uv sync
```

### 3) اجرای برنامه

```powershell
uv run python run.py
```

بعد در مرورگر: `http://127.0.0.1:5000/`

## اجرا با pip (fallback)
روی ویندوز:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

بعد در مرورگر: `http://127.0.0.1:5000/`

## برنامه‌ی پیشنهادی روز به روز (خروجی قابل ارائه)
برای اینکه دقیقاً مطابق خواسته‌ی استاد جلو بروید، هر روز یک خروجی “قابل تست” داشته باشید:

- Day 1 (Scope): لیست فیچرها + اسکچ UI + تصمیم معماری (routeها، state، pipeline پردازش)
- Day 2 (Front-end): `templates/index.html` + CSS + دکمه‌ها + جایگاه نمایش ویدیو
- Day 3 (Flask): routeهای `GET /`، `GET /video_feed`، `POST /actions` + رندر صفحه
- Day 4 (OpenCV پایه): استریم MJPEG + خاکستری/نگاتیو
- Day 5 (Featureها): capture عکس + record ویدیو + face-only
- Day 6–9 (Testing & polish):
  - هندل کردن خطاها (وب‌کم در دسترس نیست، قطع شدن دوربین، …)
  - پاک‌سازی state و threadها
  - بهبود UI/UX
  - اضافه کردن تست برای `processing.py` (ورودی/خروجی فیلترها)

## منابع
- مقاله: `https://towardsdatascience.com/camera-app-with-flask-and-opencv-bd147f6c0eec/`
- ریپو نویسنده: `https://github.com/hemanth-nag/Camera_Flask_App`
- توضیح تشخیص چهره با OpenCV DNN: `https://www.pyimagesearch.com/2018/02/26/face-detection-with-opencv-and-deep-learning/`

## Troubleshooting (Camera not detected / no permission prompt)
- این پروژه دوربین را سمت سرور با OpenCV می‌گیرد، پس مرورگر هیچ پیام اجازه‌ی دسترسی (permission prompt) نشان نمی‌دهد.
- خطاهایی مثل `Camera index out of range` یعنی OpenCV نتوانسته دوربین را باز کند. کارهای رایج:
  - برنامه‌های دیگری که از دوربین استفاده می‌کنند را ببند (Teams/Zoom/OBS/Camera).
  - ویندوز: `Settings > Privacy & security > Camera` و گزینه‌ی دسترسی برای Desktop apps را فعال کن.
  - پیدا کردن ایندکس درست دوربین: `uv run python scripts/list_cameras.py --max-index 5`
  - اجرای اجباری با ایندکس مشخص (PowerShell):
    - `$env:CAMERA_INDEX=0; uv run python run.py`
    - `$env:CAMERA_INDEX=1; uv run python run.py`
  - (اختیاری) تنظیم رزولوشن:
    - `$env:CAMERA_WIDTH=1280; $env:CAMERA_HEIGHT=720; uv run python run.py`
