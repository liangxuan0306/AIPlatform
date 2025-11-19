from django.db import models

# Create your models here.
class ContactMessage(models.Model):
    name = models.CharField(max_length=100) # 使用者姓名
    email = models.EmailField() # 使用者 Email
    message = models.TextField() # 使用者訊息
    created_at = models.DateTimeField(auto_now_add=True) # 建立時間

    def __str__(self):
        return f"{self.name} - {self.email}"
    
from django.db import models

class SheetCell(models.Model):
    sheet = models.CharField(max_length=64)   # 工作表名稱
    row   = models.IntegerField()             # 列（1 開始）
    col   = models.IntegerField()             # 欄（1=A, 2=B, ...）
    addr  = models.CharField(max_length=16)   # A1, B2...
    value = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=['sheet','row']),
                   models.Index(fields=['sheet','col'])]
        unique_together = ('sheet', 'addr')

from django.db import models

class Tool(models.Model):
    name = models.CharField(max_length=100)
    price = models.CharField(max_length=100, null=True, blank=True)
    price_range = models.CharField(max_length=50, null=True, blank=True)

    logo_file = models.CharField(max_length=200, blank=True, default="")
    logo_url = models.URLField(blank=True, default="")

    # 功能相關(類別)
    text = models.BooleanField(default=False)
    find_answer = models.BooleanField(default=False)
    search = models.BooleanField(default=False)
    code = models.BooleanField(default=False)
    support_text = models.BooleanField(default=False)
    image = models.BooleanField(default=False)
    motion_image = models.BooleanField(default=False)
    vedio = models.BooleanField(default=False)

    # 篩選條件1
    user_personal = models.BooleanField(default=False)
    user_team = models.BooleanField(default=False)
    support_chinese = models.BooleanField(default=False)
    yearly_discount = models.BooleanField(default=False)

    # 主要功能為布林 + 附註欄位
    upload_data = models.BooleanField(default=False)
    upload_data_note = models.TextField(null=True, blank=True)

    make_data = models.BooleanField(default=False)
    make_data_note = models.TextField(null=True, blank=True)

    make_image = models.BooleanField(default=False)
    make_image_note = models.TextField(null=True, blank=True)

    # 篩選條件2
    vedio_make = models.BooleanField(default=False)
    motion_image_make = models.BooleanField(default=False)
    delete_logo = models.BooleanField(default=False)
    for_personal = models.BooleanField(default=False)
    for_business = models.BooleanField(default=False)

    # 使用次數限制(僅呈現)
    user_limit = models.TextField(null=True, blank=True)  # 使用次數或條件

    # 產業別（全部勾選）
    manufacture = models.BooleanField(default=False)
    retail = models.BooleanField(default=False)
    government = models.BooleanField(default=False)
    law = models.BooleanField(default=False)
    realestate = models.BooleanField(default=False)
    education = models.BooleanField(default=False)
    healthcare = models.BooleanField(default=False)
    technology = models.BooleanField(default=False)
    marketing = models.BooleanField(default=False)
    media = models.BooleanField(default=False)
    design = models.BooleanField(default=False)
    finance = models.BooleanField(default=False)

    def __str__(self):
        return self.name