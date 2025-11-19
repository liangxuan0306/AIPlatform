# Create your views here.
from django.shortcuts import render, redirect
from .forms import RecommendForm, ContactForm
from django.contrib import messages
from .models import Tool  # AI 工具資料 (已經匯入 Excel)
from .forms import ContactForm
from django.db.models import Q
import re
from .utils import fetch_range
from django.db.models import Q, Case, When, IntegerField, Value
from django.core.exceptions import FieldDoesNotExist



def home(request):
    return render(request, 'aiproject/home.html')

def intro(request):
    return render(request, 'aiproject/intro.html')

def recommend(request):
    return render(request, 'aiproject/recommend.html')

def contact(request):
    return render(request, 'aiproject/contact.html')

from django.shortcuts import render, redirect
from .forms import ContactForm

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact')  # 送出後跳轉
    else:
        form = ContactForm()

    return render(request, 'aiproject/contact.html', {'form': form})

def tools_view(request):
    sheet = '收費方案'

    # 10 張卡的設定：range 必填，其餘可省略（有值就會套用）
    CARD_META = [
        {'range':'A2:E13','caption':'Claude','thumb':'aiproject/images/Claudelogo.png'},
        {'range':'A15:F23','caption':'Writesonic','thumb':'aiproject/images/Writesoniclogo.png'},
        {'range':'A25:D35','caption':'Stable Diffusion','thumb':'aiproject/images/StableDiffusionlogo.png'},
        {'range':'A37:D42','caption':'ChatGPT','thumb':'aiproject/images/ChatGPTlogo.png' },
        {'range':'A44:D59','caption':'Gamma','thumb':'aiproject/images/Gammalogo.jpg'},
        {'range':'A62:E71','caption':'Leonardo AI','thumb':'aiproject/images/LeonardoAIlogo.jpg'},
        {'range':'A74:D81','caption':'Gemini','thumb':'aiproject/images/Geminilogo.png'},
        {'range':'A84:D90','caption':'Perplexity','thumb':'aiproject/images/Perplexitylogo.png'},
        {'range':'A93:C98','caption':'Felo','thumb':'aiproject/images/Felologo.png'},
        {'range':'A101:C107','caption':'Sora','thumb':'aiproject/images/Soralogo.jpg'},
    ]

    def nonempty(s):
        s = '' if s is None else str(s).strip()
        return s not in ('', '-', '－')

    def matrix_to_plans(matrix):
        """把一個範圍轉成多欄方案：
        - 去除『整列都空白』的列
        - 去除『整欄都空白』的方案欄
        - 每欄 items = [{label, val}, ...]（不輸出欄標題）
        """
        if not matrix or len(matrix) < 2 or len(matrix[0]) < 2:
            return []

        col_count = len(matrix[0]) - 1         # 去掉 A 欄
        rows = matrix[1:]                       # 第 2 列起
        row_labels = [(r[0] or '').strip() for r in rows]

        vals_by_row = []
        for r in rows:
            vals_by_row.append([(r[j+1] if (j+1) < len(r) else '') for j in range(col_count)])

        # 1) 留下有任一值的列
        keep_row = [i for i, vals in enumerate(vals_by_row) if any(nonempty(v) for v in vals)]
        row_labels = [row_labels[i] for i in keep_row]
        vals_by_row = [vals_by_row[i] for i in keep_row]
        if not vals_by_row:
            return []

        # 2) 留下有任一值的欄
        keep_col = []
        for j in range(col_count):
            if any(nonempty(vals_by_row[i][j]) for i in range(len(vals_by_row))):
                keep_col.append(j)
        if not keep_col:
            return []

        # 3) 組欄
        plans = []
        for j in keep_col:
            items = []
            for i, label in enumerate(row_labels):
                v = vals_by_row[i][j]
                if nonempty(v):
                    items.append({'label': label, 'val': v})
            plans.append({'items': items})
        return plans

    url_re = re.compile(r'https?://[^\s]+', re.I)
    def link_from_top_b(matrix):
        """直接抓區塊第一列 B 欄（matrix[0][1]）的第一個網址"""
        if not matrix or len(matrix[0]) < 2:
            return None
        cell = matrix[0][1]
        if not cell:
            return None
        m = url_re.search(str(cell))
        return m.group(0) if m else None

    cards = []
    for meta in CARD_META:
        rg = meta['range']
        matrix = fetch_range(sheet, rg) or []
        plans = matrix_to_plans(matrix)
        if not plans:
            continue
        cards.append({
            'range': rg,
            'plans': plans,
            'caption': meta.get('caption'),
            'thumb': meta.get('thumb'),
            'width': meta.get('width', '150px'),     # 左欄寬度（可 per-card）
            'ratio': meta.get('ratio', '1 / 1'),     # 圖片長寬比（可 per-card）
            'source_url': link_from_top_b(matrix),   # ★ 連結來自每個區塊的 B(首列)
        })

    return render(request, 'aiproject/tools.html', {
        'sheet': sheet,
        'cards': cards,
    })
from django.shortcuts import render, redirect
from django.db.models import Q, Sum, Case, When, IntegerField
from .models import Tool
# views.py
from django.shortcuts import render, redirect
from django.db.models import Q, Sum, Case, When, IntegerField
from .models import Tool

# -------- 小工具：處理表單取值 --------
def _as_list(v):
    """確保回傳 list（應對 checkbox 或單值）"""
    if v is None:
        return []
    return v if isinstance(v, list) else [v]

def _first(v):
    """取 radio 的單一值"""
    if isinstance(v, list):
        return v[0] if v else None
    return v

# ============ 首頁：三題單選 + 4 項複選（希望功能） ============
def recommend(request):
    if request.method == "POST":
        f = request.POST

        # 重設後續步驟的暫存，避免舊資料殘留
        request.session.pop("step1_data", None)
        request.session.pop("step2_data", None)

        step0 = {
            "industry":    f.get("industry"),            # radio
            "main_need":   f.get("main_need"),           # radio
            "price_range": f.get("price_range"),         # radio
            # 只收這四個複選（值請對應 Tool 欄位名）
            # user_personal / user_team / yearly_discount / support_chinese
            "advanced_base": f.getlist("advanced_need"),
        }
        request.session["step0_data"] = step0

        # 若主功能為「圖像 / 影像生成」→ step2；否則 step1
        if step0.get("main_need") == "image_or_vedio":
            return redirect("recommend2")
        return redirect("recommend1")

    return render(request, "aiproject/recommend.html")


# ============ step1：一般進一步（複選） ============
def recommend1(request):
    if request.method == "POST":
        step1 = {
            # 例：upload_data / make_data / make_image / for_personal / for_business
            "advanced_step1": request.POST.getlist("advanced_step1"),
        }
        request.session["step1_data"] = step1
        return redirect("recommend_result")

    return render(request, "aiproject/recommend1.html")


# ============ step2：圖像/影像專屬進一步（複選） ============
def recommend2(request):
    if request.method == "POST":
        step2 = {
            # 例：motion_image_make / vedio_make / delete_logo / for_personal / for_business
            "advanced_step2": request.POST.getlist("advanced_step2"),
        }
        request.session["step2_data"] = step2
        return redirect("recommend_result")

    return render(request, "aiproject/recommend2.html")



def recommend_result(request):
    s0 = request.session.get("step0_data", {})
    s1 = request.session.get("step1_data", {})
    s2 = request.session.get("step2_data", {})

    industry    = s0.get("industry")
    main_need   = s0.get("main_need")
    price_range = s0.get("price_range")

    base_flags  = s0.get("advanced_base", [])            # user_personal / user_team / yearly_discount / support_chinese
    step1_flags = s1.get("advanced_step1", [])           # upload_data / make_data / make_image / for_personal / for_business
    step2_flags = s2.get("advanced_step2", [])           # motion_image_make / vedio_make / delete_logo / for_personal / for_business

    qs = Tool.objects.all()

    # --- 價格：依欄位型別決定轉型 ---
    try:
        pr_field = Tool._meta.get_field("price_range")
        if price_range not in [None, ""]:
            if pr_field.get_internal_type() in ("IntegerField", "SmallIntegerField", "PositiveIntegerField"):
                qs = qs.filter(price_range=int(price_range))
            else:
                qs = qs.filter(price_range=str(price_range))
    except FieldDoesNotExist:
        pass

    # --- 產業（布林欄位）：必須為 True ---
    if industry:
        # 避免使用者傳不存在的欄位名
        if any(f.name == industry for f in Tool._meta.get_fields()):
            qs = qs.filter(**{industry: True})

    # --- 主功能：必須 ---
    if main_need:
        if main_need == "image_or_vedio":
            qs = qs.filter(Q(image=True) | Q(vedio=True))
        elif any(f.name == main_need for f in Tool._meta.get_fields()):
            qs = qs.filter(**{main_need: True})

    # --- 其它條件改「加分」：符合就 +1，最後依分數排序 ---
    score_expr = None  # 先不建立，後面有條件才建立
    def add_flag(expr, field_name):
        if any(f.name == field_name for f in Tool._meta.get_fields()):
            piece = Case(When(**{field_name: True}, then=1),
                         default=0,
                         output_field=IntegerField())
            return (expr + piece) if expr is not None else (Value(0, output_field=IntegerField()) + piece)
        return expr

    for f in list(base_flags) + list(step1_flags) + list(step2_flags):
        score_expr = add_flag(score_expr, f)

    if score_expr is not None:
        qs = qs.annotate(score=score_expr).order_by("-score", "name")
    else:
        qs = qs.order_by("name")

    chosen = {
        "industry": industry,
        "main_need": main_need,
        "price_range": price_range,
        "advanced_base": base_flags,
        "advanced_step1": step1_flags,
        "advanced_step2": step2_flags,
    }


        # ==== 中文顯示用對照 ====
    industry_map = {
        "manufacture": "製造與工業", "retail": "零售與電商", "government": "政府/公共/非營利",
        "law": "法律與合規", "realestate": "不動產與建築", "education": "教育",
        "healthcare": "醫療與生技", "technology": "科技與資訊", "marketing": "行銷/廣告/公關",
        "media": "媒體與內容", "design": "設計與創意", "finance": "金融與保險",
    }
    main_need_map = {
        "find_answer": "即問即答",
        "search": "搜尋引擎",
        "text": "文本生成",
        "support_text": "文書輔助",
        "code": "程式碼輔助",
        "image_or_vedio": "圖像 / 影像生成",
    }
    price_range_map = {
        "0": "免費", "1": "1–600 元", "2": "601–1000 元", "3": "1001–5000 元",
        "4": "5001 元以上", "6": "聯繫業務決定", "7": "依使用量計費",
    }

    adv_base_map  = {
        "user_personal": "個人方案", "user_team": "團隊方案",
        "yearly_discount": "年繳優惠", "support_chinese": "支援中文",
    }
    adv_step1_map = {
        "upload_data": "可上傳文件", "make_data": "文件/報告生成",
        "make_image": "由文件生成圖片", "for_personal": "內容可私有化", "for_business": "可商業/營利公開",
    }
    adv_step2_map = {
        "motion_image_make": "可生成動態圖像", "vedio_make": "可影片生成",
        "delete_logo": "可去浮水印", "for_personal": "內容可私有化", "for_business": "可商業/營利公開",
    }

    def mget(d, k, default="—"):
        if k in (None, "", []):
            return default
        return d.get(str(k), d.get(k, default))

    chosen_human = {
        "industry": mget(industry_map, industry),
        "main_need": mget(main_need_map, main_need),
        "price_range": mget(price_range_map, price_range),
        "advanced_base": [adv_base_map.get(x, x) for x in base_flags] if base_flags else [],
        "advanced_step1": [adv_step1_map.get(x, x) for x in step1_flags] if step1_flags else [],
        "advanced_step2": [adv_step2_map.get(x, x) for x in step2_flags] if step2_flags else [],
}
    return render(request, "aiproject/recommend_result.html", {
        "tools": qs,
        "chosen": chosen,
        "chosen_human": chosen_human # 中文顯示用
    })
