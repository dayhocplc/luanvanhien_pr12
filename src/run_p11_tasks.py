# -*- coding: utf-8 -*-
"""
run_p11_tasks.py — Bản chạy CHÍNH THỨC của bài P11 (27/09/2026): T12 + T14 + T17 + T18
và hai thí nghiệm bổ sung cho bản tiếng Anh.

    .venv/Scripts/python.exe src/run_p11_tasks.py                 # ~30 phút CPU
    P11_REPS=2 P11_NTEST=5000 .venv/Scripts/python.exe src/run_p11_tasks.py --quick   # thử nhanh

Đầu ra: out/reports/p11_tasks.json (cùng lược đồ với imbalance.json + các khoá mới)
        out/reports/p11_config_log.json (T18: hạt giống, phiên bản, SHA-256)

SỬA SO VỚI src/run_imbalance.py (bản 28/08/2026, kết quả giữ ở imbalance_20260828.json)
---------------------------------------------------------------------------------------
LỖI: tập huấn luyện và tập hiệu chỉnh được rút ĐỘC LẬP từ cùng một kho DEV, nên trùng
nhau một phần (≈ n_calib/|kho| ≈ 8 % hồ sơ âm của tập hiệu chỉnh đã nằm trong tập huấn
luyện). Mô hình dự báo trên chính hồ sơ huấn luyện của nó (rõ nhất là Fuzzy k-NN: khoảng
cách 0 → điểm = nhãn của chính hồ sơ) nên điểm cắt và phép Platt khớp trên tập hiệu chỉnh
bị lệch. Bản này rút huấn luyện + hiệu chỉnh trong MỘT lần rút không hoàn lại → rời nhau.

BỔ SUNG
-------
E1 (hiệu chỉnh tiên nghiệm giải tích — Saerens 2002, Elkan 2001): sau khi tái lấy mẫu về
    tỷ lệ π_s = 0,5, đổi xác suất về tỷ lệ gốc π bằng công thức Bayes
        p' = p·π/π_s / [p·π/π_s + (1−p)(1−π)/(1−π_s)],
    không cần tập hiệu chỉnh. Công thức đúng khi mô hình ước lượng đúng P(y|x) dưới tỷ lệ
    π_s; nó cho biết phần nào của sai lệch hiệu chỉnh do tái lấy mẫu là "dịch tiên nghiệm"
    thuần tuý (sửa được bằng một phép tính) và phần nào là biến dạng hình dạng.
E2 (cỡ tập hiệu chỉnh cho dịch chuyển ngưỡng): điểm cắt tối đa hoá lợi ích ròng thực
    nghiệm chọn trên 250…8 000 hồ sơ; so với quy tắc cắm thẳng p ≥ p_t của mô hình nguyên
    trạng và với điểm cắt "tiên tri" chọn trên chính tập kiểm thử (cận trên).
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time
from datetime import datetime

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import scipy
import sklearn
from scipy import stats

import config as cfg
import run_imbalance as RI
from run_imbalance import (METHODS, MODELS, PREVS, PT_GRID, PT_MAIN, average_precision, best_cut_for_nb,
                           bh_adjust, brier, build_pools, ece, fit_predict, nb_at_cut, nb_curve_prob,
                           platt, resample, roc_auc)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(PROJECT_DIR, "out", "reports")

QUICK = "--quick" in sys.argv
SEED = RI.SEED                       # 20260829 — kho hồ sơ giữ nguyên như bản 28/08
SEED_RUN = 20260927                  # luồng rút mẫu / huấn luyện của bản chính thức
N_REPS = int(os.environ.get("P11_REPS", "20"))
N_TEST = int(os.environ.get("P11_NTEST", "50000"))
N_TRAIN = int(os.environ.get("P11_NTRAIN", "5000"))
N_CALIB = int(os.environ.get("P11_NCALIB", "2000"))
CALIB_SIZES = [250, 500, 1000, 2000, 4000, 8000]
N_CALIB_MAX = max(CALIB_SIZES)
PC_METHODS = ["RUS", "ROS", "SMOTE", "CW"]           # E1: có hiệu chỉnh tiên nghiệm
E2_MODELS = MODELS
PI_S = 0.5                                           # tỷ lệ sau tái lấy mẫu / trọng số lớp


def prior_correct(p, pi, pi_s=PI_S):
    p = np.clip(np.asarray(p, dtype=float), 0.0, 1.0)
    a = p * (pi / pi_s)
    b = (1.0 - p) * ((1.0 - pi) / (1.0 - pi_s))
    return a / np.maximum(a + b, 1e-300)


def draw_split(pool_pos, pool_neg, n_tr, n_ca, prev, rng):
    """Rút tập huấn luyện và kho hiệu chỉnh RỜI NHAU trong một lần rút không hoàn lại.

    Trả về (Xtr, ytr, Cpos, Cneg): kho hiệu chỉnh giữ riêng hai lớp theo thứ tự ngẫu nhiên,
    để các tập hiệu chỉnh cỡ s là các tiền tố lồng nhau, phân tầng theo đúng tỷ lệ prev."""
    k_tr, k_ca = int(round(n_tr * prev)), int(round(n_ca * prev))
    ip = rng.choice(len(pool_pos), size=k_tr + k_ca, replace=False)
    ineg = rng.choice(len(pool_neg), size=(n_tr - k_tr) + (n_ca - k_ca), replace=False)
    Xtr = np.vstack([pool_pos[ip[:k_tr]], pool_neg[ineg[:n_tr - k_tr]]])
    ytr = np.concatenate([np.ones(k_tr, dtype=int), np.zeros(n_tr - k_tr, dtype=int)])
    o = rng.permutation(n_tr)
    return Xtr[o], ytr[o], pool_pos[ip[k_tr:]], pool_neg[ineg[n_tr - k_tr:]]


def calib_subset(Cpos, Cneg, s, prev):
    k = int(round(s * prev))
    X = np.vstack([Cpos[:k], Cneg[:s - k]])
    y = np.concatenate([np.ones(k, dtype=int), np.zeros(s - k, dtype=int)])
    return X, y


def metrics(yte, p_te, nb_curve, tp, fp):
    flagged = tp + fp
    return {
        "pr_auc": average_precision(yte, p_te),
        "roc_auc": roc_auc(yte, p_te),
        "brier": brier(yte, p_te),
        "ece": ece(yte, p_te),
        "mean_p": float(np.mean(p_te)),
        "nb": float(nb_curve[I_MAIN]),
        "flag_rate": float(flagged / len(yte)),
        "nns": float(flagged / tp) if tp > 0 else float("nan"),
        "sens": float(tp / max(int(yte.sum()), 1)),
        "tp": float(tp), "fp": float(fp),
    }


I_MAIN = int(np.argmin(np.abs(PT_GRID - PT_MAIN)))


def prob_rule(yte, p_te):
    nbv, tpv, fpv = nb_curve_prob(yte, p_te, PT_GRID)
    return [float(v) for v in nbv], float(tpv[I_MAIN]), float(fpv[I_MAIN])


def cut_rule(yte, p_te, ysel, psel):
    curve, tp, fp = [], 0.0, 0.0
    for j, t in enumerate(PT_GRID):
        cut = best_cut_for_nb(ysel, psel, float(t))
        v, a, b = nb_at_cut(yte, p_te, cut, float(t))
        curve.append(float(v))
        if j == I_MAIN:
            tp, fp = a, b
    return curve, tp, fp


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main() -> int:
    t_all = time.time()
    started = datetime.now().isoformat(timespec="seconds")
    all_methods = METHODS + [f"{m}_PC" for m in PC_METHODS]
    print("=" * 78)
    print(f"P11 — BAN CHINH THUC{' (CHAY NHANH)' if QUICK else ''}: {len(all_methods)} cach x "
          f"{len(MODELS)} mo hinh x {len(PREVS)} ty le; TRAIN {N_TRAIN} · CALIB {N_CALIB} "
          f"(kho {N_CALIB_MAX}) · TEST {N_TEST} · {N_REPS} lan lap")
    print("=" * 78, flush=True)
    P = build_pools()

    cells, diffs, curves, ref, e2 = {}, {}, {}, {}, {}
    overlap_old = {}
    for prev in PREVS:
        Xte, yte = RI.draw(P["test_pos"], P["test_neg"], N_TEST, prev,
                           np.random.default_rng(SEED + 100 + int(prev * 10000)))
        pi = float(yte.mean())
        ref[prev] = {"pi": pi, "n_pos": int(yte.sum()),
                     "all": [float(pi - (1 - pi) * (t / (1 - t))) for t in PT_GRID],
                     "all_main": float(pi - (1 - pi) * (PT_MAIN / (1 - PT_MAIN)))}
        # Mức trùng lặp kỳ vọng của thiết kế cũ (rút độc lập): hồ sơ hiệu chỉnh đã nằm trong tập huấn luyện
        k_tr, k_ca = round(N_TRAIN * prev), round(N_CALIB * prev)
        overlap_old[prev] = {"pos": k_ca * k_tr / len(P["dev_pos"]),
                             "neg": (N_CALIB - k_ca) * (N_TRAIN - k_tr) / len(P["dev_neg"])}
        print(f"\n[prev = {prev:.0%}] TEST n = {len(yte)}, duong {int(yte.sum())}", flush=True)

        for rep in range(N_REPS):
            rng = np.random.default_rng(SEED_RUN + 1000 * rep + int(prev * 10000))
            Xtr, ytr, Cpos, Cneg = draw_split(P["dev_pos"], P["dev_neg"], N_TRAIN, N_CALIB_MAX, prev, rng)
            Xca, yca = calib_subset(Cpos, Cneg, N_CALIB, prev)
            pi_tr = float(ytr.mean())
            for model in MODELS:
                seed_m = SEED_RUN + 31 * rep + 7 * MODELS.index(model)
                cache = {}
                for meth in METHODS:
                    if meth == "TS":
                        p_te, p_ca = cache["N0"]
                        curve, tp, fp = cut_rule(yte, p_te, yca, p_ca)
                    else:
                        Xr, yr, w = resample(meth, Xtr, ytr, rng)
                        p_te = fit_predict(model, Xr, yr, w, Xte, seed_m)
                        p_ca = fit_predict(model, Xr, yr, w, Xca, seed_m)
                        if meth == "SMOTE_RC":
                            p_te, p_ca = platt(p_ca, yca, p_te), platt(p_ca, yca, p_ca)
                        if meth == "N0":
                            # E2: cùng mô hình N0, dự báo trên toàn kho hiệu chỉnh 8 000 hồ sơ
                            Xc_all = np.vstack([Cpos, Cneg])
                            yc_all = np.concatenate([np.ones(len(Cpos), int), np.zeros(len(Cneg), int)])
                            pc_all = fit_predict(model, Xr, yr, w, Xc_all, seed_m)
                            npos = len(Cpos)
                            slot = e2.setdefault((prev, model), {})
                            for s in CALIB_SIZES:
                                k = int(round(s * prev))
                                ysel = np.concatenate([yc_all[:k], yc_all[npos:npos + s - k]])
                                psel = np.concatenate([pc_all[:k], pc_all[npos:npos + s - k]])
                                cut = best_cut_for_nb(ysel, psel, PT_MAIN)
                                v, a, b = nb_at_cut(yte, p_te, cut, PT_MAIN)
                                slot.setdefault(f"ts_{s}", []).append(float(v))
                                slot.setdefault(f"flag_{s}", []).append(float((a + b) / len(yte)))
                            cut_or = best_cut_for_nb(yte, p_te, PT_MAIN)
                            slot.setdefault("oracle", []).append(float(nb_at_cut(yte, p_te, cut_or, PT_MAIN)[0]))
                            slot.setdefault("plugin", []).append(float(nb_at_cut(yte, p_te, PT_MAIN, PT_MAIN)[0]))
                        curve, tp, fp = prob_rule(yte, p_te)
                        if meth in PC_METHODS:
                            q_te = prior_correct(p_te, pi_tr)
                            c2, tp2, fp2 = prob_rule(yte, q_te)
                            rec2 = metrics(yte, q_te, c2, tp2, fp2)
                            key2 = (prev, model, f"{meth}_PC")
                            s2 = cells.setdefault(key2, {})
                            for k_, v_ in rec2.items():
                                s2.setdefault(k_, []).append(v_)
                            curves.setdefault(key2, []).append(c2)
                    cache[meth] = (p_te, p_ca)
                    rec = metrics(yte, p_te, curve, tp, fp)
                    key = (prev, model, meth)
                    slot = cells.setdefault(key, {})
                    for k_, v_ in rec.items():
                        slot.setdefault(k_, []).append(v_)
                    curves.setdefault(key, []).append(curve)

                base = cells[(prev, model, "N0")]
                for meth in all_methods:
                    if meth == "N0":
                        continue
                    cur = cells[(prev, model, meth)]
                    d = diffs.setdefault((prev, model, meth), {})
                    fam = ["nb"] if meth == "TS" else (["brier", "nb"] if meth.endswith("_PC")
                                                       else ["pr_auc", "brier", "nb"])
                    for k_ in fam:
                        d.setdefault(k_, []).append(cur[k_][-1] - base[k_][-1])
            print(f"    lan lap {rep + 1}/{N_REPS} ({time.time() - t_all:.0f}s)", flush=True)

    # ------------------------------------------------ T17: hai họ phép kiểm, BH riêng từng họ
    tests = []
    for family, keep in (("main", lambda m: not m.endswith("_PC")), ("prior_correction", lambda m: m.endswith("_PC"))):
        rows = []
        for (prev, model, meth), d in diffs.items():
            if not keep(meth):
                continue
            for k_, v in d.items():
                v = np.asarray(v, dtype=float)
                v = v[np.isfinite(v)]
                p = 1.0 if (len(v) < 3 or np.allclose(v, 0.0)) else float(stats.ttest_1samp(v, 0.0).pvalue)
                rows.append({"family": family, "prev": prev, "model": model, "method": meth, "metric": k_,
                             "effect": float(np.mean(v)), "sd": float(np.std(v, ddof=1)) if len(v) > 1 else 0.0,
                             "p_raw": p})
        q = bh_adjust(np.array([r["p_raw"] for r in rows]))
        for r, qq in zip(rows, q):
            r["p_bh"] = float(qq)
        tests += rows
    n_main = sum(1 for t in tests if t["family"] == "main")
    print(f"\nT17 — ho chinh: {n_main} phep kiem; ho hieu chinh tien nghiem: {len(tests) - n_main}")

    def ms(v):
        v = np.asarray(v, dtype=float)
        return [float(np.nanmean(v)), float(np.nanstd(v, ddof=1)) if len(v) > 1 else 0.0]

    out = {
        "quick": QUICK, "seed_pool": SEED, "seed_run": SEED_RUN, "n_reps": N_REPS, "n_test": N_TEST,
        "n_train": N_TRAIN, "n_calib": N_CALIB, "calib_sizes": CALIB_SIZES, "prevs": PREVS,
        "pt_main": PT_MAIN, "pt_grid": [float(t) for t in PT_GRID], "i_main": I_MAIN,
        "methods": METHODS, "pc_methods": PC_METHODS, "all_methods": all_methods,
        "method_label": RI.METHOD_LABEL, "models": MODELS, "model_label": RI.MODEL_LABEL,
        "n_cells": len(METHODS) * len(MODELS) * len(PREVS),
        "n_tests": n_main, "n_tests_pc": len(tests) - n_main,
        "pool": {k: P[k] for k in ("n_pos_raw", "n_neg_raw", "n_pos_kept", "n_neg_kept")},
        "dev_pool": {"pos": int(len(P["dev_pos"])), "neg": int(len(P["dev_neg"]))},
        "test_pool": {"pos": int(len(P["test_pos"])), "neg": int(len(P["test_neg"]))},
        "overlap_old_design": {f"{k}": v for k, v in overlap_old.items()},
        "ref": {f"{k}": v for k, v in ref.items()},
        "cells": {f"{p}|{m}|{h}": {k: ms(v) for k, v in c.items()} for (p, m, h), c in cells.items()},
        "per_rep": {f"{p}|{m}|{h}": {k: [float(x) for x in c[k]] for k in ("pr_auc", "brier", "nb", "mean_p")}
                    for (p, m, h), c in cells.items()},
        "curves": {f"{p}|{m}|{h}": np.mean(np.asarray(v), axis=0).tolist() for (p, m, h), v in curves.items()},
        "calib_size": {f"{p}|{m}": {k: ms(v) for k, v in c.items()} for (p, m), c in e2.items()},
        "calib_size_per_rep": {f"{p}|{m}": c for (p, m), c in e2.items()},
        "tests": tests,
        "runtime_s": time.time() - t_all,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    tag = "_quick" if QUICK else ""
    with open(os.path.join(OUT_DIR, f"p11_tasks{tag}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)

    # ------------------------------------------------ T18: nhật ký cấu hình
    files = ["src/run_p11_tasks.py", "src/run_imbalance.py", "src/ts_simulate.py", "src/ts_features.py",
             "src/ts_fuzzy.py", "src/config.py", "src/data/questions.csv"]
    log = {
        "run_started": started, "runtime_s": out["runtime_s"], "quick": QUICK,
        "command": "python src/run_p11_tasks.py",
        "seeds": {"pool_generator_pos": SEED, "pool_generator_neg": SEED + 1,
                  "test_draw": "SEED + 100 + int(prev*10000)",
                  "train_calib_draw": "SEED_RUN + 1000*rep + int(prev*10000)",
                  "model_seed (RF, FCM)": "SEED_RUN + 31*rep + 7*model_index",
                  "SEED": SEED, "SEED_RUN": SEED_RUN},
        "design": {"methods": METHODS, "prior_corrected": PC_METHODS, "models": MODELS, "prevalences": PREVS,
                   "n_reps": N_REPS, "n_train": N_TRAIN, "n_calib": N_CALIB, "n_test": N_TEST,
                   "calib_sizes_E2": CALIB_SIZES, "pt_main": PT_MAIN,
                   "pt_grid": [float(PT_GRID[0]), float(PT_GRID[-1]), len(PT_GRID)],
                   "n_configurations": len(all_methods) * len(MODELS) * len(PREVS),
                   "n_tests_main": n_main, "n_tests_prior_correction": len(tests) - n_main,
                   "multiplicity": "Benjamini–Hochberg, FDR 0.05, separately within each family",
                   "rf": {"n_estimators": 200, "min_samples_leaf": 5},
                   "lr": {"C": 1.0, "max_iter": 2000}, "smote_k": 5},
        "config": {"SHAPLEY": {d: cfg.SHAPLEY[d] for d in RI.DOMS}, "FKNN_K": cfg.FKNN_K, "FKNN_M": cfg.FKNN_M,
                   "FCM_C": cfg.FCM_C, "FCM_M": cfg.FCM_M, "FCM_MAX_ITER": cfg.FCM_MAX_ITER, "FCM_TOL": cfg.FCM_TOL,
                   "FCM_MIN_LABELED_PER_CLUSTER": cfg.FCM_MIN_LABELED_PER_CLUSTER,
                   "FUSION_WEIGHTS": dict(cfg.FUSION_WEIGHTS)},
        "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                     "sklearn": sklearn.__version__, "platform": platform.platform()},
        "sha256": {f: sha(os.path.join(PROJECT_DIR, f)) for f in files},
    }
    with open(os.path.join(OUT_DIR, f"p11_config_log{tag}.json"), "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=1)
    print(f"Da ghi out/reports/p11_tasks{tag}.json va p11_config_log{tag}.json ({time.time() - t_all:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
