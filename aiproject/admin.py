from django.contrib import admin

# Register your models here.
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'created_at')  # 後台列表顯示欄位
    search_fields = ('name', 'email', 'message')               # 可搜尋欄位
    list_filter = ('created_at',)                              # 篩選條件


from django.contrib import admin
from .models import SheetCell  # 儲存格模型

@admin.register(SheetCell)
class SheetCellAdmin(admin.ModelAdmin):
    list_display  = ('sheet', 'row', 'col', 'value_short')
    list_filter   = ('sheet',)
    search_fields = ('sheet', 'value')
    ordering      = ('sheet', 'row', 'col')
    list_per_page = 100

    def value_short(self, obj):
        s = (obj.value or '')
        return s if len(s) <= 80 else s[:80] + '…'
    value_short.short_description = 'value'

from django.contrib import admin
from .models import Tool

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    # 後台列表顯示欄位
    list_display = ("name","price","price_range","support_chinese","yearly_discount","user_personal","user_team","technology","education", "logo_file", "logo_url" )

    # 可篩選的布林欄位
    list_filter = (
        "support_chinese","yearly_discount","user_personal","user_team",
        "delete_logo","for_personal","for_business","manufacture",
        "retail","government","law","realestate",
        "education","healthcare","technology","marketing",
        "media","design","finance",)

    # 可搜尋的欄位
    search_fields = ("name", "price", "price_range", "user_limit")

    # 編輯頁的欄位分區
    fieldsets = (
        ("基本資料", {"fields": ("name", "price", "price_range")}),
        ("主要功能類別", {
            "fields": ("text", "find_answer", "search", "code", "support_text", "image", "motion_image", "vedio" ),
         }),
        ("文件與生成功能", {
            "fields": (
                "upload_data",
                "upload_data_note",
                "make_data",
                "make_data_note",
                "make_image",
                "make_image_note",
            ),
            "classes": ("collapse",),
        }),
        ("使用屬性", {
            "fields": (
                "vedio_make",
                "motion_image_make",
                "user_personal",
                "user_team",
                "support_chinese",
                "yearly_discount",
                "delete_logo",
                "for_personal",
                "for_business",
                "user_limit",
            )
        }),
        ("產業別", {
            "fields": (
                "manufacture",
                "retail",
                "government",
                "law",
                "realestate",
                "education",
                "healthcare",
                "technology",
                "marketing",
                "media",
                "design",
                "finance",
            ),
        }),
    )

    # 每頁顯示筆數
    list_per_page = 25
