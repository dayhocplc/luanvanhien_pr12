# -*- coding: utf-8 -*-
"""
p11_referral_audit.py — kiểm tra đầu ra của một công cụ sàng lọc TRƯỚC KHI một dịch vụ tâm lý dùng nó để
xếp danh sách chờ đánh giá hoặc để nói con số nguy cơ với gia đình (bài P11, bản công nghệ hỗ trợ tâm lý trị liệu).

    python src/p11_referral_audit.py --demo
    python src/p11_referral_audit.py diem.csv --prevalence 0.02 [--capacity 0.05] [--pt 0.02 0.05 0.10]
                                     [--score-col score] [--label-col label]
                                     [--train-prev 0.02 --balanced-prev 0.5] [--out bao_cao.json]

Đầu vào: CSV mỗi dòng một trẻ đã sàng lọc, cột điểm (xác suất 0–1 do công cụ xuất) và, nếu có, cột nhãn 0/1
từ đánh giá chuyên sâu. Công cụ KHÔNG chẩn đoán. Nó trả lời năm câu hỏi:

  1. THỔI PHỒNG: xác suất trung bình gấp bao nhiêu lần tỷ lệ mắc dự kiến của quần thể? (> 1,5 lần → nhiều khả
     năng mô hình được huấn luyện trên dữ liệu đã tái lấy mẫu / gán trọng số lớp, hoặc điểm không phải xác suất.)
  2. TẢI CHUYỂN: với quy tắc "chuyển khi nguy cơ ≥ p_t", bao nhiêu phần trăm trẻ bị chuyển — so với năng lực
     đánh giá của dịch vụ?
  3. NĂNG LỰC: nếu dịch vụ nhận đúng K % trẻ điểm cao nhất, điểm cắt là bao nhiêu và có bao nhiêu trẻ trùng
     điểm ở ranh giới (phải bốc thăm)?
  4. SỬA THANG không cần nhãn: hiệu chỉnh tiên nghiệm (nếu nhà cung cấp khai báo tỷ lệ huấn luyện và tỷ lệ sau
     cân bằng) hoặc "khớp trung bình" (dịch log-odds để xác suất trung bình bằng tỷ lệ dự kiến). Cả hai giữ
     nguyên thứ hạng; chúng KHÔNG sửa được biến dạng hình dạng (hệ số góc hiệu chỉnh xa 1).
  5. Nếu có nhãn: tỷ lệ quan sát (KTC Wilson 95 %), tỷ lệ dự kiến có nằm trong KTC không, hệ số góc hiệu chỉnh
     (chỉ khi ≥ 10 ca dương — dưới mức đó ước lượng quá nhiễu), lợi ích ròng trước/sau sửa.

Các ngưỡng cảnh báo (1,5 lần; hệ số góc ngoài [0,7; 1,4]; 10 ca dương) là quy ước của nghiên cứu mô phỏng
out/reports/p11_tl.json, không phải chuẩn lâm sàng. Chỉ phụ thuộc numpy.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np

CLIP = 1e-6
BANDS = [0.0, 0.01, 0.05, 0.20, 1.0000001]
BAND_LABEL = ["dưới 1 %", "1–5 %", "5–20 %", "từ 20 % trở lên"]
INFLATION_WARN = 1.5
SLOPE_OK = (0.7, 1.4)
MIN_EVENTS_SLOPE = 10


def logit(p):
    p = np.clip(np.asarray(p, dtype=float), CLIP, 1 - CLIP)
    return np.log(p / (1 - p))


def sigm(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -60, 60)))


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def shift_to_mean(p, target_mean):
    z = logit(p)
    lo, hi = -15.0, 15.0
    for _ in range(90):
        mid = 0.5 * (lo + hi)
        if sigm(z + mid).mean() > target_mean:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def prior_correct(p, pi, pi_s):
    p = np.clip(np.asarray(p, dtype=float), 0.0, 1.0)
    a = p * (pi / pi_s)
    b = (1.0 - p) * ((1.0 - pi) / (1.0 - pi_s))
    return a / np.maximum(a + b, 1e-300)


def calib_slope(y, p):
    x = logit(p)
    y = np.asarray(y, dtype=float)

    def ll(a_, b_):
        z = a_ + b_ * x
        return float(np.sum(y * z - np.logaddexp(0.0, z)))

    a, b = 0.0, 1.0
    cur = ll(a, b)
    for _ in range(100):
        q = sigm(a + b * x)
        w = q * (1 - q)
        g = np.array([np.sum(y - q), np.sum((y - q) * x)])
        H = np.array([[w.sum(), (w * x).sum()], [(w * x).sum(), (w * x * x).sum()]])
        try:
            step = np.linalg.solve(H + 1e-9 * np.eye(2), g)
        except np.linalg.LinAlgError:
            break
        t = 1.0
        while t > 1e-8:
            new = ll(a + t * step[0], b + t * step[1])
            if new >= cur - 1e-12:
                break
            t *= 0.5
        a, b, cur = a + t * step[0], b + t * step[1], new
        if np.max(np.abs(t * step)) < 1e-10:
            break
    return float(b)


def bands(p, y=None):
    idx = np.digitize(p, BANDS[1:-1], right=False)
    out = []
    for b, lab in enumerate(BAND_LABEL):
        m = idx == b
        r = {"dai": lab, "ty_trong": float(m.mean()), "tren_1000_tre": int(round(1000 * m.mean())),
             "nguy_co_TB_hien_thi": float(p[m].mean()) if m.any() else None}
        if y is not None:
            k, n = int(y[m].sum()), int(m.sum())
            r["ty_le_quan_sat"] = k / n if n else None
            r["wilson95"] = list(wilson(k, n)) if n else None
        out.append(r)
    return out


def capacity_cut(p, frac):
    n = len(p)
    K = max(1, int(round(frac * n)))
    s = np.sort(p)[::-1]
    v = float(s[K - 1])
    above = int((p > v).sum())
    tie = int((p == v).sum())
    return {"K_tre": K, "diem_cat": v, "tre_tren_diem_cat": above, "tre_trung_diem_o_ranh_gioi": tie,
            "phai_boc_tham": tie > (K - above)}


def net_benefit(y, p, pt):
    refer = p >= pt
    n = len(y)
    tp = float(np.sum(refer & (y == 1)))
    fp = float(np.sum(refer & (y == 0)))
    return (tp - fp * pt / (1 - pt)) / n


def audit(p, prevalence=None, capacity=None, pts=(0.02, 0.05, 0.10), y=None, train_prev=None, balanced_prev=None):
    p = np.asarray(p, dtype=float)
    if p.max() > 1.0 + 1e-9:
        raise SystemExit("điểm > 1 — công cụ này cần xác suất 0–1 (điểm 0–100 phải chia 100 trước)")
    if prevalence is None and y is None:
        raise SystemExit("cần --prevalence hoặc cột nhãn")
    R = {"n": int(len(p)), "xac_suat_TB": float(p.mean()), "so_gia_tri_khac_nhau": int(len(np.unique(p)))}
    canh_bao = []
    if y is not None:
        y = np.asarray(y, dtype=int)
        k = int(y.sum())
        R["nhan"] = {"so_ca_duong": k, "ty_le_quan_sat": k / len(y), "wilson95": list(wilson(k, len(y)))}
        if prevalence is not None:
            lo, hi = R["nhan"]["wilson95"]
            R["nhan"]["ty_le_du_kien_trong_KTC"] = bool(lo <= prevalence <= hi)
    ref = prevalence if prevalence is not None else R["nhan"]["ty_le_quan_sat"]
    R["ty_le_tham_chieu"] = ref
    R["he_so_thoi_phong"] = float(p.mean() / ref) if ref > 0 else None
    if R["he_so_thoi_phong"] is not None and R["he_so_thoi_phong"] > INFLATION_WARN:
        canh_bao.append(f"Xác suất trung bình gấp {R['he_so_thoi_phong']:.1f} lần tỷ lệ tham chiếu: KHÔNG đọc con số "
                        "này cho gia đình như một xác suất; hỏi nhà cung cấp về tái lấy mẫu / trọng số lớp.")
    R["tai_chuyen"] = {str(pt): float((p >= pt).mean()) for pt in pts}
    if capacity is not None:
        R["nang_luc"] = capacity_cut(p, capacity)
        over = [pt for pt in pts if (p >= pt).mean() > capacity]
        if over:
            canh_bao.append("Quy tắc ngưỡng " + ", ".join(f"{100 * t:g} %" for t in over) +
                            f" chuyển nhiều hơn năng lực {100 * capacity:g} %: danh sách chờ sẽ vượt tải.")
        if R["nang_luc"]["phai_boc_tham"]:
            canh_bao.append(f"{R['nang_luc']['tre_trung_diem_o_ranh_gioi']} trẻ trùng điểm ở ranh giới năng lực: thứ tự "
                            "giữa các trẻ này do bốc thăm, không do công cụ.")
    R["dai_nguy_co_nguyen_trang"] = bands(p, y)
    # ---- sửa thang (giữ thứ hạng)
    if train_prev is not None and balanced_prev is not None:
        q = prior_correct(p, train_prev, balanced_prev)
        R["sua_thang"] = {"cach": "hiệu chỉnh tiên nghiệm (tỷ lệ nhà cung cấp khai báo)", "train_prev": train_prev,
                          "balanced_prev": balanced_prev}
        if prevalence is not None and abs(train_prev - prevalence) / prevalence > 0.25:
            canh_bao.append("Tỷ lệ huấn luyện khác tỷ lệ dự kiến tại chỗ > 25 %: sau hiệu chỉnh tiên nghiệm nên khớp "
                            "trung bình thêm một lần theo tỷ lệ tại chỗ.")
    else:
        d = shift_to_mean(p, ref)
        q = sigm(logit(p) + d)
        R["sua_thang"] = {"cach": "khớp trung bình (dịch log-odds, không cần nhãn)", "delta_log_odds": d,
                          "ti_so_odds": float(math.exp(d))}
    R["sua_thang"]["xac_suat_TB_sau"] = float(q.mean())
    R["sua_thang"]["tai_chuyen_sau"] = {str(pt): float((q >= pt).mean()) for pt in pts}
    R["sua_thang"]["dai_nguy_co_sau"] = bands(q, y)
    if y is not None:
        k = int(y.sum())
        if k >= MIN_EVENTS_SLOPE and k <= len(y) - MIN_EVENTS_SLOPE:
            s = calib_slope(y, q)
            R["sua_thang"]["he_so_goc_hieu_chinh"] = s
            if not (SLOPE_OK[0] <= s <= SLOPE_OK[1]):
                canh_bao.append(f"Hệ số góc hiệu chỉnh {s:.2f} ngoài [{SLOPE_OK[0]}; {SLOPE_OK[1]}]: biến dạng HÌNH DẠNG — "
                                "dịch log-odds không sửa được; cần mô hình không tái lấy mẫu hoặc hiệu chỉnh lại "
                                "trên đủ nhãn.")
        else:
            R["sua_thang"]["he_so_goc_hieu_chinh"] = None
            canh_bao.append(f"Chỉ có {k} ca dương: không ước lượng hệ số góc hiệu chỉnh (cần ≥ {MIN_EVENTS_SLOPE}). "
                            "Không kết luận được thang có bị biến dạng hình dạng hay không.")
        R["loi_ich_rong_x1000"] = {str(pt): {"truoc": 1000 * net_benefit(y, p, pt), "sau": 1000 * net_benefit(y, q, pt),
                                             "chuyen_tat_ca": 1000 * (k / len(y) - (1 - k / len(y)) * pt / (1 - pt))}
                                   for pt in pts}
    R["canh_bao"] = canh_bao
    return R, q


def text_report(R, title):
    L = [f"== {title} ==", f"n = {R['n']}; xác suất TB {R['xac_suat_TB']:.4f}; tỷ lệ tham chiếu {R['ty_le_tham_chieu']:.4f}"
         f" → thổi phồng × {R['he_so_thoi_phong']:.2f}"]
    L.append("Tải chuyển theo ngưỡng: " + "; ".join(f"p_t {float(k) * 100:g} %: {100 * v:.1f} % trẻ"
                                                     for k, v in R["tai_chuyen"].items()))
    if "nang_luc" in R:
        c = R["nang_luc"]
        L.append(f"Năng lực {c['K_tre']} trẻ: điểm cắt {c['diem_cat']:.4f}; trùng điểm ở ranh giới {c['tre_trung_diem_o_ranh_gioi']}")
    s = R["sua_thang"]
    L.append(f"Sửa thang — {s['cach']}: xác suất TB sau {s['xac_suat_TB_sau']:.4f}; tải chuyển sau: " +
             "; ".join(f"{float(k) * 100:g} %: {100 * v:.1f} %" for k, v in s["tai_chuyen_sau"].items()))
    L.append("Dải nguy cơ trước → sau (trên 1 000 trẻ): " + "; ".join(
        f"{a['dai']}: {a['tren_1000_tre']} → {b['tren_1000_tre']}"
        for a, b in zip(R["dai_nguy_co_nguyen_trang"], s["dai_nguy_co_sau"])))
    if "nhan" in R:
        h = R["nhan"]
        L.append(f"Nhãn: {h['so_ca_duong']} ca dương, tỷ lệ {h['ty_le_quan_sat']:.4f} "
                 f"(Wilson 95 % {h['wilson95'][0]:.4f}–{h['wilson95'][1]:.4f})")
        L.append("Lợi ích ròng ×1000 trước → sau: " + "; ".join(
            f"{float(k) * 100:g} %: {v['truoc']:.2f} → {v['sau']:.2f} (chuyển tất cả {v['chuyen_tat_ca']:.2f})"
            for k, v in R["loi_ich_rong_x1000"].items()))
        if s.get("he_so_goc_hieu_chinh") is not None:
            L.append(f"Hệ số góc hiệu chỉnh sau sửa: {s['he_so_goc_hieu_chinh']:.2f}")
    for w in R["canh_bao"]:
        L.append("  ! " + w)
    return "\n".join(L)


def demo():
    """Ba nhà cung cấp giả định trên dữ liệu tổng hợp của bài (kho _p11_pool.npz, tỷ lệ 2 %)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import run_p11_tl as T
    import run_imbalance as RI
    P = T.load_pools()
    rng = np.random.default_rng(20261200)
    Xtr, ytr = RI.draw(P["dev_pos"], P["dev_neg"], 5000, 0.02, rng)
    Xloc, _ = RI.draw(P["test_pos"], P["test_neg"], 5000, 0.02, rng)               # 5 000 trẻ, KHÔNG dùng nhãn
    Xlab, ylab = T.draw_binom(P["test_pos"], P["test_neg"], 1000, 0.02, rng)        # 1 000 hồ sơ có nhãn
    cases = [("A_LR_SMOTE_khong_nhan", "LR", "SMOTE", False), ("B_RF_SMOTE_co_1000_nhan", "RF", "SMOTE", True),
             ("C_LR_nguyen_trang_co_1000_nhan", "LR", "N0", True)]
    out, txt = {}, []
    for name, model, meth, lab in cases:
        Xr, yr, w = RI.resample(meth, Xtr, ytr, rng)
        p_loc, p_lab = T.fit_predict(model, Xr, yr, w, [Xloc, Xlab], 20261200)
        if lab:
            R, _ = audit(p_lab, prevalence=0.02, capacity=0.05, y=ylab)
        else:
            R, _ = audit(p_loc, prevalence=0.02, capacity=0.05)
        out[name] = R
        txt.append(text_report(R, name))
    os.makedirs(T.OUT_DIR, exist_ok=True)
    with open(os.path.join(T.OUT_DIR, "p11_tool_demo.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(os.path.join(T.OUT_DIR, "p11_tool_demo.txt"), "w", encoding="utf-8") as f:
        f.write("\n\n".join(txt) + "\n")
    print("\n\n".join(txt))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="?")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--score-col", default="score")
    ap.add_argument("--label-col", default=None)
    ap.add_argument("--prevalence", type=float, default=None)
    ap.add_argument("--capacity", type=float, default=None)
    ap.add_argument("--pt", type=float, nargs="+", default=[0.02, 0.05, 0.10])
    ap.add_argument("--train-prev", type=float, default=None)
    ap.add_argument("--balanced-prev", type=float, default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.demo:
        demo()
        return 0
    if not a.csv:
        ap.error("cần tệp CSV hoặc --demo")
    rows = list(csv.DictReader(open(a.csv, encoding="utf-8-sig")))
    p = np.array([float(r[a.score_col]) for r in rows])
    y = np.array([int(float(r[a.label_col])) for r in rows]) if a.label_col else None
    R, _ = audit(p, a.prevalence, a.capacity, a.pt, y, a.train_prev, a.balanced_prev)
    print(text_report(R, os.path.basename(a.csv)))
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(R, f, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
