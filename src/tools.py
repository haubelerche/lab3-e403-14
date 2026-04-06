"""
vinfast_langgraph/src/tools.py — mock + tool dùng chung v1/v2.
"""
from langchain_core.tools import tool

CATALOG = {
    "VF3":      {"price": 322_000_000, "type": "electric", "colors": ["Trắng", "Hồng", "Xanh lá", "Vàng"]},
    "VF8 Plus": {"price": 1_259_000_000, "type": "electric", "colors": ["Trắng", "Đen", "Xám", "Đỏ"]},
    "VF9 Plus": {"price": 1_598_000_000, "type": "electric", "colors": ["Trắng", "Đen", "Xanh"]},
    "Lux A2.0": {"price": 850_000_000,  "type": "petrol",   "colors": ["Trắng", "Đen", "Bạc"]},
}

PROMOTIONS = {
    "VF3":      {"month": 4, "discount": 10_000_000},
    "VF8 Plus": {"month": 4, "discount": 30_000_000},
    "VF9 Plus": {"month": 4, "discount": 50_000_000},
    "Lux A2.0": {"month": 4, "discount": 0},
}

INTEREST_RATE = 0.085  # 8.5%/năm


@tool
def check_price(model: str) -> dict:
    """Tra cứu giá niêm yết và màu sắc xe VinFast. model: ví dụ 'VF8 Plus', 'VF3'."""
    info = CATALOG.get(model)
    if not info:
        return {"error": f"Không tìm thấy '{model}'. Có: {list(CATALOG.keys())}"}
    return {"model": model, **info}


@tool
def calculate_monthly_payment(price: float, down_pct: float, months: int) -> dict:
    """
    Tính tiền trả góp hàng tháng theo công thức anuity.
    price: giá xe sau KM (VNĐ), down_pct: % trả trước (20-50), months: kỳ hạn (12/24/36/48/60).
    """
    if down_pct < 20 or down_pct > 50:
        return {"error": "down_pct phải từ 20 đến 50 (%)"}
    if months not in (12, 24, 36, 48, 60):
        return {"error": f"months phải là 12/24/36/48/60, nhận được {months}"}

    down = price * down_pct / 100
    loan = price - down
    r = INTEREST_RATE / 12
    monthly = loan * r * (1 + r) ** months / ((1 + r) ** months - 1)
    return {
        "down_payment": int(down),
        "loan_amount":  int(loan),
        "monthly_payment": int(monthly),
        "months": months,
        "interest_rate": f"{INTEREST_RATE*100}%/năm",
    }
