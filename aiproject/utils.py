# aiproject/utils.py
import re
from .models import SheetCell  # 相對匯入。一定放在 aiproject 內

def col_to_index(s: str) -> int:
    n = 0
    for ch in s:
        n = n * 26 + (ord(ch.upper()) - 64)
    return n

def fetch_range(sheet: str, a1_range: str):
    """
    回傳 2D 陣列。例如 'A1:E12'
    """
    m = re.fullmatch(r'([A-Za-z]+)(\d+):([A-Za-z]+)(\d+)', a1_range)
    if not m:
        raise ValueError("range 格式需像 A1:E12")
    c1, r1, c2, r2 = m.groups()
    left, right = sorted([col_to_index(c1), col_to_index(c2)])
    top, bottom = sorted([int(r1), int(r2)])

    qs = SheetCell.objects.filter(
        sheet=sheet,
        row__gte=top, row__lte=bottom,
        col__gte=left, col__lte=right
    ).order_by('row', 'col')

    rows = bottom - top + 1
    cols = right - left + 1
    grid = [['' for _ in range(cols)] for __ in range(rows)]
    for cell in qs:
        grid[cell.row - top][cell.col - left] = cell.value or ''
    return grid
