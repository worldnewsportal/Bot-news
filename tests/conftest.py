import sys
from pathlib import Path

# إضافة المجلد الرئيسي للمشروع لـ sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
