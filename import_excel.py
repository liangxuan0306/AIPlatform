# aiproject/import_excel.py
import os
import re
import django
import pandas as pd

# ---------------- Django 啟動 ----------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nkust_project.settings")
django.setup()

from aiproject.models import Tool

# ---------------- 路徑設定 ----------------
# 這支腳本位在 aiproject/ 底下
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(APP_DIR)

# Excel 檔（放在 aiproject/imports/ 底下）
EXCEL_PATH = os.path.join(APP_DIR, "imports", "pricedjango.xlsx")
EXCEL_SHEET = "django資料庫"

# 靜態圖片資料夾（你已有的 images）
IMAGES_DIR = os.path.join(APP_DIR, "static", "aiproject", "images")

# 匯入前是否清空舊資料
CLEAR_ALL = True


# ---------------- 小工具 ----------------
def to_bool(v):
    """將 Excel 值轉成乾淨布林。"""
    if pd.isna(v):
        return False
    s = str(v).strip().lower()
    return s in {"1", "true", "yes", "y", "是", "有", "支援", "可", "允許"}


def clean_str(v, default=""):
    """把 NaN / None 轉成字串，保留 '0'。"""
    if pd.isna(v):
        return default
    return str(v).strip()


def slugify_name(name: str) -> str:
    """
    把工具名稱簡化成檔名可用的 slug，用來在 images/ 底下比對。
    例：'StableDiffusion 專業版' -> 'stablediffusion'
    """
    s = re.sub(r"[^A-Za-z0-9]+", "", name)  # 去掉非英數
    return s.lower()


def find_logo_file(tool_name: str, hint_from_excel: str | None) -> str:
    """
    回傳相對於 static/ 的路徑 (例如 'aiproject/images/ChatGPTlogo.png')，
    找不到時回傳空字串。
    規則：
      1) 若 Excel 有給 `logo_file` 欄位，先直接找該檔名（容許不分大小寫）
      2) 否則用工具名稱 slug 嘗試在 images 內找常見副檔名
    """
    if not os.path.isdir(IMAGES_DIR):
        return ""

    # 先列出 images 底下所有檔名（小寫）
    filenames = {f.lower(): f for f in os.listdir(IMAGES_DIR) if os.path.isfile(os.path.join(IMAGES_DIR, f))}

    # 1) Excel 明確指定（例如 'ChatGPTlogo.png'）
    if hint_from_excel:
        key = hint_from_excel.strip().lower()
        if key in filenames:
            return f"aiproject/images/{filenames[key]}"

    # 2) 依名稱推測
    base = slugify_name(tool_name)
    exts = [".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"]
    for ext in exts:
        guess = base + ext
        if guess in filenames:
            return f"aiproject/images/{filenames[guess]}"

    # 3) 寬鬆包含（有些檔名可能含品牌字樣）
    for fname_lower, orig in filenames.items():
        if base and base in fname_lower:
            return f"aiproject/images/{orig}"

    return ""


# ---------------- 讀取 Excel ----------------
if not os.path.isfile(EXCEL_PATH):
    raise FileNotFoundError(f"找不到 Excel 檔：{EXCEL_PATH}")

df = pd.read_excel(EXCEL_PATH, sheet_name=EXCEL_SHEET)
print(f"讀取到 {len(df)} 筆資料")

# ---------------- 匯入資料 ----------------
if CLEAR_ALL:
    Tool.objects.all().delete()
    print("舊資料已清空，準備重新匯入...")

ok_cnt, miss_logo_cnt = 0, 0

for _, row in df.iterrows():
    # 基本欄位（保留 '0'）
    name = clean_str(row.get("name", ""))
    raw_price = clean_str(row.get("price", ""))
    raw_price_range = clean_str(row.get("price_range", ""))

    # 圖檔（可選）：
    #   - 若 Excel 有 'logo_file' 欄位，放檔名（例如 'ChatGPTlogo.png'）
    #   - 若 Excel 有 'logo_url' 欄位，放外部圖片 URL
    excel_logo_file = clean_str(row.get("logo_file", ""))
    excel_logo_url = excel_logo_file

    # 在你的 images/ 底下尋找對應圖檔
    resolved_logo_file = find_logo_file(name, excel_logo_file)
    if not resolved_logo_file and not excel_logo_url:
        miss_logo_cnt += 1  # 沒有本地圖，也沒有外部圖

    Tool.objects.create(
        # 文字／數值
        name=name,
        price=raw_price,
        price_range=raw_price_range,

        # 圖片
        logo_file=resolved_logo_file,   # 例如 'aiproject/images/ChatGPTlogo.png'
        logo_url=excel_logo_url,        # 外部 URL（有就會在前端優先顯示）

        # 主要功能
        text=to_bool(row.get("text", 0)),
        find_answer=to_bool(row.get("find_answer", 0)),
        search=to_bool(row.get("search", 0)),
        code=to_bool(row.get("code", 0)),
        support_text=to_bool(row.get("support_text", 0)),
        image=to_bool(row.get("image", 0)),
        motion_image=to_bool(row.get("motion_image", 0)),
        vedio=to_bool(row.get("vedio", 0)),

        # 使用類型 & 常見條件
        user_personal=to_bool(row.get("user_personal", 0)),
        user_team=to_bool(row.get("user_team", 0)),
        support_chinese=to_bool(row.get("support_chinese", 0)),
        yearly_discount=to_bool(row.get("yearly_discount", 0)),

        # 進階需求（一般）
        upload_data=to_bool(row.get("upload_data", 0)),
        upload_data_note=clean_str(row.get("upload_data_note", "")),
        make_data=to_bool(row.get("make_data", 0)),
        make_data_note=clean_str(row.get("make_data_note", "")),
        make_image=to_bool(row.get("make_image", 0)),
        make_image_note=clean_str(row.get("make_image_note", "")),

        # 進階需求（圖像/影像）
        vedio_make=to_bool(row.get("vedio_make", 0)),
        motion_image_make=to_bool(row.get("motion_image_make", 0)),
        delete_logo=to_bool(row.get("delete_logo", 0)),

        # 授權
        for_personal=to_bool(row.get("for_personal", 0)),
        for_business=to_bool(row.get("for_business", 0)),

        # 使用限制說明（字串）
        user_limit=clean_str(row.get("user_limit", "")),

        # 產業別（布林）
        manufacture=to_bool(row.get("manufacture", 0)),
        retail=to_bool(row.get("retail", 0)),
        government=to_bool(row.get("government", 0)),
        law=to_bool(row.get("law", 0)),
        realestate=to_bool(row.get("realestate", 0)),
        education=to_bool(row.get("education", 0)),
        healthcare=to_bool(row.get("healthcare", 0)),
        technology=to_bool(row.get("technology", 0)),
        marketing=to_bool(row.get("marketing", 0)),
        media=to_bool(row.get("media", 0)),
        design=to_bool(row.get("design", 0)),
        finance=to_bool(row.get("finance", 0)),
    )
    ok_cnt += 1

print(f"匯入完成！成功 {ok_cnt} 筆；其中 {miss_logo_cnt} 筆沒有圖（logo_file / logo_url 都空）。")
print("到 /admin 檢查工具清單，或直接前往前台查看結果頁。")
