from django.core.management.base import BaseCommand
import pandas as pd
from pathlib import Path
from aiproject.models import SheetCell

def index_to_col(n:int)->str:
    s=''
    while n>0:
        n, r = divmod(n-1, 26)
        s = chr(65+r)+s
    return s

class Command(BaseCommand):
    help = "Load all sheets of an Excel into SheetCell table"

    def add_arguments(self, parser):
        parser.add_argument('xlsx_path', type=str)

    def handle(self, *args, **opts):
        path = Path(opts['xlsx_path'])
        xls  = pd.ExcelFile(path)
        SheetCell.objects.all().delete()  # 重新匯入會先清空
        for sheet in xls.sheet_names:
            df = pd.read_excel(path, sheet_name=sheet, header=None)  # 不用表頭
            for r in range(df.shape[0]):
                for c in range(df.shape[1]):
                    v = df.iat[r, c]
                    row = r+1
                    col = c+1
                    addr = f'{index_to_col(col)}{row}'
                    SheetCell.objects.create(
                        sheet=sheet, row=row, col=col, addr=addr,
                        value=None if pd.isna(v) else str(v)
                    )
        self.stdout.write(self.style.SUCCESS("Excel loaded."))
