"""5 test case — simple + multi-step — chạy cho cả v1 và v2."""

TEST_CASES = [
    {
        "id": "T01",
        "type": "simple",
        "input": "VF8 Plus giá bao nhiêu?",
        "expected_contains": ["1,259,000,000", "1259000000", "1.259.000.000"],
        "note": "Tra giá đơn thuần — gọi check_price",
    },
    {
        "id": "T02",
        "type": "simple",
        "input": "VF9 Plus tháng 4 giảm bao nhiêu?",
        "expected_contains": ["50,000,000", "50000000", "50 triệu"],
        "note": "Bug B2 ở v1: không biết KM → hallucinate hoặc bỏ qua",
    },
    {
        "id": "T03",
        "type": "multi_step",
        "input": "Mua VF8 Plus tháng 4 trả trước 30% vay 48 tháng, hàng tháng bao nhiêu?",
        "expected_contains": ["21,", "21204", "21.2", "21.204"],
        "note": "Full flow: check_price → áp KM → calculate_monthly_payment",
    },
    {
        "id": "T04",
        "type": "multi_turn",
        "turns": [
            "Toyota Camry bản hybrid giá bao nhiêu?",
            "Mua VF3 tháng này có KM không? Nếu có thì tính trả góp 24 tháng trả 25%.",
        ],
        "per_turn": [
            {
                "all": ["vinfast"],
                "any": [
                    "chỉ hỗ trợ",
                    "chỉ tư vấn",
                    "chỉ trả lời",
                    "chỉ hỏi",
                    "xe vinfast",
                ],
            },
            {
                "any": ["10,000,000", "10000000", "10 triệu", "10.000.000"],
            },
        ],
        "note": "L1: hãng khác → từ chối, nhắc chỉ VinFast; L2: VF3 KM + góp",
    },
    {
        "id": "T05",
        "type": "multi_turn",
        "turns": [
            "Vay 50 tháng mua Lux A2.0.",
            "Vậy tính giúp Lux A2.0 trả trước 20%, vay 48 tháng, mỗi tháng đóng bao nhiêu?",
        ],
        "expected_contains": [
            "16760846",
            "16.760.846",
            "16,760,846",
        ],
        "note": "Lượt 1: 50 tháng → lỗi / giải thích; lượt 2: 48 tháng + 20% → tiền góp ~16,76 triệu",
    },
]
