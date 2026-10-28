# -*- coding: utf-8 -*-
"""
run_imbalance.py — T12 + T14 + T17: MẤT CÂN BẰNG LỚP VÀ ĐIỂM VẬN HÀNH (bài P11).

    .venv/Scripts/python.exe src/run_imbalance.py
    IMB_REPS=3 IMB_NTEST=8000 .venv/Scripts/python.exe src/run_imbalance.py   # thử nhanh

CÂU HỎI
-------
Ở tỷ lệ hiện mắc 1–5 %, thực hành phổ biến là tái lấy mẫu tập huấn luyện
(SMOTE, lấy mẫu thừa, lấy mẫu thiếu) rồi báo cáo AUC hoặc accuracy. Ba câu hỏi:

  (1) Tái lấy mẫu có làm mô hình PHÂN BIỆT tốt hơn không (PR-AUC)?
  (2) Nó làm gì với HIỆU CHỈNH XÁC SUẤT (Brier, ECE, xác suất trung bình)?
  (3) Ở cấp QUYẾT ĐỊNH, nó hơn hay kém việc chỉ dịch chuyển ngưỡng (net benefit)?

THIẾT KẾ
--------
  • 7 cách xử lý mất cân bằng × 4 mô hình × 4 tỷ lệ hiện mắc = 112 ô
  • Mỗi ô lặp R lần: TRAIN 5 000 + CALIB 2 000 rút lại ở mỗi lần lặp
  • TEST CỐ ĐỊNH n = 50 000 cho mỗi tỷ lệ hiện mắc                        (T12)
  • Đường cong quyết định / net benefit trên dải ngưỡng ưu tiên          (T14)
  • Hiệu chỉnh Benjamini–Hochberg trên TOÀN BỘ phép so sánh đã thực hiện (T17)

HAI ĐIỂM THIẾT KẾ ĐÁNG NÓI
--------------------------
1. Bốn cột tỷ lệ hiện mắc được dựng bằng cách rút lại từ cùng một kho hồ sơ
   dương và một kho hồ sơ âm. Bộ sinh chỉ dùng tỷ lệ hiện mắc ở đúng một chỗ —
   bước tung đồng xu z — nên phân phối đặc trưng CÓ ĐIỀU KIỆN theo z không đổi.
   Do đó biến duy nhất thay đổi giữa bốn cột là tỷ lệ trộn hai lớp.

2. Cách "dịch chuyển ngưỡng" dùng ĐÚNG mô hình của cách "nguyên trạng"; chỉ
   điểm cắt là khác. Vì vậy PR-AUC và Brier của hai cách bằng nhau THEO XÂY
   DỰNG, và cách này chỉ tham gia nhóm chỉ số cấp quyết định.

Kịch bản chạy sinh ra out/reports/imbalance.json.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import json
import time
import warnings

import numpy as np

warnings.filterwarnings("ignore")

from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KDTree

import config as cfg
from ts_dataset import load_questions
from ts_features import build_feature_vector
from ts_fuzzy import build_all_fis, infer_all_domains, risk_to_unit
from ts_simulate import generate_dataset

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(PROJECT_DIR, "out", "reports")

# ------------------------------------------------------------- hằng số chạy
SEED = 20260829
N_REPS = int(os.environ.get("IMB_REPS", "20"))
N_TEST = int(os.environ.get("IMB_NTEST", "50000"))       # T12
N_TRAIN = int(os.environ.get("IMB_NTRAIN", "5000"))
N_CALIB = int(os.environ.get("IMB_NCALIB", "2000"))
PREVS = [0.01, 0.02, 0.03, 0.05]
PT_MAIN = 0.02                                           # ngưỡng ưu tiên chính
PT_GRID = np.round(np.concatenate([np.arange(0.002, 0.0201, 0.001),
                                   np.arange(0.022, 0.1001, 0.002)]), 6)

DOMS = ["GTNN", "VDTHO", "VDTINH", "BCHOC", "CNXH", "DHBT"]
PHI = np.array([cfg.SHAPLEY[d] for d in DOMS], dtype=float)

METHODS = ["N0", "RUS", "ROS", "SMOTE", "CW", "TS", "SMOTE_RC"]
METHOD_LABEL = {
    "N0": "nguyen trang",
    "RUS": "lay mau thieu",
    "ROS": "lay mau thua",
    "SMOTE": "SMOTE",
    "CW": "trong so lop",
    "TS": "dich chuyen nguong",
    "SMOTE_RC": "SMOTE + hieu chinh lai",
}

MODELS = ["LR", "RF", "FKNN", "HYB"]
MODEL_LABEL = {
    "LR": "hoi quy logistic",
    "RF": "rung ngau nhien",
    "FKNN": "Fuzzy k-NN",
    "HYB": "mo hinh lai ba nhanh",
}

EPS = 1e-12


# =====================================================================
# Chỉ số — bản vector hoá (ts_evaluate viết theo lối vòng lặp, quá chậm ở
# n = 50 000 × 112 ô × 20 lần lặp). Hai bản được đối chiếu trong self-test.
# =====================================================================
def roc_auc(y, s):
    y = np.asarray(y)
    s = np.asarray(s, dtype=float)
    n_pos = float(y.sum())
    n_neg = float(len(y) - n_pos)
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    order = np.argsort(s, kind="stable")
    ss = s[order]
    n = len(ss)
    r = np.empty(n, dtype=float)
    start = 0
    for i in range(1, n + 1):
        if i == n or ss[i] != ss[start]:
            r[order[start:i]] = 0.5 * (start + i - 1) + 1.0
            start = i
    return float((r[y == 1].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def average_precision(y, s):
    """Diện tích dưới đường cong precision–recall, tổng theo bậc thang.

    Các quan sát có cùng điểm số được gộp thành một bậc, nếu không thì thứ tự
    ngẫu nhiên bên trong nhóm trùng điểm sẽ tự nó tạo ra một phần diện tích."""
    y = np.asarray(y)
    s = np.asarray(s, dtype=float)
    n_pos = float(y.sum())
    if n_pos == 0:
        return float("nan")
    order = np.argsort(-s, kind="stable")
    ys = y[order]
    ss = s[order]
    tp = np.cumsum(ys)
    fp = np.cumsum(1 - ys)
    last = np.empty(len(ss), dtype=bool)
    last[:-1] = ss[:-1] != ss[1:]
    last[-1] = True
    tp = tp[last]
    fp = fp[last]
    prec = tp / np.maximum(tp + fp, EPS)
    rec = tp / n_pos
    d_rec = np.diff(np.concatenate([[0.0], rec]))
    return float((prec * d_rec).sum())


def brier(y, p):
    return float(np.mean((np.asarray(p, dtype=float)
                          - np.asarray(y, dtype=float)) ** 2))


def ece(y, p, n_bins=10):
    """Sai số hiệu chỉnh kỳ vọng, chia ô theo PHÂN VỊ của chính xác suất dự báo.

    Chia đều trên [0,1] gần như vô dụng ở tỷ lệ hiện mắc thấp vì hầu hết xác
    suất rơi vào ô đầu tiên; chia theo phân vị giữ số quan sát trong mỗi ô."""
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    edges = np.unique(np.quantile(p, np.linspace(0.0, 1.0, n_bins + 1)))
    if len(edges) < 2:
        return float(abs(p.mean() - y.mean()))
    idx = np.clip(np.searchsorted(edges, p, side="left") - 1, 0, len(edges) - 2)
    tot = 0.0
    for b in range(len(edges) - 1):
        m = idx == b
        if m.sum() == 0:
            continue
        tot += m.sum() / len(y) * abs(p[m].mean() - y[m].mean())
    return float(tot)


def nb_at_cut(y, s, cut, pt):
    """NB = TP/n - (FP/n) * (pt / (1 - pt)), quyết định theo quy tắc s >= cut."""
    y = np.asarray(y)
    s = np.asarray(s, dtype=float)
    pred = s >= cut
    tp = float(np.sum(pred & (y == 1)))
    fp = float(np.sum(pred & (y == 0)))
    return (tp - fp * (pt / (1.0 - pt))) / len(y), tp, fp


def net_benefit(y, p, pt):
    return nb_at_cut(y, p, pt, pt)


def _cum(y, s):
    """Sắp giảm dần theo điểm số, trả về (điểm số đã sắp, TP tích luỹ, FP tích
    luỹ) với phần tử 0 ứng với "không gắn cờ ai"."""
    order = np.argsort(-np.asarray(s, dtype=float), kind="stable")
    ys = np.asarray(y, dtype=float)[order]
    ss = np.asarray(s, dtype=float)[order]
    tp = np.concatenate([[0.0], np.cumsum(ys)])
    fp = np.concatenate([[0.0], np.cumsum(1.0 - ys)])
    return ss, tp, fp


def nb_curve_prob(y, p, pts):
    """Net benefit tại nhiều ngưỡng ưu tiên cùng lúc, quy tắc quyết định
    p >= pt. Một lần sắp xếp cho cả dải ngưỡng."""
    ss, tp, fp = _cum(y, p)
    pts = np.asarray(pts, dtype=float)
    idx = np.searchsorted(-ss, -pts, side="right")
    odds = pts / (1.0 - pts)
    return (tp[idx] - fp[idx] * odds) / len(y), tp[idx], fp[idx]


def best_cut_for_nb(y, s, pt):
    """Điểm cắt tối đa hoá net benefit thực nghiệm, chọn TRÊN TẬP HIỆU CHỈNH.

    Quét đủ mọi điểm cắt mà dữ liệu xác định (không lấy mẫu lưới), kể cả
    phương án "không gắn cờ ai" ứng với net benefit bằng 0 — phương án này là
    một lựa chọn hợp lệ trong phân tích đường cong quyết định."""
    ss, tp, fp = _cum(y, s)
    nb = (tp - fp * (pt / (1.0 - pt))) / len(y)
    # Chỉ vị trí ở CUỐI mỗi nhóm điểm số trùng nhau mới ứng với một điểm cắt
    # thực hiện được: cắt tại ss[j-1] luôn gắn cờ trọn nhóm trùng giá trị đó.
    ok = np.zeros(len(nb), dtype=bool)
    ok[0] = True                                  # "không gắn cờ ai", NB = 0
    ok[len(ss)] = True
    ok[1:len(ss)] = ss[:-1] != ss[1:]
    j = int(np.argmax(np.where(ok, nb, -np.inf)))
    if j == 0:                      # không điểm cắt nào cho net benefit dương
        return float(ss[0]) + 1.0
    return float(ss[j - 1])


# =====================================================================
# Bảy cách xử lý mất cân bằng
# =====================================================================
def smote(X, y, rng, k=5):
    """SMOTE gốc (Chawla 2002): nội suy tuyến tính tới một trong k láng giềng
    gần nhất CÙNG lớp thiểu số, sinh đến khi hai lớp cân bằng."""
    pos = np.flatnonzero(y == 1)
    neg = np.flatnonzero(y == 0)
    need = len(neg) - len(pos)
    if need <= 0 or len(pos) < 2:
        return X, y
    P = X[pos]
    kk = int(min(k, len(P) - 1))
    _, nb = KDTree(P).query(P, k=kk + 1)          # cột 0 là chính nó
    nb = nb[:, 1:]
    base = rng.integers(0, len(P), size=need)
    pick = nb[base, rng.integers(0, kk, size=need)]
    lam = rng.random((need, 1))
    New = P[base] + lam * (P[pick] - P[base])
    return (np.vstack([X, New]),
            np.concatenate([y, np.ones(need, dtype=y.dtype)]))


def resample(kind, X, y, rng):
    """→ (X', y', sample_weight hoặc None)."""
    pos = np.flatnonzero(y == 1)
    neg = np.flatnonzero(y == 0)
    if kind in ("N0", "TS"):
        return X, y, None
    if kind == "CW":
        w = np.where(y == 1, len(y) / (2.0 * max(len(pos), 1)),
                     len(y) / (2.0 * max(len(neg), 1)))
        return X, y, w
    if kind == "RUS":
        take = rng.choice(neg, size=len(pos), replace=False)
        idx = np.concatenate([pos, take])
        rng.shuffle(idx)
        return X[idx], y[idx], None
    if kind == "ROS":
        take = rng.choice(pos, size=len(neg), replace=True)
        idx = np.concatenate([neg, take])
        rng.shuffle(idx)
        return X[idx], y[idx], None
    if kind in ("SMOTE", "SMOTE_RC"):
        Xs, ys = smote(X, y, rng)
        return Xs, ys, None
    raise ValueError(kind)


# =====================================================================
# Bốn mô hình — mọi mô hình trả về xác suất trên thang [0,1]
# =====================================================================
class FuzzyKNN:
    """Fuzzy k-NN (Keller 1985) trên khoảng cách Euclid có trọng số Shapley.

    Toạ độ được nhân sẵn với căn bậc hai của trọng số, nên khoảng cách Euclid
    thường trên toạ độ đã nhân đúng bằng khoảng cách có trọng số; nhờ đó dùng
    được cây k-D thay cho ma trận khoảng cách đầy đủ 50 000 × 5 000."""

    def __init__(self, k=cfg.FKNN_K, m=cfg.FKNN_M):
        self.k = int(k)
        self.m = float(m)

    def fit(self, X, y, w=None):
        self.sc = np.sqrt(PHI)
        self.y = np.asarray(y, dtype=float)
        self.tree = KDTree(X * self.sc[None, :])
        self.cw = (np.ones(len(y), dtype=float) if w is None
                   else np.asarray(w, dtype=float))
        return self

    def predict_proba1(self, X):
        k = int(min(self.k, len(self.y)))
        d, i = self.tree.query(X * self.sc[None, :], k=k)
        wg = np.maximum(d, 1e-12) ** (-2.0 / (self.m - 1.0)) * self.cw[i]
        u = (wg * self.y[i]).sum(axis=1) / np.maximum(wg.sum(axis=1), EPS)
        exact = d[:, 0] <= 1e-12
        u[exact] = self.y[i[exact, 0]]
        return np.clip(u, 0.0, 1.0)


class FuzzyCMeans:
    """Fuzzy C-Means; mức nguy cơ của mỗi cụm gán từ nhãn của tập huấn luyện."""

    def __init__(self, c=cfg.FCM_C, m=cfg.FCM_M):
        self.c = int(c)
        self.m = float(m)

    def _u(self, X, C):
        d = np.maximum(np.linalg.norm(X[:, None, :] - C[None, :, :], axis=2), 1e-12)
        inv = d ** (-2.0 / (self.m - 1.0))
        return inv / inv.sum(axis=1, keepdims=True)

    def fit(self, X, y, seed, w=None):
        rng = np.random.default_rng(seed)
        y = np.asarray(y, dtype=float)
        sw = np.ones(len(y)) if w is None else np.asarray(w, dtype=float)
        U = rng.random((X.shape[0], self.c))
        U /= U.sum(axis=1, keepdims=True)
        C = None
        for _ in range(cfg.FCM_MAX_ITER):
            Um = U ** self.m
            C = (Um.T @ X) / np.maximum(Um.sum(axis=0)[:, None], EPS)
            U_new = self._u(X, C)
            if np.max(np.abs(U_new - U)) < cfg.FCM_TOL:
                U = U_new
                break
            U = U_new
        Um = U ** self.m
        self.C = (Um.T @ X) / np.maximum(Um.sum(axis=0)[:, None], EPS)
        U = self._u(X, self.C)
        hard = np.argmax(U, axis=1)
        risk = np.zeros(self.c, dtype=float)
        for j in range(self.c):
            ws = float((U[:, j] * sw).sum())
            if (int((hard == j).sum()) >= cfg.FCM_MIN_LABELED_PER_CLUSTER
                    and ws > EPS):
                risk[j] = float((U[:, j] * sw * y).sum() / ws)
            else:
                risk[j] = float(self.C[j] @ PHI)     # rơi về nhánh luật
        self.risk = risk
        return self

    def predict_proba1(self, X):
        return np.clip(self._u(X, self.C) @ self.risk, 0.0, 1.0)


def rule_branch(X):
    """Nhánh 1 — tích phân Choquet 2-cộng tính. Với INTERACTION = {} (kết quả
    P10.2 của đề tài) nó suy biến đúng bằng trung bình có trọng số Shapley."""
    return np.clip(X @ PHI, 0.0, 1.0)


def fit_predict(model, Xtr, ytr, w, Xte, seed):
    if model == "LR":
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(Xtr, ytr, sample_weight=w)
        return clf.predict_proba(Xte)[:, 1]
    if model == "RF":
        clf = RandomForestClassifier(n_estimators=200, min_samples_leaf=5,
                                     n_jobs=-1, random_state=seed)
        clf.fit(Xtr, ytr, sample_weight=w)
        return clf.predict_proba(Xte)[:, 1]
    if model == "FKNN":
        return FuzzyKNN().fit(Xtr, ytr, w).predict_proba1(Xte)
    if model == "HYB":
        f = FuzzyKNN().fit(Xtr, ytr, w).predict_proba1(Xte)
        g = FuzzyCMeans().fit(Xtr, ytr, seed, w).predict_proba1(Xte)
        r = rule_branch(Xte)
        W = cfg.FUSION_WEIGHTS
        return np.clip(W["rule"] * r + W["fknn"] * f + W["fcm"] * g, 0.0, 1.0)
    raise ValueError(model)


def _logit(p):
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def platt(p_ca, y_ca, p_target):
    """Hiệu chỉnh lại theo Platt trên thang log-odds, khớp trên TẬP HIỆU CHỈNH.

    Tập hiệu chỉnh giữ nguyên tỷ lệ hiện mắc thật và không hề bị tái lấy mẫu;
    đó là toàn bộ lý do phép hiệu chỉnh này sửa được cái mà SMOTE làm hỏng."""
    y_ca = np.asarray(y_ca)
    if len(np.unique(y_ca)) < 2:
        return p_target
    lr = LogisticRegression(max_iter=1000)
    lr.fit(_logit(p_ca)[:, None], y_ca)
    return lr.predict_proba(_logit(p_target)[:, None])[:, 1]


# =====================================================================
# T17 — Benjamini–Hochberg
# =====================================================================
def bh_adjust(p):
    p = np.asarray(p, dtype=float)
    m = len(p)
    order = np.argsort(p)
    q = np.empty(m, dtype=float)
    prev = 1.0
    for rank in range(m - 1, -1, -1):
        i = order[rank]
        prev = min(prev, p[i] * m / (rank + 1))
        q[i] = prev
    return np.clip(q, 0.0, 1.0)


# =====================================================================
# Kho hồ sơ
# =====================================================================
def featurize(records, questions, fis):
    X, y = [], []
    for rec in records:
        try:
            fv = build_feature_vector(rec, questions)
        except Exception:
            continue                       # INV-4: bỏ trống > 30 % → từ chối
        risk = {k: v for k, v in infer_all_domains(fv, fis).items() if v is not None}
        u = risk_to_unit(risk, "point")
        if any(d not in u for d in DOMS):
            continue
        X.append([u[d] for d in DOMS])
        y.append(int(rec.label))
    return np.array(X, dtype=float), np.array(y, dtype=int)


def build_pools():
    """Kho hồ sơ dương và kho hồ sơ âm, sinh riêng rồi chia đôi DEV / TEST."""
    q = load_questions()
    fis = build_all_fis()
    t0 = time.time()
    n_pos_raw = int(os.environ.get("IMB_POOL_POS", "14000"))
    n_neg_raw = int(os.environ.get("IMB_POOL_NEG", "200000"))
    rp, _ = generate_dataset(n_pos_raw, q, seed=SEED, prevalence=1.0, prefix="POS")
    rn, _ = generate_dataset(n_neg_raw, q, seed=SEED + 1, prevalence=0.0, prefix="NEG")
    Xp, yp = featurize(rp, q, fis)
    Xn, yn = featurize(rn, q, fis)
    assert yp.min() == 1 and yn.max() == 0
    print(f"  kho duong {len(Xp)}/{n_pos_raw} · kho am {len(Xn)}/{n_neg_raw} · "
          f"{time.time() - t0:.1f}s", flush=True)
    hp, hn = len(Xp) // 2, len(Xn) // 2
    return {"dev_pos": Xp[:hp], "dev_neg": Xn[:hn],
            "test_pos": Xp[hp:], "test_neg": Xn[hn:],
            "n_pos_raw": n_pos_raw, "n_neg_raw": n_neg_raw,
            "n_pos_kept": int(len(Xp)), "n_neg_kept": int(len(Xn))}


def draw(pool_pos, pool_neg, n, prev, rng):
    k = int(round(n * prev))
    ip = rng.choice(len(pool_pos), size=k, replace=False)
    ineg = rng.choice(len(pool_neg), size=n - k, replace=False)
    X = np.vstack([pool_pos[ip], pool_neg[ineg]])
    y = np.concatenate([np.ones(k, dtype=int), np.zeros(n - k, dtype=int)])
    o = rng.permutation(len(y))
    return X[o], y[o]


# =====================================================================
def main() -> int:
    t_all = time.time()
    print("=" * 78)
    print("P11 — MAT CAN BANG LOP VA DIEM VAN HANH")
    print("=" * 78)
    print(f"  {len(METHODS)} cach xu ly x {len(MODELS)} mo hinh x {len(PREVS)} "
          f"ty le hien mac = {len(METHODS) * len(MODELS) * len(PREVS)} o")
    print(f"  TRAIN {N_TRAIN} · CALIB {N_CALIB} · TEST {N_TEST} · {N_REPS} lan lap")
    print("Sinh kho ho so...", flush=True)
    P = build_pools()

    i_main = int(np.argmin(np.abs(PT_GRID - PT_MAIN)))
    assert abs(PT_GRID[i_main] - PT_MAIN) < 1e-9

    cells = {}      # (prev, model, method) -> {metric: [giá trị mỗi lần lặp]}
    diffs = {}      # (prev, model, method) -> {metric: [hiệu số so với N0]}
    curves = {}     # (prev, model, method) -> [đường NB mỗi lần lặp]
    ref = {}

    for prev in PREVS:
        Xte, yte = draw(P["test_pos"], P["test_neg"], N_TEST, prev,
                        np.random.default_rng(SEED + 100 + int(prev * 10000)))
        pi = float(yte.mean())
        ref[prev] = {
            "pi": pi, "n_pos": int(yte.sum()),
            "all": [float(pi - (1 - pi) * (t / (1 - t))) for t in PT_GRID],
            "all_main": float(pi - (1 - pi) * (PT_MAIN / (1 - PT_MAIN))),
        }
        print(f"\n[prev = {prev:.0%}]  TEST n = {len(yte)}, duong {int(yte.sum())} "
              f"({pi:.3%})", flush=True)

        for rep in range(N_REPS):
            rng = np.random.default_rng(SEED + 1000 * rep + int(prev * 10000))
            Xtr, ytr = draw(P["dev_pos"], P["dev_neg"], N_TRAIN, prev, rng)
            Xca, yca = draw(P["dev_pos"], P["dev_neg"], N_CALIB, prev, rng)

            for model in MODELS:
                cache = {}
                for meth in METHODS:
                    seed_m = SEED + 31 * rep + 7 * MODELS.index(model)
                    if meth == "TS":
                        p_te, p_ca = cache["N0"]
                    else:
                        Xr, yr, w = resample(meth, Xtr, ytr, rng)
                        p_te = fit_predict(model, Xr, yr, w, Xte, seed_m)
                        p_ca = fit_predict(model, Xr, yr, w, Xca, seed_m)
                        if meth == "SMOTE_RC":
                            p_te, p_ca = platt(p_ca, yca, p_te), platt(p_ca, yca, p_ca)
                    cache[meth] = (p_te, p_ca)

                    if meth == "TS":
                        nb_curve, tp, fp = [], 0.0, 0.0
                        for j, t in enumerate(PT_GRID):
                            cut = best_cut_for_nb(yca, p_ca, float(t))
                            v, a, b = nb_at_cut(yte, p_te, cut, float(t))
                            nb_curve.append(float(v))
                            if j == i_main:
                                tp, fp = a, b
                        nb_main = nb_curve[i_main]
                    else:
                        nbv, tpv, fpv = nb_curve_prob(yte, p_te, PT_GRID)
                        nb_curve = [float(v) for v in nbv]
                        nb_main = nb_curve[i_main]
                        tp, fp = float(tpv[i_main]), float(fpv[i_main])

                    flagged = tp + fp
                    rec = {
                        "pr_auc": average_precision(yte, p_te),
                        "roc_auc": roc_auc(yte, p_te),
                        "brier": brier(yte, p_te),
                        "ece": ece(yte, p_te),
                        "mean_p": float(np.mean(p_te)),
                        "nb": float(nb_main),
                        "flag_rate": float(flagged / len(yte)),
                        "nns": float(flagged / tp) if tp > 0 else float("nan"),
                        "sens": float(tp / max(int(yte.sum()), 1)),
                    }
                    key = (prev, model, meth)
                    slot = cells.setdefault(key, {})
                    for k, v in rec.items():
                        slot.setdefault(k, []).append(v)
                    curves.setdefault(key, []).append(nb_curve)

                base = cells[(prev, model, "N0")]
                for meth in METHODS:
                    if meth == "N0":
                        continue
                    cur = cells[(prev, model, meth)]
                    d = diffs.setdefault((prev, model, meth), {})
                    fam = ["nb"] if meth == "TS" else ["pr_auc", "brier", "nb"]
                    for k in fam:
                        d.setdefault(k, []).append(cur[k][-1] - base[k][-1])
            print(f"    lan lap {rep + 1}/{N_REPS} xong "
                  f"({time.time() - t_all:.0f}s)", flush=True)

    # ------------------------------------------------------- T17
    keys, fams, raw_p, eff = [], [], [], []
    for (prev, model, meth), d in diffs.items():
        for k, v in d.items():
            v = np.asarray(v, dtype=float)
            v = v[np.isfinite(v)]
            if len(v) < 3 or np.allclose(v, 0.0):
                p = 1.0
            else:
                p = float(stats.ttest_1samp(v, 0.0).pvalue)
            keys.append((prev, model, meth))
            fams.append(k)
            raw_p.append(p)
            eff.append(float(np.mean(v)))
    q = bh_adjust(np.array(raw_p))
    print(f"\nT17 — so phep kiem da thuc hien: {len(raw_p)}")

    out = {
        "seed": SEED, "n_reps": N_REPS, "n_test": N_TEST, "n_train": N_TRAIN,
        "n_calib": N_CALIB, "prevs": PREVS, "pt_main": PT_MAIN,
        "pt_grid": [float(t) for t in PT_GRID], "i_main": i_main,
        "methods": METHODS, "method_label": METHOD_LABEL,
        "models": MODELS, "model_label": MODEL_LABEL,
        "n_cells": len(METHODS) * len(MODELS) * len(PREVS),
        "n_tests": len(raw_p),
        "pool": {k: P[k] for k in
                 ("n_pos_raw", "n_neg_raw", "n_pos_kept", "n_neg_kept")},
        "ref": {f"{k}": v for k, v in ref.items()},
        "cells": {f"{p}|{m}|{h}": {k: [float(np.mean(v)),
                                       float(np.std(v, ddof=1)) if len(v) > 1 else 0.0]
                                   for k, v in c.items()}
                  for (p, m, h), c in cells.items()},
        "curves": {f"{p}|{m}|{h}": np.mean(np.asarray(v), axis=0).tolist()
                   for (p, m, h), v in curves.items()},
        "tests": [{"prev": k[0], "model": k[1], "method": k[2], "metric": f,
                   "effect": e, "p_raw": pr, "p_bh": float(qq)}
                  for k, f, e, pr, qq in zip(keys, fams, eff, raw_p, q)],
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "imbalance.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"\nDa ghi out/reports/imbalance.json  ({time.time() - t_all:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
