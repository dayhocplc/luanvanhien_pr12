# -*- coding: utf-8 -*-
"""
fig_p11_tl.py — ba hình cho bài P11 bản công nghệ hỗ trợ tâm lý trị liệu (đọc out/reports/p11_tl.json).

    .venv/Scripts/python.exe src/fig_p11_tl.py          # nhãn tiếng Việt → p11tl_fig1..3 (manuscript/P11_TL)
    .venv/Scripts/python.exe src/fig_p11_tl.py --en     # nhãn tiếng Anh  → p11tl_en_fig1..3 (manuscript/P11_TL_EN)

Hình 1 — Con số nguy cơ nói với gia đình (LR, tỷ lệ 2 %): tỷ trọng trẻ và tỷ lệ mắc thật mỗi dải,
         huấn luyện nguyên trạng / SMOTE / SMOTE rồi khớp trung bình.
Hình 2 — Dịch vụ theo năng lực: số ca thật trên 100 lượt đánh giá khi nhận K % trẻ điểm cao nhất.
Hình 3 — Đường cong quyết định (lợi ích ròng) của LR và RF: nguyên trạng, SMOTE thô, SMOTE đã sửa thang.
"""

from __future__ import annotations

import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

import figstyle as fs

plt = fs.plt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O = json.load(open(os.path.join(ROOT, "out", "reports", "p11_tl.json"), encoding="utf-8"))
EN = "--en" in sys.argv
MAN = os.path.join(ROOT, "manuscript", "P11_TL_EN" if EN else "P11_TL")
NAMES = [f"p11tl_{'en_' if EN else ''}fig{i}" for i in (1, 2, 3)]
BANDS = ["<1%", "1–5%", "5–20%", "≥20%"] if EN else ["dưới 1 %", "1–5 %", "5–20 %", "từ 20 %"]
L = {
    "N0raw": ("(a) Trained as collected", "(a) Huấn luyện nguyên trạng"),
    "SMraw": ("(b) Trained after SMOTE", "(b) Huấn luyện sau SMOTE"),
    "SMmm": ("(c) SMOTE + mean matching", "(c) SMOTE + khớp trung bình"),
    "kids": ("{s}%\ntrue {o}/1,000", "{s} % trẻ\nthật {o}/1 000"),
    "none": ("≈0%", "≈ 0 %"),
    "band": ("Risk band shown to the family", "Dải nguy cơ nói với gia đình"),
    "share": ("Share of screened children (%)", "Tỷ trọng trẻ được sàng lọc (%)"),
    "cap": ("Service capacity: {k}% of screened children", "Năng lực dịch vụ: {k} % số trẻ được sàng lọc"),
    "yield": ("True cases per 100 assessments", "Số ca thật trên 100 lượt đánh giá"),
    "base": ("assessing at random", "đánh giá ngẫu nhiên"),
    "meth": {"N0": ("as collected", "nguyên trạng"), "RUS": ("under-sampling", "lấy mẫu thiếu"),
             "ROS": ("over-sampling", "lấy mẫu thừa"), "SMOTE": ("SMOTE", "SMOTE"),
             "CW": ("class weights", "trọng số lớp")},
    "LR": ("logistic regression", "hồi quy logistic"), "RF": ("random forest", "rừng ngẫu nhiên"),
    "nobody": ("refer none", "không chuyển ai"), "all": ("refer all", "chuyển tất cả"),
    "c_N0": ("as collected", "nguyên trạng"), "c_SMraw": ("SMOTE, raw output", "SMOTE, đầu ra thô"),
    "c_SMmm": ("SMOTE + mean matching", "SMOTE + khớp trung bình"),
    "c_SMpc": ("SMOTE + prior correction", "SMOTE + hiệu chỉnh tiên nghiệm"),
    "pt": ("Referral threshold p$_t$ (%)", "Ngưỡng chuyển đánh giá p$_t$ (%)"),
    "nb": ("Net benefit × 1,000", "Lợi ích ròng × 1 000"),
}


def t(k, i=None):
    v = L[k] if i is None else L[k][i]
    return v[0 if EN else 1]


def vn(x, nd=1):
    s = f"{x:.{nd}f}"
    return s if EN else s.replace(".", ",")


def save(fig, name):
    os.makedirs(fs.FIG_DIR, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(fs.FIG_DIR, f"{name}.{ext}"), dpi=300)
    os.makedirs(MAN, exist_ok=True)
    shutil.copy(os.path.join(fs.FIG_DIR, f"{name}.png"), os.path.join(MAN, f"{name}.png"))
    plt.close(fig)


def hinh_1():
    t1 = O["tl1"]
    fig, axes = plt.subplots(1, 3, figsize=(7.6, 3.0), sharey=True)
    for ax, (key, meth, corr, col) in zip(axes, (("N0raw", "N0", "raw", fs.C["xanh"]),
                                                 ("SMraw", "SMOTE", "raw", fs.C["donhat"]),
                                                 ("SMmm", "SMOTE", "mm_0.02", fs.C["luc"]))):
        share = [t1[f"LR|{meth}|{corr}|{b}|share"][0] for b in O["bands"]]
        obs = [t1[f"LR|{meth}|{corr}|{b}|obs"][0] for b in O["bands"]]
        x = np.arange(4)
        ax.bar(x, [100 * s for s in share], width=0.62, color=col, edgecolor="white", linewidth=1.0)
        for i, (s, o) in enumerate(zip(share, obs)):
            if s >= 0.0005 and not np.isnan(o):
                ax.text(i, 100 * s + 2.5 + (9 if (s < 0.1 and i == 3) else 0),
                        t("kids").format(s=vn(100 * s), o=f"{1000 * o:.0f}"),
                        ha="center", va="bottom", fontsize=5.8, color="#222222")
            else:
                ax.text(i, 2.5, t("none"), ha="center", va="bottom", fontsize=6.3, color=fs.C["xam"])
        ax.set_xticks(x, BANDS, fontsize=7)
        ax.set_xlabel(t("band"), fontsize=8)
        ax.set_title(t(key), loc="left", fontsize=8.5)
        ax.set_ylim(0, 112)
    axes[0].set_ylabel(t("share"))
    fig.tight_layout()
    save(fig, NAMES[0])


def hinh_2():
    t2 = O["tl2"]
    meths = O["methods"]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), sharey=True)
    for ax, K in zip(axes, (0.05, 0.10)):
        w = 0.38
        for j, (model, col, hatch) in enumerate((("LR", fs.C["xanh"], ""), ("RF", fs.C["cam"], "//"))):
            mu = [100 * t2[f"{model}|{m}|cap|{K}|ppv"][0] for m in meths]
            sd = [100 * t2[f"{model}|{m}|cap|{K}|ppv"][1] for m in meths]
            xx = np.arange(len(meths)) + (j - 0.5) * w
            ax.bar(xx, mu, width=w, yerr=sd, color=col, hatch=hatch, edgecolor="white", capsize=2,
                   error_kw={"lw": 0.8}, label=t(model))
        ax.axhline(100 * O["prev"], color=fs.C["xam"], lw=1.0, ls="--", label=t("base"))
        ax.set_xticks(np.arange(len(meths)), [t("meth", m) for m in meths], rotation=25, ha="right", fontsize=7)
        ax.set_title(t("cap").format(k=f"{100 * K:.0f}"), loc="left", fontsize=8.5)
        ax.set_ylim(0, 10.5)
    axes[0].set_ylabel(t("yield"))
    axes[1].legend(loc="upper right", fontsize=7)
    fig.tight_layout()
    save(fig, NAMES[1])


def hinh_3():
    cur = O["curves"]
    x = 100 * np.array(O["pt_fine"])
    allnb = 1000 * np.array(O["ref_all_fine"])
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
    for ax, model in zip(axes, ("LR", "RF")):
        ax.axhline(0, color=fs.C["xam"], lw=1.0, label=t("nobody"))
        ax.plot(x, allnb, color=fs.C["xamnhat"], lw=2.4, ls="--", label=t("all"))
        ax.plot(x, 1000 * np.array(cur[f"{model}|N0|raw"]), color=fs.C["xanh"], lw=2.0, label=t("c_N0"))
        ax.plot(x, 1000 * np.array(cur[f"{model}|SMOTE|raw"]), color=fs.C["donhat"], lw=1.8, ls="-.",
                label=t("c_SMraw"))
        ax.plot(x, 1000 * np.array(cur[f"{model}|SMOTE|mm_0.02"]), color=fs.C["luc"], lw=1.6, ls=":",
                label=t("c_SMmm"))
        ax.plot(x, 1000 * np.array(cur[f"{model}|SMOTE|pc"]), color=fs.C["tim"], lw=1.4, ls=(0, (5, 2)),
                label=t("c_SMpc"))
        ax.set_ylim(-6, 16)
        ax.set_xlim(0, 20)
        ax.set_title(f"({'ab'[('LR', 'RF').index(model)]}) " + t(model).capitalize(), loc="left", fontsize=8.5)
        ax.set_xlabel(t("pt"))
    axes[0].set_ylabel(t("nb"))
    axes[1].legend(loc="upper right", fontsize=6.5)
    fig.tight_layout()
    save(fig, NAMES[2])


if __name__ == "__main__":
    fs.setup()
    hinh_1()
    hinh_2()
    hinh_3()
    print("Da ve", ", ".join(NAMES))
