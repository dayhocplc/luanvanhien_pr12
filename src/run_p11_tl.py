# -*- coding: utf-8 -*-
"""
run_p11_tl.py — ba phân tích thực hành cho bản tiếng Việt hướng công nghệ hỗ trợ tâm lý trị liệu
của bài P11 (mất cân bằng lớp), 27/09/2026.

    .venv/Scripts/python.exe src/run_p11_tl.py            # ~10–20 phút (lần đầu thêm ~2,5 phút sinh kho)
    P11TL_REPS=2 .venv/Scripts/python.exe src/run_p11_tl.py --quick

Dùng lại NGUYÊN VẸN bộ sinh, kho hồ sơ, năm cách xử lý mất cân bằng và các mô hình của
run_imbalance.py (import trực tiếp; kho hồ sơ giống hệt kho của out/reports/p11_tasks.json), nên mọi
con số so sánh được với lưới chính. Mọi dữ liệu là dữ liệu tổng hợp; không có dữ liệu trẻ thật.

Bối cảnh: một dịch vụ tâm lý nhận trẻ được công cụ sàng lọc gắn cờ, tỷ lệ mắc cộng đồng 2 %
(gần tỷ lệ 2,0 % của nghiên cứu thực địa Cà Mau 2026). Hai mô hình phổ biến nhất trong y văn
sàng lọc bằng học máy: hồi quy logistic (LR) và rừng ngẫu nhiên (RF). Năm cách huấn luyện:
nguyên trạng (N0), lấy mẫu thiếu (RUS), lấy mẫu thừa (ROS), SMOTE, trọng số lớp (CW).

TL1 — Con số nguy cơ nói với gia đình. Bốn dải nguy cơ (< 1 %, 1–5 %, 5–20 %, ≥ 20 %): tỷ trọng
      trẻ trong mỗi dải và tỷ lệ mắc thật trong dải — trước và sau các phép sửa thang ở TL3.
TL2 — Hai cách vận hành dịch vụ.
      (a) Theo NĂNG LỰC: dịch vụ chỉ đánh giá được K % trẻ được sàng lọc (K = 2, 5, 10 %), nhận K %
          trẻ có điểm cao nhất. Chỉ thứ hạng quyết định → số ca thật trên 100 lượt đánh giá (PPV@K),
          độ nhạy@K. Trùng điểm ở ranh giới được chia theo kỳ vọng của việc bốc ngẫu nhiên.
      (b) Theo NGƯỠNG NGUY CƠ: chuyển khi xác suất ≥ p_t (2, 5, 10 %) → tỷ lệ trẻ bị chuyển,
          lợi ích ròng (Vickers & Elkin 2006), so với năng lực của dịch vụ.
TL3 — Kiểm tra và sửa thang trước khi triển khai, khi nhà cung cấp đã huấn luyện có tái lấy mẫu:
      raw    : dùng nguyên xác suất của mô hình;
      pc     : hiệu chỉnh tiên nghiệm giải tích (Saerens 2002) — cần BIẾT tỷ lệ huấn luyện và tỷ lệ
               sau tái lấy mẫu (0,5);
      mm_a   : "khớp trung bình" không cần nhãn — dịch log-odds δ sao cho xác suất trung bình trên
               chính quần thể tại chỗ (không nhãn) bằng tỷ lệ mắc giả định a (a = 1 %, 2 %, 4 %;
               a = 2 % là đúng, 1 % và 4 % là ước lượng sai gấp đôi);
      icpt_n : cập nhật hệ số chặn trên n hồ sơ có nhãn tại chỗ (n = 100, 200, 500; số ca dương
               ~ Nhị thức(n, 2 %));
      platt_n: khớp lại Platt đầy đủ trên cùng n hồ sơ đó.
      Chỉ số: xác suất trung bình, ECE (10 ô phân vị), Brier, hệ số góc hiệu chỉnh, tỷ lệ chuyển và
      lợi ích ròng ở p_t = 2, 5, 10 %.
      Mọi phép sửa là biến đổi đơn điệu tăng (trừ Platt khi hệ số góc âm) → không đổi thứ hạng.

T17: hiệu số ghép cặp theo lần lặp so với N0 (cùng mô hình), kiểm định t một mẫu, Benjamini–Hochberg
     trong họ phép kiểm của bài này. T18: hạt giống cố định, SHA-256 của kho hồ sơ và mã nguồn.
RF: huấn luyện n_jobs=-1 (cây độc lập, tất định theo random_state) nhưng DỰ BÁO n_jobs=1 để tổng qua
    các cây có thứ tự cố định → chạy lại trùng từng bit (khác run_p11_tasks.py, xem p11_determinism.txt).

Ghi ra out/reports/p11_tl.json, p11_tl.txt, p11_tl_config_log.json. Kho hồ sơ lưu ở
out/reports/_p11_pool.npz (lần đầu sinh bằng run_imbalance.build_pools, ~2,5 phút).
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import scipy
import sklearn
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

import run_imbalance as RI

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(PROJECT_DIR, "out", "reports")
POOL_NPZ = os.path.join(OUT_DIR, "_p11_pool.npz")

QUICK = "--quick" in sys.argv
SEED_TL = 20261100
N_REPS = int(os.environ.get("P11TL_REPS", "20"))
PREV = 0.02
N_EVAL = 50000
N_TRAIN = 5000
PI_S = 0.5
MODELS = ["LR", "RF"]
METHODS = ["N0", "RUS", "ROS", "SMOTE", "CW"]
BANDS = [0.0, 0.01, 0.05, 0.20, 1.0000001]
BAND_LABEL = ["<1%", "1-5%", "5-20%", ">=20%"]
CAPS = [0.02, 0.05, 0.10]
PTS = [0.02, 0.05, 0.10]
ASSUMED = [0.01, 0.02, 0.04]
N_AUDIT = [100, 200, 500]
PT_FINE = [round(0.005 * i, 3) for i in range(1, 41)]            # 0,5 % … 20 % — chỉ để vẽ hình
EPS = 1e-12


# ------------------------------------------------------------------ tiện ích
def logit(p):
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def sigm(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -60, 60)))


def prior_correct(p, pi, pi_s=PI_S):
    p = np.clip(np.asarray(p, dtype=float), 0.0, 1.0)
    a = p * (pi / pi_s)
    b = (1.0 - p) * ((1.0 - pi) / (1.0 - pi_s))
    return a / np.maximum(a + b, 1e-300)


def shift_to_mean(p, target_sum):
    """δ sao cho Σ sigm(logit p + δ) = target_sum (chia đôi 90 lần trên [−15, 15])."""
    z = logit(p)
    lo, hi = -15.0, 15.0
    for _ in range(90):
        mid = 0.5 * (lo + hi)
        if sigm(z + mid).sum() > target_sum:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def platt_fit(p, y):
    lr = LogisticRegression(max_iter=1000)
    lr.fit(logit(p)[:, None], y)
    return float(lr.coef_[0][0]), float(lr.intercept_[0])


def calib_slope(y, p):
    """Hệ số góc hiệu chỉnh: hồi quy logistic y ~ a + b·logit(p), Newton–Raphson không phạt,
    khởi đầu ở (0, 1) (mô hình hiệu chỉnh hoàn hảo) và chia đôi bước khi log-likelihood không tăng."""
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


def band_stats(y, q):
    idx = np.digitize(q, BANDS[1:-1], right=False)
    out = []
    for b in range(len(BAND_LABEL)):
        m = idx == b
        k = int(m.sum())
        out.append({"share": k / len(y), "obs": float(y[m].mean()) if k else float("nan"),
                    "mean_p": float(q[m].mean()) if k else float("nan")})
    return out


def capacity(y, s, frac):
    """Nhận đúng frac·n trẻ điểm cao nhất; nhóm trùng điểm ở ranh giới chia theo kỳ vọng."""
    n = len(y)
    K = int(round(frac * n))
    order = np.argsort(-s, kind="stable")
    ss, ys = s[order], y[order]
    v = ss[K - 1]
    above = ss > v
    tie = ss == v
    n_above = int(above.sum())
    tp_above = float(ys[above].sum())
    need = K - n_above
    tie_n = int(tie.sum())
    tp = tp_above + (need / tie_n) * float(ys[tie].sum())
    return {"ppv": tp / K, "sens": tp / max(float(y.sum()), 1.0),
            "tie_frac": (tie_n - need) / K if tie_n > need else 0.0}


def decision(y, q, pt):
    n = len(y)
    refer = q >= pt
    tp = float(np.sum(refer & (y == 1)))
    fp = float(np.sum(refer & (y == 0)))
    return {"nb": tp / n - fp / n * pt / (1 - pt), "refer": float(refer.mean()),
            "sens": tp / max(float(y.sum()), 1.0), "per100": 100 * tp / (tp + fp) if tp + fp > 0 else float("nan")}


def fit_predict(model, Xtr, ytr, w, X_list, seed):
    """Như RI.fit_predict nhưng RF dự báo n_jobs=1 (tái lập từng bit); trả danh sách xác suất."""
    if model == "LR":
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(Xtr, ytr, sample_weight=w)
    elif model == "RF":
        clf = RandomForestClassifier(n_estimators=200, min_samples_leaf=5, n_jobs=-1, random_state=seed)
        clf.fit(Xtr, ytr, sample_weight=w)
        clf.set_params(n_jobs=1)
    else:
        raise ValueError(model)
    return [clf.predict_proba(X)[:, 1] for X in X_list]


def draw_binom(pool_pos, pool_neg, n, prev, rng):
    k = int(rng.binomial(n, prev))
    ip = rng.choice(len(pool_pos), size=k, replace=False)
    ineg = rng.choice(len(pool_neg), size=n - k, replace=False)
    X = np.vstack([pool_pos[ip], pool_neg[ineg]])
    y = np.r_[np.ones(k, dtype=int), np.zeros(n - k, dtype=int)]
    perm = rng.permutation(n)
    return X[perm], y[perm]


def load_pools():
    if os.path.exists(POOL_NPZ):
        z = np.load(POOL_NPZ)
        P = {k: z[k] for k in ("dev_pos", "dev_neg", "test_pos", "test_neg")}
        print(f"  doc kho ho so tu {os.path.relpath(POOL_NPZ, PROJECT_DIR)}", flush=True)
    else:
        B = RI.build_pools()
        P = {k: B[k] for k in ("dev_pos", "dev_neg", "test_pos", "test_neg")}
        os.makedirs(OUT_DIR, exist_ok=True)
        np.savez_compressed(POOL_NPZ, **P)
        print(f"  da luu kho ho so vao {os.path.relpath(POOL_NPZ, PROJECT_DIR)}", flush=True)
    return P


def pool_hash(P):
    h = hashlib.sha256()
    for k in ("dev_pos", "dev_neg", "test_pos", "test_neg"):
        h.update(np.ascontiguousarray(P[k], dtype=np.float64).tobytes())
    return h.hexdigest()


def acc(store, key, val):
    store.setdefault(key, []).append(float(val))


def summ(store):
    out = {}
    for k, v in store.items():
        a = np.array(v, dtype=float)
        ok = a[~np.isnan(a)]
        out[k] = [float(ok.mean()) if len(ok) else float("nan"),
                  float(ok.std(ddof=1)) if len(ok) > 1 else 0.0, int(len(ok))]
    return out


def bh(p):
    return RI.bh_adjust(np.asarray(p, dtype=float))


# ------------------------------------------------------------------ chạy
def main() -> int:
    t0 = time.time()
    started = datetime.now().isoformat(timespec="seconds")
    print("=" * 78)
    print(f"P11 ban tam ly tri lieu — ty le {PREV:.0%}, {len(MODELS)} mo hinh x {len(METHODS)} cach, "
          f"{N_REPS} lan lap, tap danh gia {N_EVAL}")
    print("=" * 78, flush=True)
    P = load_pools()
    ph = pool_hash(P)
    # Quần thể tại chỗ cố định (đánh giá) + phần còn lại của kho TEST làm nguồn mẫu kiểm tra có nhãn
    rng0 = np.random.default_rng(SEED_TL)
    op, on = rng0.permutation(len(P["test_pos"])), rng0.permutation(len(P["test_neg"]))
    k_ev = int(round(N_EVAL * PREV))
    Xev = np.vstack([P["test_pos"][op[:k_ev]], P["test_neg"][on[:N_EVAL - k_ev]]])
    yev = np.r_[np.ones(k_ev, dtype=int), np.zeros(N_EVAL - k_ev, dtype=int)]
    A_pos, A_neg = P["test_pos"][op[k_ev:]], P["test_neg"][on[N_EVAL - k_ev:]]

    tl1, tl2, tl3, curves, diffs, raw_nb = {}, {}, {}, {}, {}, {}
    for rep in range(N_REPS):
        rng = np.random.default_rng(SEED_TL + 1000 * (rep + 1))
        Xtr, ytr = RI.draw(P["dev_pos"], P["dev_neg"], N_TRAIN, PREV, rng)
        pi_tr = float(ytr.mean())
        audits = {n: draw_binom(A_pos, A_neg, n, PREV, rng) for n in N_AUDIT}
        for model in MODELS:
            seed_m = SEED_TL + 31 * rep + 7 * MODELS.index(model)
            base = {}
            for meth in METHODS:
                Xr, yr, w = RI.resample(meth, Xtr, ytr, rng)
                preds = fit_predict(model, Xr, yr, w, [Xev] + [audits[n][0] for n in N_AUDIT], seed_m)
                p_ev, p_aud = preds[0], dict(zip(N_AUDIT, preds[1:]))
                head = f"{model}|{meth}"
                # ---- TL2a: năng lực (chỉ thứ hạng)
                for K in CAPS:
                    c = capacity(yev, p_ev, K)
                    for k_, v_ in c.items():
                        acc(tl2, f"{head}|cap|{K}|{k_}", v_)
                    if meth == "N0":
                        base[f"cap{K}"] = c["ppv"]
                    else:
                        acc(diffs, f"{head}|cap|{K}|ppv", c["ppv"] - base[f"cap{K}"])
                # ---- các phép sửa thang (TL3)
                corr = {"raw": p_ev,
                        "pc": prior_correct(p_ev, pi_tr) if meth != "N0" else p_ev}
                for a in ASSUMED:
                    d = shift_to_mean(p_ev, a * len(p_ev))
                    corr[f"mm_{a}"] = sigm(logit(p_ev) + d)
                    acc(tl3, f"{head}|mm_{a}|delta", d)
                for n in N_AUDIT:
                    Xa, ya = audits[n]
                    pa = p_aud[n]
                    d = shift_to_mean(pa, float(ya.sum()))
                    corr[f"icpt_{n}"] = sigm(logit(p_ev) + d)
                    acc(tl3, f"{head}|icpt_{n}|npos", ya.sum())
                    if len(np.unique(ya)) == 2:
                        b, a0 = platt_fit(pa, ya)
                        corr[f"platt_{n}"] = sigm(a0 + b * logit(p_ev))
                        acc(tl3, f"{head}|platt_{n}|neg_slope", float(b < 0))
                    else:
                        acc(tl3, f"{head}|platt_{n}|skipped", 1.0)
                for cn, q in corr.items():
                    k3 = f"{head}|{cn}"
                    acc(tl3, k3 + "|mean_p", q.mean())
                    acc(tl3, k3 + "|ece", RI.ece(yev, q))
                    acc(tl3, k3 + "|brier", RI.brier(yev, q))
                    acc(tl3, k3 + "|slope", calib_slope(yev, q))
                    for pt in PTS:
                        dd = decision(yev, q, pt)
                        for k_, v_ in dd.items():
                            acc(tl2, f"{head}|{cn}|{pt}|{k_}", v_)
                        if meth == "N0" and cn == "raw":
                            raw_nb[(model, pt)] = dd["nb"]
                        elif cn in ("raw", "pc", "mm_0.02"):
                            acc(diffs, f"{head}|{cn}|nb|{pt}", dd["nb"] - raw_nb[(model, pt)])
                    if cn in ("raw", "pc", "mm_0.02", "icpt_200"):
                        for b_, st in zip(BAND_LABEL, band_stats(yev, q)):
                            for k_, v_ in st.items():
                                acc(tl1, f"{head}|{cn}|{b_}|{k_}", v_)
                    if cn in ("raw", "pc", "mm_0.02"):
                        nbv, _, _ = RI.nb_curve_prob(yev, q, PT_FINE)
                        curves.setdefault(k3, []).append([float(x) for x in nbv])
        print(f"  lan lap {rep + 1}/{N_REPS} ({time.time() - t0:.0f}s)", flush=True)

    # ---- T17: kiểm định ghép cặp, BH trong họ
    tests = []
    for k, v in diffs.items():
        a = np.asarray(v, dtype=float)
        p = 1.0 if (len(a) < 3 or np.allclose(a, 0.0)) else float(stats.ttest_1samp(a, 0.0).pvalue)
        tests.append({"key": k, "effect": float(a.mean()), "sd": float(a.std(ddof=1)) if len(a) > 1 else 0.0,
                      "p_raw": p})
    q = bh([t["p_raw"] for t in tests])
    for t, qq in zip(tests, q):
        t["p_bh"] = float(qq)

    ref_all = {str(pt): float(PREV - (1 - PREV) * pt / (1 - pt)) for pt in PTS}
    out = {
        "quick": QUICK, "seed": SEED_TL, "n_reps": N_REPS, "prev": PREV, "n_eval": N_EVAL, "n_train": N_TRAIN,
        "n_eval_pos": int(yev.sum()), "audit_pool": {"pos": int(len(A_pos)), "neg": int(len(A_neg))},
        "pool_sha256": ph, "pool_sizes": {k: int(len(v)) for k, v in P.items()},
        "models": MODELS, "methods": METHODS, "bands": BAND_LABEL, "caps": CAPS, "pts": PTS,
        "assumed": ASSUMED, "n_audit": N_AUDIT, "pt_fine": PT_FINE, "ref_all": ref_all,
        "ref_all_fine": [float(PREV - (1 - PREV) * t / (1 - t)) for t in PT_FINE],
        "tl1": summ(tl1), "tl2": summ(tl2), "tl3": summ(tl3),
        "curves": {k: np.mean(np.asarray(v), axis=0).tolist() for k, v in curves.items()},
        "tests": tests, "n_tests": len(tests),
    }
    tag = "_quick" if QUICK else ""
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f"p11_tl{tag}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    write_txt(out, tag)
    files = ["src/run_p11_tl.py", "src/run_imbalance.py", "src/ts_simulate.py", "src/ts_features.py",
             "src/ts_fuzzy.py", "src/config.py", "src/data/questions.csv"]
    log = {"run_started": started, "command": "python src/run_p11_tl.py", "quick": QUICK,
           "seeds": {"SEED_TL": SEED_TL, "eval_split": "default_rng(SEED_TL)",
                     "rep": "default_rng(SEED_TL + 1000*(rep+1))", "model": "SEED_TL + 31*rep + 7*model_index",
                     "pool": "run_imbalance.SEED (20260829) / +1"},
           "design": {k: out[k] for k in ("prev", "n_eval", "n_train", "n_reps", "models", "methods", "caps",
                                          "pts", "assumed", "n_audit")},
           "n_tests_bh": len(tests), "pool_sha256": ph,
           "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                        "sklearn": sklearn.__version__, "platform": platform.platform()},
           "sha256": {f: hashlib.sha256(open(os.path.join(PROJECT_DIR, f), "rb").read()).hexdigest()
                      for f in files}}
    with open(os.path.join(OUT_DIR, f"p11_tl_config_log{tag}.json"), "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=1)
    print(f"Da ghi out/reports/p11_tl{tag}.json ({time.time() - t0:.0f}s)")
    return 0


def write_txt(o, tag):
    g = lambda d, k: d[k][0]
    L = [f"P11 ban tam ly tri lieu — {o['n_reps']} lan lap, ty le {o['prev']:.0%}, du lieu tong hop"]
    L.append("\nTL2a nang luc (so ca that / 100 luot danh gia | do nhay)")
    for m in o["models"]:
        for h in o["methods"]:
            L.append(f"  {m:3s} {h:6s} " + "  ".join(
                f"K={K:.0%}: {100 * g(o['tl2'], f'{m}|{h}|cap|{K}|ppv'):5.2f} | {g(o['tl2'], f'{m}|{h}|cap|{K}|sens'):.3f}"
                for K in o["caps"]))
    L.append("\nTL2b/TL3 (x.suat TB | ECE x1000 | he so goc | [p_t: ty le chuyen, NB x1000])")
    corrs = ["raw", "pc"] + [f"mm_{a}" for a in o["assumed"]] + [f"icpt_{n}" for n in o["n_audit"]] + \
            [f"platt_{n}" for n in o["n_audit"]]
    for m in o["models"]:
        for h in o["methods"]:
            for c in corrs:
                k = f"{m}|{h}|{c}"
                if k + "|mean_p" not in o["tl3"]:
                    continue
                L.append(f"  {m:3s} {h:6s} {c:10s} {g(o['tl3'], k + '|mean_p'):.4f} {1000 * g(o['tl3'], k + '|ece'):7.2f} "
                         f"{g(o['tl3'], k + '|slope'):6.2f}  " + "  ".join(
                             f"{pt:.0%}: {g(o['tl2'], f'{k}|{pt}|refer'):.3f} {1000 * g(o['tl2'], f'{k}|{pt}|nb'):6.2f}"
                             for pt in o["pts"]))
    L.append("\n  chuyen tat ca: " + "  ".join(f"{pt}: {1000 * v:.2f}" for pt, v in o["ref_all"].items()))
    L.append("\nTL1 dai nguy co (ty trong | ty le that /1000)")
    for m in o["models"]:
        for h in o["methods"]:
            for c in ("raw", "pc", "mm_0.02", "icpt_200"):
                k = f"{m}|{h}|{c}"
                L.append(f"  {m:3s} {h:6s} {c:9s} " + "  ".join(
                    f"{b}: {g(o['tl1'], f'{k}|{b}|share'):.3f} | {1000 * g(o['tl1'], f'{k}|{b}|obs'):6.1f}"
                    for b in o["bands"]))
    L.append(f"\nT17: {o['n_tests']} phep kiem, BH")
    for t in o["tests"]:
        L.append(f"  {t['key']:32s} {t['effect']:+.5f} ± {t['sd']:.5f}  p {t['p_raw']:.2e}  q {t['p_bh']:.2e}")
    with open(os.path.join(OUT_DIR, f"p11_tl{tag}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
