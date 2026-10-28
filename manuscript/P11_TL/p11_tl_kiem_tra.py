# -*- coding: utf-8 -*-
"""Tự kiểm bản thảo Bài 11 (bản công nghệ hỗ trợ tâm lý trị liệu): mọi nhận định định tính trong bài được đối chiếu
lại với tệp kết quả, và bản .md đã dựng được kiểm tra về hình thức.

    .venv/Scripts/python.exe manuscript/P11_TL/p11_tl_kiem_tra.py [--lang vi|en]

Ghi p11_tl_kiem_tra.txt (bản Việt) hoặc manuscript/P11_TL_EN/p11_tl_en_kiem_tra.txt; dòng cuối "ĐẠT k/n".
"""
from __future__ import annotations

import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_p11_tl as b  # noqa: E402

EN = b.EN
TL, G, DEMO = b.TL, b.G, b.DEMO
MD = open(os.path.join(b.OUTDIR, f"{b.BASE}.md"), encoding="utf-8").read()
SRC = open(os.path.join(b.OUTDIR, f"{b.BASE}_src.md"), encoding="utf-8").read()
out, ok = [], 0


def chk(name, cond):
    global ok
    ok += bool(cond)
    out.append(("ĐẠT  " if cond else "LỖI  ") + name)


T1 = lambda k: TL["tl1"][k][0]
T2 = lambda k: TL["tl2"][k][0]
T3 = lambda k: TL["tl3"][k][0]
test = b.tl_test
RS = ("RUS", "ROS", "SMOTE", "CW")
DIST = ("ROS", "SMOTE", "CW")

# ---------------------------------------------------------------- thiết kế
chk("20 lần lặp ở p11_tl.json và p11_tasks.json; không phải bản chạy nhanh",
    TL["n_reps"] == 20 and G["n_reps"] == 20 and not TL["quick"] and not G["quick"])
chk("quần thể 50 000 trẻ, đúng 1 000 trẻ mắc (2 %)", TL["n_eval"] == 50000 and TL["n_eval_pos"] == 1000)
chk("tập huấn luyện 5 000 hồ sơ, 2 %", TL["n_train"] == 5000 and TL["prev"] == 0.02)
chk("kho hồ sơ trùng kho của lưới chính (kích thước)",
    TL["pool_sizes"]["dev_pos"] == G["dev_pool"]["pos"] and TL["pool_sizes"]["dev_neg"] == G["dev_pool"]["neg"]
    and TL["pool_sizes"]["test_pos"] == G["test_pool"]["pos"])
chk("mẫu kiểm tra rút từ phần còn lại, rời quần thể đánh giá",
    TL["audit_pool"]["pos"] + 1000 == G["test_pool"]["pos"] and TL["audit_pool"]["neg"] + 49000 == G["test_pool"]["neg"])
chk("108 phép kiểm trong họ BH của bài", TL["n_tests"] == 108 == len(TL["tests"]))
triv = [t for t in TL["tests"] if "|N0|pc|" in t["key"]]
chk("đúng 6 phép kiểm tầm thường (N0 + hiệu chỉnh tiên nghiệm), hiệu số 0",
    len(triv) == 6 and all(t["effect"] == 0 and t["p_raw"] == 1 for t in triv))
chk("'chuyển tất cả' ở p_t = 2 % có NB đúng bằng 0", abs(TL["ref_all"]["0.02"]) < 1e-12)
chk("SMOTE k = 5 và RF 200 cây / 5 hồ sơ mỗi lá trong run_imbalance",
    "k=5" in open(os.path.join(b.ROOT, "src", "run_imbalance.py"), encoding="utf-8").read()
    and "n_estimators=200, min_samples_leaf=5" in open(os.path.join(b.ROOT, "src", "run_p11_tl.py"), encoding="utf-8").read())

# ---------------------------------------------------------------- 3.1 lưới chính
bt = b.main_tests("brier")
chk("Brier xấu hơn có ý nghĩa ở 64/64 ô", len(bt) == 64 and all(t["effect"] > 0 and t["p_bh"] < 0.05 for t in bt))
pr = b.main_tests("pr_auc")
up = [t for t in pr if t["effect"] > 0 and t["p_bh"] < 0.05]
chk("PR-AUC tăng có ý nghĩa chỉ ở FKNN hoặc RF+RUS", len(up) > 0 and all(
    t["model"] == "FKNN" or (t["model"] == "RF" and t["method"] == "RUS") for t in up))
chk("'Fuzzy k-NN gần như không phân biệt được' (AUC < 0,56 ở mọi tỷ lệ)",
    all(b.gcell(p, "FKNN", "N0", "roc_auc") < 0.56 for p in G["prevs"]))
nbt = b.main_tests("nb")
upnb = [t for t in nbt if t["effect"] > 0 and t["p_bh"] < 0.05]
chk("NB tăng: chủ yếu FKNN hoặc tỷ lệ 5 % (mọi ô tăng thuộc một trong hai)",
    all(t["model"] == "FKNN" or t["prev"] == 0.05 for t in upnb))
chk("LR và HYB sau cân bằng lại gắn cờ ≥ 99,9 % trẻ ở cả bốn tỷ lệ",
    all(b.gcell(p, m, h, "flag_rate") >= 0.999 for p in G["prevs"] for m in ("LR", "HYB") for h in RS))
chk("dịch chuyển ngưỡng: PR-AUC và Brier trùng nguyên trạng",
    all(b.gcell(p, m, "TS", k) == b.gcell(p, m, "N0", k) for p in G["prevs"] for m in G["models"]
        for k in ("pr_auc", "brier")))
chk("mốc Brier 19,6 phần nghìn = 0,02·0,98", abs(0.02 * 0.98 - 0.0196) < 1e-12)
chk("LR và RF có AUC ≥ 0,68 (phân biệt thực) ở 2 %",
    b.gcell(0.02, "LR", "N0", "roc_auc") >= 0.68 and b.gcell(0.02, "RF", "N0", "roc_auc") >= 0.68)

# ---------------------------------------------------------------- 3.2 dải nguy cơ
infl = {(m, h): T3(f"{m}|{h}|raw|mean_p") / 0.02 for m in ("LR", "RF") for h in RS}
chk("LR thổi phồng > 20 lần với cả bốn cách ('hơn hai mươi lần' ở kết luận)", all(infl[("LR", h)] > 20 for h in RS))
chk("tóm tắt EN 'about twentyfold' (LR SMOTE 19–23 lần)", 19 <= infl[("LR", "SMOTE")] <= 23)
chk("tóm tắt EN '86%' khớp", round(100 * T1("LR|SMOTE|raw|>=20%|share")) == 86)
chk("tóm tắt EN 'true rate about 2%' (dải ≥ 20 % sau SMOTE: 15–30/1 000)",
    0.015 <= T1("LR|SMOTE|raw|>=20%|obs") <= 0.030)
chk("sau SMOTE không trẻ nào ở dải < 1 % và 1–5 % (≤ 0,05 %)",
    T1("LR|SMOTE|raw|<1%|share") <= 0.0005 and T1("LR|SMOTE|raw|1-5%|share") <= 0.0005)
chk("nguyên trạng: dải trung thực (1–5 %: 10–50/1 000; 5–20 %: 50–200/1 000; < 1 %: < 10/1 000)",
    0.01 <= T1("LR|N0|raw|1-5%|obs") <= 0.05 and 0.05 <= T1("LR|N0|raw|5-20%|obs") <= 0.20
    and T1("LR|N0|raw|<1%|obs") < 0.01)
chk("khớp trung bình: dải trung thực trở lại (1–5 % và 5–20 % đúng khoảng)",
    0.01 <= T1("LR|SMOTE|mm_0.02|1-5%|obs") <= 0.05 and 0.05 <= T1("LR|SMOTE|mm_0.02|5-20%|obs") <= 0.20)
chk("'phần lớn trẻ ở dải 1–5 %' khi nguyên trạng", T1("LR|N0|raw|1-5%|share") > 0.5)

# ---------------------------------------------------------------- 3.3 năng lực
chk("LR nguyên trạng ở K = 5 % gấp > 4 lần ngẫu nhiên", T2("LR|N0|cap|0.05|ppv") / 0.02 > 4)
chk("LR: ROS/SMOTE/CW không có ý nghĩa ở cả 3 mức (9/9)",
    all(test(f"LR|{h}|cap|{K}|ppv")["p_bh"] >= 0.05 for h in DIST for K in TL["caps"]))
chk("LR: RUS giảm có ý nghĩa ở cả 3 mức",
    all(test(f"LR|RUS|cap|{K}|ppv")["effect"] < 0 and test(f"LR|RUS|cap|{K}|ppv")["p_bh"] < 0.05 for K in TL["caps"]))
chk("RF: ROS/SMOTE/CW giảm có ý nghĩa ở mọi mức (9/9)",
    all(test(f"RF|{h}|cap|{K}|ppv")["effect"] < 0 and test(f"RF|{h}|cap|{K}|ppv")["p_bh"] < 0.05
        for h in DIST for K in TL["caps"]))
chk("RF: RUS tăng có ý nghĩa ở K = 5 % và 10 %",
    all(test(f"RF|RUS|cap|{K}|ppv")["effect"] > 0 and test(f"RF|RUS|cap|{K}|ppv")["p_bh"] < 0.05 for K in (0.05, 0.1)))
chk("dấu * trong Bảng 3 khớp đúng số phép kiểm có ý nghĩa",
    b.tables()["TABLE3"].count("\\*") == sum(test(f"{m}|{h}|cap|{K}|ppv")["p_bh"] < 0.05
                                            for m in ("LR", "RF") for h in RS for K in TL["caps"]))
chk("năng lực dùng thứ hạng: sửa thang không đổi thứ hạng (δ hữu hạn, mm tăng đơn điệu)",
    all(abs(T3(f"{m}|{h}|mm_0.02|delta")) < 15 for m in ("LR", "RF") for h in TL["methods"]))
chk("RF: SMOTE bỏ lỡ thêm trẻ mắc (độ nhạy ở K = 5 % thấp hơn)",
    T2("RF|SMOTE|cap|0.05|sens") < T2("RF|N0|cap|0.05|sens"))

# ---------------------------------------------------------------- 3.4 ngưỡng
chk("LR sau cân bằng lại: chuyển ≥ 99,9 % ở 2 % và 5 %",
    all(T2(f"LR|{h}|raw|{pt}|refer") >= 0.999 for h in RS for pt in (0.02, 0.05)))
chk("LR sau cân bằng lại: NB ở 5 % = NB 'chuyển tất cả' (±0,05 phần nghìn)",
    all(abs(T2(f"LR|{h}|raw|0.05|nb") - TL["ref_all"]["0.05"]) < 5e-5 for h in RS))
chk("'chuyển tất cả' tệ hơn không chuyển ai ở 5 %", TL["ref_all"]["0.05"] < 0)
chk("'dài gấp khoảng hai mươi lần' năng lực 5 % (LR SMOTE chuyển ≥ 95 % ở 5 %)",
    T2("LR|SMOTE|raw|0.05|refer") / 0.05 >= 19)
chk("RF SMOTE ở 5 %: NB âm, nguyên trạng dương", T2("RF|SMOTE|raw|0.05|nb") < 0 < T2("RF|N0|raw|0.05|nb"))
chk("RF SMOTE thô: NB thấp hơn nguyên trạng ở cả 3 ngưỡng (có ý nghĩa)",
    all(test(f"RF|SMOTE|raw|nb|{pt}")["effect"] < 0 and test(f"RF|SMOTE|raw|nb|{pt}")["p_bh"] < 0.05 for pt in TL["pts"]))
cur = TL["curves"]
chk("Hình 3a: LR SMOTE thô trùng 'chuyển tất cả' tại p_t ≤ 2 % (±0,2 phần nghìn)",
    all(abs(cur["LR|SMOTE|raw"][i] - TL["ref_all_fine"][i]) < 2e-4 for i, t in enumerate(TL["pt_fine"]) if t <= 0.02))
chk("Hình 3a: LR SMOTE pc/mm gần đường nguyên trạng (±0,5 phần nghìn trên toàn dải)",
    max(abs(cur[f"LR|SMOTE|{c}"][i] - cur["LR|N0|raw"][i]) for c in ("pc", "mm_0.02")
        for i in range(len(TL["pt_fine"]))) < 5e-4)
chk("Hình 3b: RF SMOTE pc/mm thấp hơn nguyên trạng ở p_t 2–5 %",
    all(cur[f"RF|SMOTE|{c}"][i] < cur["RF|N0|raw"][i] for c in ("pc", "mm_0.02")
        for i, t in enumerate(TL["pt_fine"]) if 0.02 <= t <= 0.05))

# ---------------------------------------------------------------- 3.5 sửa thang
chk("LR: hệ số góc quanh 1 (0,85–1,25) ở mọi cách huấn luyện",
    all(0.85 <= T3(f"LR|{h}|raw|slope") <= 1.25 for h in TL["methods"]))
chk("dịch log-odds không đổi hệ số góc (pc/mm = raw, ±1e-6) với LR",
    all(abs(T3(f"LR|{h}|{c}|slope") - T3(f"LR|{h}|raw|slope")) < 1e-6 for h in RS for c in ("mm_0.02", "mm_0.04")))
chk("LR: pc và mm đưa ECE ≤ 3,5 phần nghìn", all(T3(f"LR|{h}|{c}|ece") <= 0.0035 for h in RS for c in ("pc", "mm_0.02")))
chk("LR: NB sau pc/mm chênh nguyên trạng ≤ 0,5 phần nghìn",
    all(abs(test(f"LR|{h}|{c}|nb|{pt}")["effect"]) <= 5e-4 for h in RS for c in ("pc", "mm_0.02") for pt in TL["pts"]))
chk("'một vài hiệu số rất nhỏ vẫn có ý nghĩa' (có ≥ 1 và mọi cái ≤ 0,5 phần nghìn)",
    any(test(f"LR|{h}|{c}|nb|{pt}")["p_bh"] < 0.05 for h in RS for c in ("pc", "mm_0.02") for pt in TL["pts"]))
chk("RF: hệ số góc sau ROS/SMOTE/CW < 0,45 và < nguyên trạng",
    all(T3(f"RF|{h}|raw|slope") < min(0.45, T3("RF|N0|raw|slope")) for h in DIST))
chk("RF nguyên trạng 'đã quá phân tán' (hệ số góc < 0,7)", T3("RF|N0|raw|slope") < 0.7)
chk("RF: pc sửa quá tay (nguy cơ TB < 0,01) sau ROS/SMOTE/CW", all(T3(f"RF|{h}|pc|mean_p") < 0.01 for h in DIST))
chk("RF: pc làm NB ở 2 % thấp hơn nguyên trạng (có ý nghĩa) sau ROS/SMOTE/CW",
    all(test(f"RF|{h}|pc|nb|0.02")["effect"] < 0 and test(f"RF|{h}|pc|nb|0.02")["p_bh"] < 0.05 for h in DIST))
chk("RF: mm đưa nguy cơ TB về 0,0200 (±0,0002)", all(abs(T3(f"RF|{h}|mm_0.02|mean_p") - 0.02) < 2e-4 for h in DIST))
chk("RF: mm vẫn ECE > 10 phần nghìn và NB ở 5 % âm",
    all(T3(f"RF|{h}|mm_0.02|ece") > 0.010 and T2(f"RF|{h}|mm_0.02|0.05|nb") < 0 for h in DIST))
chk("RF RUS: hệ số góc ≈ 1 (0,85–1,15); pc NB 2 % cao hơn nguyên trạng có ý nghĩa",
    0.85 <= T3("RF|RUS|raw|slope") <= 1.15 and test("RF|RUS|pc|nb|0.02")["effect"] > 0
    and test("RF|RUS|pc|nb|0.02")["p_bh"] < 0.05)
chk("tóm tắt EN 'slope 0.3–0.4' (RF ROS/SMOTE/CW làm tròn 1 chữ số ∈ [0,3; 0,4])",
    all(0.3 <= round(T3(f"RF|{h}|raw|slope"), 1) <= 0.4 for h in DIST))
chk("tỷ lệ giả định 4 %: NB ở 5 % âm và chuyển nhiều hơn tỷ lệ đúng (LR SMOTE)",
    T2("LR|SMOTE|mm_0.04|0.05|nb") < 0 and T2("LR|SMOTE|mm_0.04|0.05|refer") > T2("LR|SMOTE|mm_0.02|0.05|refer"))
chk("đánh giá thấp gây hại ít hơn đánh giá cao ở p_t 5 % và 10 % (LR, mọi cách cân bằng lại)",
    all(T2(f"LR|{h}|mm_0.01|{pt}|nb") > T2(f"LR|{h}|mm_0.04|{pt}|nb") for h in RS for pt in (0.05, 0.1)))
chk("cập nhật chặn n = 100/200 kém khớp trung bình đúng (LR, mọi cách)",
    all(T3(f"LR|{h}|icpt_{n}|ece") > T3(f"LR|{h}|mm_0.02|ece") for h in RS for n in (100, 200)))
chk("n = 500: cập nhật chặn tốt hơn n = 200 nhưng vẫn kém khớp trung bình (LR SMOTE)",
    T3("LR|SMOTE|mm_0.02|ece") < T3("LR|SMOTE|icpt_500|ece") < T3("LR|SMOTE|icpt_200|ece"))
chk("LR: Platt kém cập nhật chặn ở mọi n (LR SMOTE)",
    all(T3(f"LR|SMOTE|platt_{n}|ece") > T3(f"LR|SMOTE|icpt_{n}|ece") for n in TL["n_audit"]))
chk("hệ số góc Platt âm có xảy ra ở n = 100 và 200, hiếm ở n = 500",
    b.build_subs()["PLATT_NEG_100"].split("/")[0] != "0" and
    int(b.build_subs()["PLATT_NEG_500"].split("/")[0]) < int(b.build_subs()["PLATT_NEG_200"].split("/")[0]))
chk("RF SMOTE: Platt n = 500 là ECE thấp nhất trong Bảng 5 nhưng NB ở 5 % < nguyên trạng",
    T3("RF|SMOTE|platt_500|ece") == min(T3(f"RF|SMOTE|{c}|ece") for c in
                                        ("raw", "pc", "mm_0.01", "mm_0.02", "mm_0.04", "icpt_100", "icpt_200",
                                         "icpt_500", "platt_500"))
    and T2("RF|SMOTE|platt_500|0.05|nb") < T2("RF|N0|raw|0.05|nb"))
chk("tóm tắt: ít nhãn (100–200) kém khớp trung bình cho cả LR và RF sau SMOTE",
    all(T3(f"{m}|SMOTE|icpt_{n}|ece") > T3(f"{m}|SMOTE|mm_0.02|ece") for m in ("LR", "RF") for n in (100, 200)))

# ---------------------------------------------------------------- 3.6 công cụ
a, bb, c = DEMO["A_LR_SMOTE_khong_nhan"], DEMO["B_RF_SMOTE_co_1000_nhan"], DEMO["C_LR_nguyen_trang_co_1000_nhan"]
chk("A: 5 000 điểm không nhãn, thổi phồng > 1,5, vượt năng lực", a["n"] == 5000 and "nhan" not in a
    and a["he_so_thoi_phong"] > 1.5 and a["tai_chuyen"]["0.05"] > 0.05)
chk("B: 1 000 hồ sơ có nhãn, NB 5 % tăng sau sửa, hệ số góc < 0,7 và có cảnh báo hình dạng",
    bb["n"] == 1000 and bb["loi_ich_rong_x1000"]["0.05"]["sau"] > bb["loi_ich_rong_x1000"]["0.05"]["truoc"]
    and bb["sua_thang"]["he_so_goc_hieu_chinh"] < 0.7 and any("HÌNH DẠNG" in w for w in bb["canh_bao"]))
chk("C: thổi phồng ≈ 1, 2 % trong KTC Wilson, cảnh báo DUY NHẤT là vượt năng lực ở 5 %",
    0.8 < c["he_so_thoi_phong"] < 1.2 and c["nhan"]["ty_le_du_kien_trong_KTC"]
    and len(c["canh_bao"]) == 1 and "năng lực" in c["canh_bao"][0] and c["tai_chuyen"]["0.05"] > 0.05)

# ---------------------------------------------------------------- hình thức
chk("không còn ô {{…}} hay trích dẫn [@…] chưa điền", "{{" not in MD and "[@" not in MD and "{@" not in MD)
for i in (1, 2, 3):
    f = f"p11tl_{'en_' if EN else ''}fig{i}.png"
    chk(f"hình {i} tồn tại và được chèn", os.path.exists(os.path.join(b.OUTDIR, f)) and f in MD)
for i in range(1, 7):
    lab = "Table" if EN else "Bảng"
    chk(f"{lab} {i} có chú thích và được nhắc trong bài", MD.count(f"**{lab} {i}.**") == 1 and MD.count(f"{lab} {i}") >= 2)
for i in (1, 2, 3):
    lab = "Figure" if EN else "Hình"
    chk(f"{lab} {i} được nhắc trong bài", MD.count(f"{lab} {i}") >= 2)
chk("mọi tài liệu trong danh mục được trích (không thừa)", len(re.findall(r"^\S.*\(\d{4}[a-c]?\)\.", MD, re.M)) >= 30)
nums = re.findall(r"\\\(|\$\$.*?\((\d)\)\$\$", MD)
chk("ba công thức đánh số (1)–(3)", all(f"({k})$$" in MD.replace(" ", "") or f"\\qquad({k})" in MD.replace(" ", "")
                                        for k in (1, 2, 3)))
body = MD.split("# REFERENCES" if EN else "# TÀI LIỆU THAM KHẢO")[0]
nwords = len(re.findall(r"\w+", body))
chk(f"độ dài thân bài hợp lý ({nwords} từ, 5 000–12 000)", 5000 <= nwords <= 12000)
chk("khai báo dữ liệu tổng hợp ở tóm tắt và hạn chế",
    ("synthetic data" in MD if EN else "dữ liệu tổng hợp" in MD) and MD.count("synthetic" if EN else "tổng hợp") >= 5)
chk("khai báo công bố liên quan (hai bản đi kèm + bản ngôn ngữ còn lại)",
    ("Related publications" in MD and "Vietnamese-language version" in MD) if EN else
    ("Công bố liên quan" in MD and "bản tiếng Anh" in MD))
if EN:
    chk("bản EN không còn chữ tiếng Việt ngoài tên riêng/tài liệu",
        not re.search(r"[ăâđêôơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]",
                      body.split("# 1. INTRODUCTION")[1]))
    chk("bản EN dùng dấu chấm thập phân (không có '0,0')", not re.search(r"\b0,\d", body))
else:
    chk("bản Việt dùng dấu phẩy thập phân trong thân bài (không có '0.0' ngoài tóm tắt tiếng Anh)",
        not re.search(r"\b0\.\d", body.split("# 1. ĐẶT VẤN ĐỀ")[1]))

txt = "\n".join(out) + f"\n\nĐẠT {ok}/{len(out)}\n"
name = "p11_tl_en_kiem_tra.txt" if EN else "p11_tl_kiem_tra.txt"
open(os.path.join(b.OUTDIR, name), "w", encoding="utf-8").write(txt)
print(txt)
