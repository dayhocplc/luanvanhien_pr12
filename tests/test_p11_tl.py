# -*- coding: utf-8 -*-
"""Kiểm thử đơn vị cho Bài 11 bản tâm lý trị liệu. Chạy từ gốc kho:  python tests/test_p11_tl.py

Kiểm các hàm mà kết luận của bài dựa vào: hiệu chỉnh tiên nghiệm, khớp trung bình, hệ số góc hiệu chỉnh, nhận theo
năng lực có trùng điểm, lợi ích ròng, và các nhánh cảnh báo của công cụ kiểm tra. Không cần kho hồ sơ (vài giây).
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import p11_referral_audit as tool  # noqa: E402
import run_p11_tl as tl  # noqa: E402


def synth(n, prev, shift=1.2, seed=0):
    rng = np.random.default_rng(seed)
    y = (rng.random(n) < prev).astype(int)
    z = rng.normal(-4.0 + shift * y, 0.8)
    return 1 / (1 + np.exp(-z)), y


def test_prior_correction_inverts_balancing():
    # p ở tỷ lệ 0,5 tương ứng với q ở tỷ lệ π: odds(q) = odds(p) · [π/(1−π)] / [0,5/0,5]
    p = np.array([0.1, 0.5, 0.9])
    q = tl.prior_correct(p, 0.02)
    expect = (p / (1 - p)) * (0.02 / 0.98)
    assert np.allclose(q / (1 - q), expect)
    assert np.allclose(tl.prior_correct(p, 0.5), p)          # π = π_s → đồng nhất
    assert np.allclose(tool.prior_correct(p, 0.02, 0.5), q)  # công cụ dùng cùng công thức


def test_shift_to_mean_hits_target_and_keeps_order():
    p, _ = synth(5000, 0.02, seed=1)
    p = np.clip(p * 15, 0, 0.99)                            # thang bị thổi phồng
    d = tl.shift_to_mean(p, 0.02 * len(p))
    q = tl.sigm(tl.logit(p) + d)
    assert abs(q.mean() - 0.02) < 1e-9 and d < 0
    assert np.all(np.diff(q[np.argsort(p)]) >= 0)
    d2 = tool.shift_to_mean(p, 0.02)
    assert abs(d - d2) < 1e-9


def test_calib_slope_matches_unpenalised_logistic():
    rng = np.random.default_rng(2)
    x = rng.uniform(-5.3, -1.4, 50000)
    y = (rng.random(50000) < tl.sigm(0.55 + 1.15 * x)).astype(int)
    b = tl.calib_slope(y, tl.sigm(x))
    assert abs(b - 1.15) < 0.1                              # hội tụ từ điểm khởi đầu xa (bản cũ phân kỳ)
    assert abs(tool.calib_slope(y, tl.sigm(x)) - b) < 1e-9
    assert abs(tl.calib_slope(y, tl.sigm(tl.logit(tl.sigm(x)) + 2.0)) - b) < 1e-6   # dịch không đổi hệ số góc


def test_capacity_expected_value_with_ties():
    y = np.array([1, 0, 1, 0, 0, 0, 0, 0, 0, 0])
    s = np.array([.9, .5, .5, .5, .5, .1, .1, .1, .1, .1])
    c = tl.capacity(y, s, 0.3)                              # K = 3: 1 trẻ trên + 2 trong 4 trẻ trùng .5 (1 dương)
    assert abs(c["ppv"] - (1 + 2 / 4) / 3) < 1e-12
    assert abs(c["sens"] - (1 + 0.5) / 2) < 1e-12
    cut = tool.capacity_cut(s, 0.3)
    assert cut["K_tre"] == 3 and cut["tre_trung_diem_o_ranh_gioi"] == 4 and cut["phai_boc_tham"]


def test_decision_net_benefit_by_hand():
    y = np.array([1, 1, 0, 0, 0, 0, 0, 0, 0, 0])
    q = np.array([.9, .1, .8, .7, .1, .1, .1, .1, .1, .1])
    r = tl.decision(y, q, 0.5)
    assert r["refer"] == 0.3 and abs(r["nb"] - (1 / 10 - 2 / 10)) < 1e-12
    assert abs(tool.net_benefit(y, q, 0.5) - r["nb"]) < 1e-12


def test_wilson_interval_known_value():
    lo, hi = tool.wilson(24, 1000)
    assert abs(lo - 0.01617) < 2e-4 and abs(hi - 0.03551) < 2e-4


def test_audit_flags_inflated_rebalanced_scores():
    p, _ = synth(5000, 0.02, seed=3)
    infl = tl.sigm(tl.logit(p) + math.log(49))              # như cân bằng lại 2 % → 50 %
    R, q = tool.audit(infl, prevalence=0.02, capacity=0.05)
    assert R["he_so_thoi_phong"] > 1.5 and any("thổi phồng" in w or "gấp" in w for w in R["canh_bao"])
    assert abs(q.mean() - 0.02) < 1e-6
    assert R["sua_thang"]["tai_chuyen_sau"]["0.05"] < R["tai_chuyen"]["0.05"]


def test_audit_slope_needs_ten_events_and_flags_shape():
    p, y = synth(400, 0.01, seed=4)                         # ~4 ca dương
    R, _ = tool.audit(p, prevalence=0.01, y=y)
    assert R["sua_thang"]["he_so_goc_hieu_chinh"] is None
    rng = np.random.default_rng(5)
    x = rng.normal(-4, 1.5, 20000)
    y2 = (rng.random(20000) < tl.sigm(-4 + 0.35 * (x + 4))).astype(int)   # thang quá phân tán, hệ số góc 0,35
    R2, _ = tool.audit(tl.sigm(x), prevalence=float(y2.mean()), y=y2)
    assert R2["sua_thang"]["he_so_goc_hieu_chinh"] < 0.7 and any("HÌNH DẠNG" in w for w in R2["canh_bao"])


def test_audit_rejects_0_100_scale():
    try:
        tool.audit(np.array([10.0, 50.0]), prevalence=0.02)
    except SystemExit:
        return
    raise AssertionError("phải từ chối thang 0–100")


if __name__ == "__main__":
    n = 0
    for name, f in sorted(globals().items()):
        if name.startswith("test_") and callable(f):
            f()
            n += 1
            print(f"  đạt: {name}")
    print(f"{n}/{n} kiểm thử đạt")
