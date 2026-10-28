# -*- coding: utf-8 -*-
"""Dựng bản thảo Bài 11 — góc nhìn công nghệ hỗ trợ tâm lý trị liệu, dữ liệu tổng hợp, APA 7, HAI NGÔN NGỮ.

    .venv/Scripts/python.exe manuscript/P11_TL/build_p11_tl.py [--lang vi|en] [--check-doi]

  --lang vi (mặc định): manuscript/P11_TL/P11_TL_src.md        → P11_TL.md        → P11_TL_manuscript.docx
  --lang en           : manuscript/P11_TL_EN/P11_TL_EN_src.md  → P11_TL_EN.md     → P11_TL_EN_manuscript.docx

Nguồn số liệu: out/reports/p11_tl.json (TL1–TL3), p11_tasks.json (lưới chính), p11_tool_demo.json (công cụ).
Tự kiểm: manuscript/P11_TL/p11_tl_kiem_tra.py [--lang vi|en].

Cú pháp ô (mọi con số trong bài phải đi qua đây, không gõ tay):
  {{G:prev|model|method|metric|fmt}}   ô lưới chính p11_tasks.json → cells (trung bình qua lần lặp)
  {{T1:key|fmt}} {{T2:key|fmt}} {{T3:key|fmt}}   p11_tl.json → tl1 / tl2 / tl3 (trung bình)
  {{T2SD:key|fmt}} {{T3SD:key|fmt}}   độ lệch chuẩn qua các lần lặp
  {{TÊN}}                              đại lượng dẫn xuất trong build_subs()
  fmt: k0/k1/k2 = ×1000; c1/c2 = ×100; d1..d4 = số thập phân; p0/p1 = phần trăm; n = số nguyên;
       thêm + ở cuối để in dấu dương.
Trích dẫn: [@a; @b] → (Tác giả, năm; …); {@a} → Tác giả (năm).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
REP = os.path.join(ROOT, "out", "reports")
PANDOC = os.environ.get("PANDOC") or os.path.expandvars(r"%LOCALAPPDATA%\Pandoc\pandoc.exe")
if not os.path.exists(PANDOC):
    PANDOC = "pandoc"
LANG = "en" if ("--lang" in sys.argv and sys.argv[sys.argv.index("--lang") + 1] == "en") else "vi"
EN = LANG == "en"
OUTDIR = os.path.join(ROOT, "manuscript", "P11_TL_EN") if EN else HERE
BASE = "P11_TL_EN" if EN else "P11_TL"


def load(name):
    return json.load(open(os.path.join(REP, name), encoding="utf-8"))


TL = load("p11_tl.json")
G = load("p11_tasks.json")
DEMO = load("p11_tool_demo.json")

# ------------------------------------------------------------------ tài liệu tham khảo (APA 7)
# khoá -> (tác giả trong trích dẫn, năm, mục danh mục, DOI hoặc None). {etal} / {and} đổi theo ngôn ngữ.
REFS = {
    "aishworiya2023": ("Aishworiya {etal}", "2023", "Aishworiya, R., Ma, V. K., Stewart, S., Hagerman, R., & Feldman, H. M. (2023). Meta-analysis of the Modified Checklist for Autism in Toddlers, Revised/Follow-up for screening. *Pediatrics, 151*(6), e2022059393.", "10.1542/peds.2022-059393"),
    "ancker2017": ("Ancker {etal}", "2017", "Ancker, J. S., Edwards, A., Nosal, S., Hauser, D., Mauer, E., Kaushal, R., & the HITEC Investigators. (2017). Effects of workload, work complexity, and repeated alerts on alert fatigue in a clinical decision support system. *BMC Medical Informatics and Decision Making, 17*, 36.", "10.1186/s12911-017-0430-8"),
    "benjamini1995": ("Benjamini {and} Hochberg", "1995", "Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B (Methodological), 57*(1), 289–300.", "10.1111/j.2517-6161.1995.tb02031.x"),
    "breiman2001": ("Breiman", "2001", "Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5–32.", "10.1023/A:1010933404324"),
    "brier1950": ("Brier", "1950", "Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. *Monthly Weather Review, 78*(1), 1–3.", "10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2"),
    "byt2021": ("{moh}", "2021", "{mohfull}", None),
    "carriero2025": ("Carriero {etal}", "2025", "Carriero, A., Luijken, K., de Hond, A., Moons, K. G. M., van Calster, B., & van Smeden, M. (2025). The harms of class imbalance corrections for machine learning based prediction models: A simulation study. *Statistics in Medicine, 44*(3–4), e10320.", "10.1002/sim.10320"),
    "chawla2002": ("Chawla {etal}", "2002", "Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic minority over-sampling technique. *Journal of Artificial Intelligence Research, 16*, 321–357.", "10.1613/jair.953"),
    "collins2024": ("Collins {etal}", "2024", "Collins, G. S., Moons, K. G. M., Dhiman, P., Riley, R. D., Beam, A. L., Van Calster, B., Ghassemi, M., Liu, X., Reitsma, J. B., van Smeden, M., Boulesteix, A.-L., Camaradou, J. C., Celi, L. A., Denaxas, S., Denniston, A. K., Glocker, B., Golub, R. M., Harvey, H., Heinze, G., … Logullo, P. (2024). TRIPOD+AI statement: Updated guidance for reporting clinical prediction models that use regression or machine learning methods. *BMJ, 385*, e078378.", "10.1136/bmj-2023-078378"),
    "dalpozzolo2015": ("Dal Pozzolo {etal}", "2015", "Dal Pozzolo, A., Caelen, O., Johnson, R. A., & Bontempi, G. (2015). Calibrating probability with undersampling for unbalanced classification. In *2015 IEEE Symposium Series on Computational Intelligence* (pp. 159–166). IEEE.", "10.1109/SSCI.2015.33"),
    "elkan2001": ("Elkan", "2001", "Elkan, C. (2001). The foundations of cost-sensitive learning. In *Proceedings of the Seventeenth International Joint Conference on Artificial Intelligence* (pp. 973–978). Morgan Kaufmann.", None),
    "fernandez2018": ("Fernández {etal}", "2018", "Fernández, A., García, S., Herrera, F., & Chawla, N. V. (2018). SMOTE for learning from imbalanced data: Progress and challenges, marking the 15-year anniversary. *Journal of Artificial Intelligence Research, 61*, 863–905.", "10.1613/jair.1.11192"),
    "gigerenzer1995": ("Gigerenzer {and} Hoffrage", "1995", "Gigerenzer, G., & Hoffrage, U. (1995). How to improve Bayesian reasoning without instruction: Frequency formats. *Psychological Review, 102*(4), 684–704.", "10.1037/0033-295X.102.4.684"),
    "grove2000": ("Grove {etal}", "2000", "Grove, W. M., Zald, D. H., Lebow, B. S., Snitz, B. E., & Nelson, C. (2000). Clinical versus mechanical prediction: A meta-analysis. *Psychological Assessment, 12*(1), 19–30.", "10.1037/1040-3590.12.1.19"),
    "he2009": ("He {and} Garcia", "2009", "He, H., & Garcia, E. A. (2009). Learning from imbalanced data. *IEEE Transactions on Knowledge and Data Engineering, 21*(9), 1263–1284.", "10.1109/TKDE.2008.239"),
    "hyman2020": ("Hyman {etal}", "2020", "Hyman, S. L., Levy, S. E., Myers, S. M., & Council on Children with Disabilities, Section on Developmental and Behavioral Pediatrics. (2020). Identification, evaluation, and management of children with autism spectrum disorder. *Pediatrics, 145*(1), e20193447.", "10.1542/peds.2019-3447"),
    "janssen2008": ("Janssen {etal}", "2008", "Janssen, K. J. M., Moons, K. G. M., Kalkman, C. J., Grobbee, D. E., & Vergouwe, Y. (2008). Updating methods improved the performance of a clinical prediction model in new patients. *Journal of Clinical Epidemiology, 61*(1), 76–86.", "10.1016/j.jclinepi.2007.04.018"),
    "lewis2019": ("Lewis {etal}", "2019", "Lewis, C. C., Boyd, M., Puspitasari, A., Navarro, E., Howard, J., Kassab, H., Hoffman, M., Scott, K., Lyon, A., Douglas, S., Simon, G., & Kroenke, K. (2019). Implementing measurement-based care in behavioral health: A review. *JAMA Psychiatry, 76*(3), 324–335.", "10.1001/jamapsychiatry.2018.3329"),
    "morris2019": ("Morris {etal}", "2019", "Morris, T. P., White, I. R., & Crowther, M. J. (2019). Using simulation studies to evaluate statistical methods. *Statistics in Medicine, 38*(11), 2074–2102.", "10.1002/sim.8086"),
    "nguyen2026": ("{nguyen}", "2026", "{nguyen}, D. H. (2026). *Mô hình lai luật – học máy với đầu ra mờ hỗ trợ sàng lọc sớm nguy cơ rối loạn phổ tự kỷ ở trẻ 0–36 tháng*{tr_n} [{thesis}]. {lhu}.", None),
    "nhom2026en": ("{author}", "2026a", "{author}. (2026a). *Resampling or threshold moving? Class imbalance, calibration and decision curves for developmental screening at community prevalence — A simulation study* [{submitted}].", None),
    "nhom2026vn": ("{author}", "2026b", "{author}. (2026b). *Tái lấy mẫu hay dịch chuyển ngưỡng: Xử lý mất cân bằng lớp trong sàng lọc phát triển ở tỷ lệ hiện mắc cộng đồng*{tr_b} [{submitted}].", None),
    "nhom2026p9": ("{author}", "2026c", "{author}. (2026c). *Con số nguy cơ trên màn hình có nghĩa là gì? Hiệu chỉnh xác suất để công cụ số hỗ trợ nhà tâm lý lâm sàng truyền đạt nguy cơ và quyết định chuyển đánh giá trong sàng lọc phát triển*{tr_c} [{submitted}].", None),
    "robins2014": ("Robins {etal}", "2014", "Robins, D. L., Casagrande, K., Barton, M., Chen, C.-M. A., Dumont-Mathieu, T., & Fein, D. (2014). Validation of the Modified Checklist for Autism in Toddlers, Revised with Follow-up (M-CHAT-R/F). *Pediatrics, 133*(1), 37–45.", "10.1542/peds.2013-1813"),
    "saerens2002": ("Saerens {etal}", "2002", "Saerens, M., Latinne, P., & Decaestecker, C. (2002). Adjusting the outputs of a classifier to new a priori probabilities: A simple procedure. *Neural Computation, 14*(1), 21–41.", "10.1162/089976602753284446"),
    "spiegelhalter2017": ("Spiegelhalter", "2017", "Spiegelhalter, D. (2017). Risk and uncertainty communication. *Annual Review of Statistics and Its Application, 4*, 31–60.", "10.1146/annurev-statistics-010814-020148"),
    "steyerberg2004": ("Steyerberg {etal}", "2004", "Steyerberg, E. W., Borsboom, G. J. J. M., van Houwelingen, H. C., Eijkemans, M. J. C., & Habbema, J. D. F. (2004). Validation and updating of predictive logistic regression models: A study on sample size and shrinkage. *Statistics in Medicine, 23*(16), 2567–2586.", "10.1002/sim.1844"),
    "sutton2020": ("Sutton {etal}", "2020", "Sutton, R. T., Pincock, D., Baumgart, D. C., Sadowski, D. C., Fedorak, R. N., & Kroeker, K. I. (2020). An overview of clinical decision support systems: Benefits, risks, and strategies for success. *npj Digital Medicine, 3*, 17.", "10.1038/s41746-020-0221-y"),
    "torous2021": ("Torous {etal}", "2021", "Torous, J., Bucci, S., Bell, I. H., Kessing, L. V., Faurholt-Jepsen, M., Whelan, P., Carvalho, A. F., Keshavan, M., Linardon, J., & Firth, J. (2021). The growing field of digital psychiatry: Current evidence and the future of apps, social media, chatbots, and virtual reality. *World Psychiatry, 20*(3), 318–335.", "10.1002/wps.20883"),
    "vancalster2016": ("Van Calster {etal}", "2016", "Van Calster, B., Nieboer, D., Vergouwe, Y., De Cock, B., Pencina, M. J., & Steyerberg, E. W. (2016). A calibration hierarchy for risk models was defined: From utopia to empirical data. *Journal of Clinical Epidemiology, 74*, 167–176.", "10.1016/j.jclinepi.2015.12.005"),
    "vancalster2019": ("Van Calster {etal}", "2019", "Van Calster, B., McLernon, D. J., van Smeden, M., Wynants, L., & Steyerberg, E. W. (2019). Calibration: The Achilles heel of predictive analytics. *BMC Medicine, 17*, 230.", "10.1186/s12916-019-1466-7"),
    "vandengoorbergh2022": ("van den Goorbergh {etal}", "2022", "van den Goorbergh, R., van Smeden, M., Timmerman, D., & Van Calster, B. (2022). The harm of class imbalance corrections for risk prediction models: Illustration and simulation using logistic regression. *Journal of the American Medical Informatics Association, 29*(9), 1525–1534.", "10.1093/jamia/ocac093"),
    "vickers2006": ("Vickers {and} Elkin", "2006", "Vickers, A. J., & Elkin, E. B. (2006). Decision curve analysis: A novel method for evaluating prediction models. *Medical Decision Making, 26*(6), 565–574.", "10.1177/0272989X06295361"),
    "vickers2016": ("Vickers {etal}", "2016", "Vickers, A. J., Van Calster, B., & Steyerberg, E. W. (2016). Net benefit approaches to the evaluation of prediction models, molecular markers, and diagnostic tests. *BMJ, 352*, i6.", "10.1136/bmj.i6"),
    "vo2026": ("Vo {etal}", "2026", "Vo, T. V., Nguyen, P. M., Nguyen, D. N., Nguyen, T. V., Thai, D. M., Ly, H. H. V., & Luu, T. N. N. (2026). Machine learning–assisted autism risk stratification in toddlers using the Vietnamese M-CHAT-R and perinatal predictors: A cross-sectional study in Vietnam. *Journal of Autism and Developmental Disorders*. {aop}.", "10.1007/s10803-026-07227-1"),
    "wynants2019": ("Wynants {etal}", "2019", "Wynants, L., van Smeden, M., McLernon, D. J., Timmerman, D., Steyerberg, E. W., & Van Calster, B. (2019). Three myths about risk thresholds for prediction models. *BMC Medicine, 17*, 192.", "10.1186/s12916-019-1425-3"),
    "zeidan2022": ("Zeidan {etal}", "2022", "Zeidan, J., Fombonne, E., Scorah, J., Ibrahim, A., Durkin, M. S., Saxena, S., Yusuf, A., Shih, A., & Elsabbagh, M. (2022). Global prevalence of autism: A systematic review update. *Autism Research, 15*(5), 778–790.", "10.1002/aur.2696"),
    "zipkin2014": ("Zipkin {etal}", "2014", "Zipkin, D. A., Umscheid, C. A., Keating, N. L., Allen, E., Aung, K., Beyth, R., Kaatz, S., Mann, D. M., Sussman, J. B., Korenstein, D., Schardt, C., Nagi, A., Sloane, R., & Feldstein, D. A. (2014). Evidence-based risk communication: A systematic review. *Annals of Internal Medicine, 161*(4), 270–280.", "10.7326/M14-0295"),
}
WORDS = {
    "etal": ("và cs.", "et al."), "and": ("và", "&"), "author": ("[Tác giả]", "[Author]"),
    "submitted": ("Bản thảo gửi đăng", "Manuscript submitted for publication"),
    "thesis": ("Luận văn thạc sĩ", "Master's thesis"), "aop": ("Xuất bản trực tuyến trước", "Advance online publication"),
    "moh": ("Bộ Y tế", "Ministry of Health of Viet Nam"), "nguyen": ("Nguyễn", "Nguyen"),
    "lhu": ("Trường Đại học Lạc Hồng", "Lac Hong University"),
    "tr_b": ("", " [Resampling or threshold moving: Handling class imbalance in developmental screening at community "
                 "prevalence]"),
    "tr_c": ("", " [What does the risk number on the screen mean? Probability calibration so that digital tools can "
                 "support clinical psychologists in communicating risk and deciding on referral in developmental "
                 "screening]"),
    "tr_n": ("", " [A hybrid rule-based/machine-learning model with fuzzy outputs to support early screening for autism "
                 "spectrum disorder risk in children aged 0–36 months]"),
    "mohfull": ("Bộ Y tế. (2021). *Quyết định số 2254/QĐ-BYT ngày 07/5/2021 về việc ban hành “Bộ công cụ Phát hiện "
                "sớm rối loạn phổ tự kỷ ở trẻ em”*. Hà Nội.",
                "Ministry of Health of Viet Nam. (2021). *Decision No. 2254/QĐ-BYT of 7 May 2021 promulgating the "
                "toolkit for early detection of autism spectrum disorder in children* [in Vietnamese]. Hanoi."),
}
FAMILY_ALIAS = {"hyman2020": "Hyman", "fernandez2018": "Fern", "he2009": "He", "vo2026": "Vo", "vandengoorbergh2022": "Goorbergh", "dalpozzolo2015": "Pozzolo",
                "carriero2025": "Carriero", "vancalster2016": "Calster", "vancalster2019": "Calster"}


def w(key):
    return WORDS[key][1 if EN else 0]


def fill_words(s):
    return re.sub(r"\{(\w+)\}", lambda m: w(m.group(1)) if m.group(1) in WORDS else m.group(0), s)


# ------------------------------------------------------------------ định dạng số
def fnum(x, nd=2, sign=False):
    s = f"{x:.{nd}f}"
    if s.startswith("-") and float(s) == 0:
        s = s[1:]
    if sign and not s.startswith("-"):
        s = "+" + s
    neg = s[:1] in "+-"
    head, body = (s[0], s[1:]) if neg else ("", s)
    ip, _, dp = body.partition(".")
    if len(ip) > 3:
        ip = f"{int(ip):,}"
    if EN:
        head = head.replace("-", "−")
        return head + ip + ("." + dp if dp else "")
    ip = ip.replace(",", " ")
    return head.replace("-", "−") + ip + ("," + dp if dp else "")


def pct(x, nd=1, sign=False):
    return fnum(100 * x, nd, sign) + ("%" if EN else " %")


def fmt(x, spec):
    sign = spec.endswith("+")
    spec = spec.rstrip("+")
    if spec == "n":
        return fnum(round(x), 0, sign)
    kind, nd = spec[0], int(spec[1:])
    if kind == "k":
        return fnum(1000 * x, nd, sign)
    if kind == "d":
        return fnum(x, nd, sign)
    if kind == "p":
        return pct(x, nd, sign)
    if kind == "x":
        return fnum(x, nd, sign)
    if kind == "c":                                   # số trên 100 (ca thật / 100 lượt đánh giá)
        return fnum(100 * x, nd, sign)
    raise ValueError(spec)


def gcell(prev, model, meth, metric):
    return G["cells"][f"{prev}|{model}|{meth}"][metric][0]


def T(store, key, i=0):
    return TL[store][key][i]


def token(expr, subs):
    if ":" not in expr:
        if expr not in subs:
            raise SystemExit(f"ô không có giá trị: {expr}")
        return subs[expr]
    kind, rest = expr.split(":", 1)
    parts = rest.split("|")
    spec = parts[-1]
    if kind == "G":
        v = gcell(*parts[:4])
    elif kind in ("T1", "T2", "T3"):
        v = T("tl" + kind[1], "|".join(parts[:-1]))
    elif kind in ("T2SD", "T3SD"):
        v = T("tl" + kind[1], "|".join(parts[:-1]), 1)
    else:
        raise SystemExit(f"loại ô lạ: {expr}")
    return fmt(v, spec)


def md_table(header, rows, align):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(align) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def main_tests(metric, methods=("RUS", "ROS", "SMOTE", "CW")):
    return [t for t in G["tests"] if t["family"] == "main" and t["metric"] == metric and t["method"] in methods]


def tl_test(key):
    return next(t for t in TL["tests"] if t["key"] == key)


# ------------------------------------------------------------------ đại lượng dẫn xuất
def build_subs():
    S = {}
    pool = G["pool"]
    S["POOL_POS_RAW"], S["POOL_NEG_RAW"] = fnum(pool["n_pos_raw"], 0), fnum(pool["n_neg_raw"], 0)
    S["POOL_POS"], S["POOL_NEG"] = fnum(pool["n_pos_kept"], 0), fnum(pool["n_neg_kept"], 0)
    S["DEV_POS"], S["DEV_NEG"] = fnum(G["dev_pool"]["pos"], 0), fnum(G["dev_pool"]["neg"], 0)
    S["NREP"], S["NEVAL"], S["NTRAIN"] = str(TL["n_reps"]), fnum(TL["n_eval"], 0), fnum(TL["n_train"], 0)
    S["NEVAL_POS"] = fnum(TL["n_eval_pos"], 0)
    S["AUD_POS"], S["AUD_NEG"] = fnum(TL["audit_pool"]["pos"], 0), fnum(TL["audit_pool"]["neg"], 0)
    S["NTESTS_TL"] = str(TL["n_tests"])
    S["G_NREP"], S["G_NTEST"] = str(G["n_reps"]), fnum(G["n_test"], 0)
    S["G_NCONF"] = str(len(G["all_methods"]) * len(G["models"]) * len(G["prevs"]))
    S["G_NTESTS"], S["G_NTESTS_PC"] = str(G["n_tests"]), str(G["n_tests_pc"])
    S["POOLSHA"] = TL["pool_sha256"][:12]
    # lưới chính
    b = main_tests("brier")
    S["G_BRIER_WORSE"] = f"{sum(t['effect'] > 0 and t['p_bh'] < 0.05 for t in b)}/{len(b)}"
    pr = main_tests("pr_auc")
    up = [t for t in pr if t["effect"] > 0 and t["p_bh"] < 0.05]
    S["G_PR_UP"] = f"{len(up)}/{len(pr)}"
    S["G_PR_UP_OK"] = "1" if all(t["model"] == "FKNN" or (t["model"] == "RF" and t["method"] == "RUS") for t in up) else "0"
    S["G_PR_DOWN"] = str(sum(t["effect"] < 0 and t["p_bh"] < 0.05 for t in pr))
    S["G_PR_UP_MAX"] = fnum(1000 * max(t["effect"] for t in up), 1)
    nb = main_tests("nb")
    S["G_NB_UP"] = str(sum(t["effect"] > 0 and t["p_bh"] < 0.05 for t in nb))
    S["G_NB_DOWN"] = str(sum(t["effect"] < 0 and t["p_bh"] < 0.05 for t in nb))
    S["G_NB_N"] = str(len(nb))
    # TL1 — thổi phồng
    for m in ("LR", "RF"):
        for h in ("RUS", "ROS", "SMOTE", "CW"):
            S[f"INFL_{m}_{h}"] = fnum(T("tl3", f"{m}|{h}|raw|mean_p") / TL["prev"], 1)
    S["LR_SM_HI_1000"] = fnum(1000 * T("tl1", "LR|SMOTE|raw|>=20%|share"), 0)
    # TL2a — năng lực: tỷ lệ so với đánh giá ngẫu nhiên
    for m in ("LR", "RF"):
        for K in TL["caps"]:
            S[f"LIFT_{m}_{int(K * 100)}"] = fnum(T("tl2", f"{m}|N0|cap|{K}|ppv") / TL["prev"], 1)
    rf_drop = [T("tl2", f"RF|N0|cap|0.05|ppv") - T("tl2", f"RF|{h}|cap|0.05|ppv") for h in ("ROS", "SMOTE", "CW")]
    S["RF_CAP5_LOSS_MIN"], S["RF_CAP5_LOSS_MAX"] = fnum(100 * min(rf_drop), 1), fnum(100 * max(rf_drop), 1)
    S["RF_CAP5_MISSED"] = fnum(10000 * TL["prev"] * (T("tl2", "RF|N0|cap|0.05|sens") -
                                                     T("tl2", "RF|SMOTE|cap|0.05|sens")), 0)
    lr_q = [tl_test(f"LR|{h}|cap|{K}|ppv")["p_bh"] for h in ("ROS", "SMOTE", "CW") for K in TL["caps"]]
    S["LR_CAP_NS"] = f"{sum(q >= 0.05 for q in lr_q)}/{len(lr_q)}"
    S["Q_LR_RUS_CAP"] = f"{max(tl_test(f'LR|RUS|cap|{K}|ppv')['p_bh'] for K in TL['caps']):.3f}".replace(".", "." if EN else ",")
    S["Q_RF_RUS_CAP5"] = f"{tl_test('RF|RUS|cap|0.05|ppv')['p_bh']:.3f}".replace(".", "." if EN else ",")
    rf_q = [tl_test(f"RF|{h}|cap|{K}|ppv")["p_bh"] for h in ("ROS", "SMOTE", "CW") for K in TL["caps"]]
    S["RF_CAP_SIG"] = f"{sum(q < 0.05 for q in rf_q)}/{len(rf_q)}"
    # TL2b — ngưỡng
    S["NB_ALL_5"], S["NB_ALL_10"] = fnum(1000 * TL["ref_all"]["0.05"], 2), fnum(1000 * TL["ref_all"]["0.1"], 2)
    lr_all = [T("tl2", f"LR|{h}|raw|{pt}|refer") for h in ("RUS", "ROS", "SMOTE", "CW") for pt in (0.02, 0.05)]
    S["LR_REFER_MIN"] = pct(min(lr_all), 2)
    # TL3 — sửa thang
    for m, hs in (("LR", ("RUS", "ROS", "SMOTE", "CW")), ("RF", ("ROS", "SMOTE", "CW"))):
        pcs = [T("tl3", f"{m}|{h}|pc|ece") for h in hs]
        mms = [T("tl3", f"{m}|{h}|mm_0.02|ece") for h in hs]
        S[f"{m}_PC_ECE_MIN"], S[f"{m}_PC_ECE_MAX"] = fnum(1000 * min(pcs), 1), fnum(1000 * max(pcs), 1)
        S[f"{m}_MM_ECE_MIN"], S[f"{m}_MM_ECE_MAX"] = fnum(1000 * min(mms), 1), fnum(1000 * max(mms), 1)
    lr_nbdiff = [abs(tl_test(f"LR|{h}|{c}|nb|{pt}")["effect"]) for h in ("RUS", "ROS", "SMOTE", "CW")
                 for c in ("pc", "mm_0.02") for pt in TL["pts"]]
    S["LR_REPAIR_MAXDIFF"] = fnum(1000 * max(lr_nbdiff), 2)
    sl = [T("tl3", f"RF|{h}|raw|slope") for h in ("ROS", "SMOTE", "CW")]
    S["RF_SLOPE_MIN"], S["RF_SLOPE_MAX"] = fnum(min(sl), 2), fnum(max(sl), 2)
    S["RF_N0_SLOPE"] = fnum(T("tl3", "RF|N0|raw|slope"), 2)
    lrs = [T("tl3", f"LR|{h}|raw|slope") for h in ("N0", "RUS", "ROS", "SMOTE", "CW")]
    S["LR_SLOPE_MIN"], S["LR_SLOPE_MAX"] = fnum(min(lrs), 2), fnum(max(lrs), 2)
    # Platt trên mẫu nhỏ
    negs = {n: [T("tl3", f"{m}|{h}|platt_{n}|neg_slope") * T("tl3", f"{m}|{h}|platt_{n}|neg_slope", 2)
                for m in ("LR", "RF") for h in TL["methods"]] for n in TL["n_audit"]}
    runs = {n: [T("tl3", f"{m}|{h}|platt_{n}|neg_slope", 2) for m in ("LR", "RF") for h in TL["methods"]]
            for n in TL["n_audit"]}
    for n in TL["n_audit"]:
        S[f"PLATT_NEG_{n}"] = f"{round(sum(negs[n]))}/{round(sum(runs[n]))}"
    S["NPOS_100"] = fnum(T("tl3", "LR|N0|icpt_100|npos"), 1)
    S["NPOS_200"] = fnum(T("tl3", "LR|N0|icpt_200|npos"), 1)
    S["NPOS_500"] = fnum(T("tl3", "LR|N0|icpt_500|npos"), 1)
    S["SKIP_100"] = str(round(T("tl3", "LR|N0|platt_100|skipped", 2)))
    # công cụ — ví dụ
    a, b2, c = DEMO["A_LR_SMOTE_khong_nhan"], DEMO["B_RF_SMOTE_co_1000_nhan"], DEMO["C_LR_nguyen_trang_co_1000_nhan"]
    S["DA_INFL"] = fnum(a["he_so_thoi_phong"], 1)
    S["DA_REF5"] = pct(a["tai_chuyen"]["0.05"], 1)
    S["DA_REF5_AFTER"] = pct(a["sua_thang"]["tai_chuyen_sau"]["0.05"], 1)
    S["DA_HI_BEFORE"] = str(a["dai_nguy_co_nguyen_trang"][3]["tren_1000_tre"])
    S["DA_HI_AFTER"] = str(a["sua_thang"]["dai_nguy_co_sau"][3]["tren_1000_tre"])
    S["DB_INFL"] = fnum(b2["he_so_thoi_phong"], 1)
    S["DB_NPOS"] = str(b2["nhan"]["so_ca_duong"])
    S["DB_SLOPE"] = fnum(b2["sua_thang"]["he_so_goc_hieu_chinh"], 2)
    S["DB_NB5_BEFORE"] = fnum(b2["loi_ich_rong_x1000"]["0.05"]["truoc"], 2)
    S["DB_NB5_AFTER"] = fnum(b2["loi_ich_rong_x1000"]["0.05"]["sau"], 2)
    S["DC_INFL"] = fnum(c["he_so_thoi_phong"], 2)
    S["DC_SLOPE"] = fnum(c["sua_thang"]["he_so_goc_hieu_chinh"], 2)
    S["DC_LO"], S["DC_HI"] = fnum(c["nhan"]["wilson95"][0], 3), fnum(c["nhan"]["wilson95"][1], 3)
    S["DC_REF5"] = pct(c["tai_chuyen"]["0.05"], 1)
    S.update(tables())
    return S


LAB = {
    "meth": {"N0": ("Nguyên trạng", "As collected"), "RUS": ("Lấy mẫu thiếu", "Under-sampling"),
             "ROS": ("Lấy mẫu thừa", "Over-sampling"), "SMOTE": ("SMOTE", "SMOTE"),
             "CW": ("Trọng số lớp", "Class weights"), "TS": ("Dịch chuyển ngưỡng", "Threshold moving")},
    "model": {"LR": ("Hồi quy logistic", "Logistic regression"), "RF": ("Rừng ngẫu nhiên", "Random forest"),
              "FKNN": ("Fuzzy k-NN", "Fuzzy k-NN"), "HYB": ("Mô hình lai ba nhánh", "Three-branch hybrid")},
    "corr": {"raw": ("Dùng nguyên xác suất", "Raw output"),
             "pc": ("Hiệu chỉnh tiên nghiệm (biết tỷ lệ huấn luyện)", "Prior correction (training prevalence known)"),
             "mm_0.02": ("Khớp trung bình, tỷ lệ đúng 2 %", "Mean matching, correct prevalence 2%"),
             "mm_0.01": ("Khớp trung bình, giả định 1 %", "Mean matching, assumed 1%"),
             "mm_0.04": ("Khớp trung bình, giả định 4 %", "Mean matching, assumed 4%"),
             "icpt_100": ("Cập nhật hệ số chặn, n = 100", "Intercept update, n = 100"),
             "icpt_200": ("Cập nhật hệ số chặn, n = 200", "Intercept update, n = 200"),
             "icpt_500": ("Cập nhật hệ số chặn, n = 500", "Intercept update, n = 500"),
             "platt_500": ("Khớp lại Platt, n = 500", "Platt refit, n = 500")},
    "band": (["Dưới 1 %", "1–5 %", "5–20 %", "Từ 20 % trở lên"], ["Below 1%", "1–5%", "5–20%", "20% or higher"]),
}


SHORT = {"raw": ("dùng nguyên", "raw"), "pc": ("hiệu chỉnh tiên nghiệm", "prior correction"),
         "mm_0.02": ("khớp trung bình", "mean matching")}


def lab(group, key):
    return LAB[group][key][1 if EN else 0]


def tables():
    Tb = {}
    L_ = lambda vi, en: en if EN else vi
    # Bảng 1 — lưới chính ở 2 %: PR-AUC, Brier, tỷ lệ chuyển ở p_t = 2 %
    rows = []
    for m in ("LR", "RF", "FKNN", "HYB"):
        for h in ("N0", "RUS", "SMOTE", "TS"):
            rows.append([lab("model", m) if h == "N0" else "", lab("meth", h),
                         fnum(1000 * gcell(0.02, m, h, "pr_auc"), 1), fnum(1000 * gcell(0.02, m, h, "brier"), 1),
                         pct(gcell(0.02, m, h, "flag_rate"), 1), fnum(1000 * gcell(0.02, m, h, "nb"), 2)])
    Tb["TABLE1"] = md_table([L_("Mô hình", "Model"), L_("Cách huấn luyện", "Training"), L_("PR-AUC ×1 000", "PR-AUC ×1,000"),
                             L_("Brier ×1 000", "Brier ×1,000"), L_("Tỷ lệ trẻ bị chuyển", "Children referred"),
                             L_("Lợi ích ròng ×1 000", "Net benefit ×1,000")], rows,
                            [":" + "-" * 20, ":" + "-" * 18, *([":" + "-" * 10 + ":"] * 4)])
    # Bảng 2 — dải nguy cơ (LR): nguyên trạng / SMOTE thô / SMOTE khớp trung bình / SMOTE cập nhật chặn n=200
    rows = []
    for i, bnd in enumerate(TL["bands"]):
        r = [LAB["band"][1 if EN else 0][i]]
        for meth, corr in (("N0", "raw"), ("SMOTE", "raw"), ("SMOTE", "mm_0.02")):
            s = T("tl1", f"LR|{meth}|{corr}|{bnd}|share")
            o = T("tl1", f"LR|{meth}|{corr}|{bnd}|obs")
            r += [fnum(1000 * s, 0), "—" if s < 0.0005 or o != o else fnum(1000 * o, 0)]
        rows.append(r)
    hdr = [L_("Dải nguy cơ", "Risk band")]
    for vi, en in (("nguyên trạng", "as collected"), ("SMOTE, thô", "SMOTE, raw"), ("SMOTE + khớp TB", "SMOTE + mean matching")):
        hdr += [L_(f"Trẻ/1 000 ({vi})", f"Children/1,000 ({en})"), L_(f"Mắc thật/1 000 ({vi})", f"Affected/1,000 ({en})")]
    Tb["TABLE2"] = md_table(hdr, rows, [":" + "-" * 16, *([":" + "-" * 8 + ":"] * 6)])
    # Bảng 3 — năng lực
    rows = []
    for m in ("LR", "RF"):
        for h in TL["methods"]:
            r = [lab("model", m) if h == "N0" else "", lab("meth", h)]
            for K in TL["caps"]:
                mu, sd = T("tl2", f"{m}|{h}|cap|{K}|ppv"), T("tl2", f"{m}|{h}|cap|{K}|ppv", 1)
                cellv = f"{fnum(100 * mu, 2)} ± {fnum(100 * sd, 2)}"
                if h != "N0":
                    t = tl_test(f"{m}|{h}|cap|{K}|ppv")
                    if t["p_bh"] < 0.05:
                        cellv += "\\*"
                r.append(cellv)
            r.append(pct(T("tl2", f"{m}|{h}|cap|0.05|sens"), 1))
            rows.append(r)
    Tb["TABLE3"] = md_table([L_("Mô hình", "Model"), L_("Cách huấn luyện", "Training"),
                             "K = 2 %" if not EN else "K = 2%", "K = 5 %" if not EN else "K = 5%",
                             "K = 10 %" if not EN else "K = 10%", L_("Độ nhạy ở K = 5 %", "Sensitivity at K = 5%")],
                            rows, [":" + "-" * 18, ":" + "-" * 16, *([":" + "-" * 12 + ":"] * 4)])
    # Bảng 4 — ngưỡng: tỷ lệ chuyển và NB, raw / pc / mm
    rows = [[L_("Chuyển tất cả", "Refer all"), ""] + [f"100{',0' if not EN else '.0'}{' %' if not EN else '%'} · "
                                                     f"{fnum(1000 * TL['ref_all'][str(pt)], 2)}" for pt in TL["pts"]]]
    for m in ("LR", "RF"):
        for h, c in (("N0", "raw"), ("SMOTE", "raw"), ("SMOTE", "pc"), ("SMOTE", "mm_0.02"), ("CW", "raw"),
                     ("CW", "mm_0.02"), ("RUS", "pc")):
            r = [lab("model", m) if (h, c) == ("N0", "raw") else "",
                 f"{lab('meth', h)} — {SHORT[c][1 if EN else 0]}"]
            for pt in TL["pts"]:
                r.append(f"{pct(T('tl2', f'{m}|{h}|{c}|{pt}|refer'), 1)} · {fnum(1000 * T('tl2', f'{m}|{h}|{c}|{pt}|nb'), 2)}")
            rows.append(r)
    Tb["TABLE4"] = md_table([L_("Mô hình", "Model"), L_("Huấn luyện — xử lý đầu ra", "Training — output handling"),
                             "p~t~ = 2 %" if not EN else "p~t~ = 2%", "p~t~ = 5 %" if not EN else "p~t~ = 5%",
                             "p~t~ = 10 %" if not EN else "p~t~ = 10%"], rows,
                            [":" + "-" * 13, ":" + "-" * 25, *([":" + "-" * 19 + ":"] * 3)])
    # Bảng 5 — sửa thang cho LR-SMOTE và RF-SMOTE
    rows = []
    for m in ("LR", "RF"):
        for c in ("raw", "pc", "mm_0.01", "mm_0.02", "mm_0.04", "icpt_100", "icpt_200", "icpt_500", "platt_500"):
            k = f"{m}|SMOTE|{c}"
            r = [lab("model", m) if c == "raw" else "", lab("corr", c),
                 fnum(T("tl3", k + "|mean_p"), 4),
                 f"{fnum(1000 * T('tl3', k + '|ece'), 1)} ± {fnum(1000 * T('tl3', k + '|ece', 1), 1)}",
                 "—" if c.startswith("platt") else fnum(T("tl3", k + "|slope"), 2),
                 pct(T("tl2", f"{k}|0.05|refer"), 1), fnum(1000 * T("tl2", f"{k}|0.05|nb"), 2)]
            rows.append(r)
        k = f"{m}|N0|raw"
        rows.append(["", L_("*Mốc: huấn luyện nguyên trạng*", "*Reference: trained as collected*"),
                     fnum(T("tl3", k + "|mean_p"), 4), fnum(1000 * T("tl3", k + "|ece"), 1),
                     fnum(T("tl3", k + "|slope"), 2), pct(T("tl2", f"{k}|0.05|refer"), 1),
                     fnum(1000 * T("tl2", f"{k}|0.05|nb"), 2)])
    Tb["TABLE5"] = md_table([L_("Mô hình", "Model"), L_("Xử lý đầu ra (sau SMOTE)", "Output handling (after SMOTE)"),
                             L_("Nguy cơ TB", "Mean risk"), L_("ECE ×1 000", "ECE ×1,000"),
                             L_("Hệ số góc", "Slope"), L_("Chuyển ở 5 %", "Referred at 5%"),
                             L_("NB ×1 000 ở 5 %", "NB ×1,000 at 5%")], rows,
                            [":" + "-" * 13, ":" + "-" * 30, ":" + "-" * 9 + ":", ":" + "-" * 14 + ":",
                             ":" + "-" * 8 + ":", ":" + "-" * 9 + ":", ":" + "-" * 10 + ":"])
    return Tb


# ------------------------------------------------------------------ trích dẫn
def cite(text):
    used, order = set(), []

    def use(k):
        if k not in REFS:
            raise SystemExit(f"thiếu tài liệu: {k}")
        used.add(k)

    def short(k):
        a, y = REFS[k][0], REFS[k][1]
        return fill_words(a), y

    def rep(m):
        keys = [k.strip().lstrip("@") for k in m.group(1).split(";")]
        parts = []
        for k in keys:
            use(k)
            a, y = short(k)
            parts.append(f"{a}, {y}")
        return "(" + "; ".join(parts) + ")"
    out = re.sub(r"\[(@[^\]]+)\]", rep, text)

    def narr(m):
        k = m.group(1)
        use(k)
        a, y = short(k)
        a = a.replace(" & ", " and ") if EN else a
        return f"{a} ({y})"
    out = re.sub(r"\{@([A-Za-z0-9]+)\}", narr, out)
    return out, used


H = {"User-Agent": "p11-tl-refcheck/1.0 (mailto:research@example.org)"}


def check_dois(keys):
    bad, n = [], 0
    for k in sorted(keys):
        s, doi = fill_words(REFS[k][2]), REFS[k][3]
        if not doi:
            continue
        n += 1
        try:
            m = None
            for attempt in range(4):                       # Crossref đôi khi quá thời gian: thử lại
                try:
                    m = json.load(urllib.request.urlopen(urllib.request.Request(
                        "https://api.crossref.org/works/" + urllib.request.quote(doi), headers=H), timeout=60))["message"]
                    break
                except Exception:  # noqa: BLE001
                    if attempt == 3:
                        raise
            years = {str(m[f]["date-parts"][0][0]) for f in ("published-print", "published-online", "issued")
                     if m.get(f)}
            fam = next((a.get("family") for a in m.get("author") or [] if a.get("family")), "")
            probs = []
            if not any(y in s for y in years):
                probs.append(f"năm {sorted(years)} không có trong trích dẫn")
            key = FAMILY_ALIAS.get(k, (fam or "").split()[0] if fam else "")
            if key and key.lower() not in s.lower():
                probs.append(f"họ tác giả đầu '{fam}' không khớp")
            title = (m.get("title") or [""])[0]
            words = [x for x in re.findall(r"[A-Za-z]{5,}", title)][:4]
            if words and not all(x.lower() in s.lower() for x in words):
                probs.append(f"tên bài Crossref '{title[:70]}' không khớp")
            if probs:
                bad.append(f"{k}: " + "; ".join(probs))
        except Exception as e:  # noqa: BLE001
            bad.append(f"{k}: không tra được DOI {doi} ({e})")
    return n, bad


def main():
    src = open(os.path.join(OUTDIR, f"{BASE}_src.md"), encoding="utf-8").read()
    subs = build_subs()
    md = re.sub(r"\{\{([^{}]+)\}\}", lambda m: m.group(0) if m.group(1) == "REFERENCES" else token(m.group(1), subs),
                src)
    md, used = cite(md)
    unused = set(REFS) - used
    if unused:
        raise SystemExit(f"tài liệu không được trích: {sorted(unused)}")
    reflist = sorted((fill_words(REFS[k][2]) + (f" https://doi.org/{REFS[k][3]}" if REFS[k][3] else "") for k in used),
                     key=lambda s: s.replace("*", "").replace("[", "").lower())
    md = md.replace("{{REFERENCES}}", "\n\n".join(reflist))
    left = re.findall(r"\{\{[^}]*\}\}", md)
    if left:
        raise SystemExit(f"còn ô chưa điền: {left}")
    open(os.path.join(OUTDIR, f"{BASE}.md"), "w", encoding="utf-8", newline="\n").write(md)
    if "--check-doi" in sys.argv:
        n, bad = check_dois(used)
        rep = [f"Đối chiếu Crossref {n} DOI: {len(bad)} vấn đề"] + bad
        open(os.path.join(OUTDIR, f"{BASE.lower()}_doi_check.txt"), "w", encoding="utf-8").write("\n".join(rep) + "\n")
        print("\n".join(rep))
    ref_doc = os.path.join(HERE, "reference_tl.docx")      # A4, Times New Roman 13, giãn dòng 1,3
    out = os.path.join(OUTDIR, f"{BASE}_manuscript.docx")
    r = subprocess.run([PANDOC, f"{BASE}.md", "-o", out, "--reference-doc", ref_doc, "--resource-path", OUTDIR],
                       cwd=OUTDIR, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit("pandoc lỗi: " + r.stderr)
    postprocess(out)
    print(f"đã dựng {out}")


def postprocess(path):
    """Viền bảng kiểu APA (đường trên, dưới tiêu đề, dưới cùng); cỡ chữ bảng 10; thụt treo danh mục tài liệu."""
    import docx
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt
    d = docx.Document(path)
    in_refs = False
    head = "REFERENCES" if EN else "TÀI LIỆU THAM KHẢO"
    for p in d.paragraphs:
        if p.style.name.startswith("Heading"):
            in_refs = p.text.strip().startswith(head)
            continue
        if in_refs and p.text.strip():
            pf = p.paragraph_format
            pf.left_indent, pf.first_line_indent = Cm(1.27), Cm(-1.27)
            pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for tbl in d.tables:
        tblPr = tbl._tbl.tblPr
        b = tblPr.find(qn("w:tblBorders"))
        if b is not None:
            tblPr.remove(b)
        b = tblPr.makeelement(qn("w:tblBorders"), {})
        for side in ("top", "bottom"):
            b.append(b.makeelement(qn(f"w:{side}"), {qn("w:val"): "single", qn("w:sz"): "8", qn("w:space"): "0",
                                                     qn("w:color"): "000000"}))
        tblPr.append(b)
        for c in tbl.rows[0].cells:
            tcPr = c._tc.get_or_add_tcPr()
            bb = tcPr.makeelement(qn("w:tcBorders"), {})
            bb.append(bb.makeelement(qn("w:bottom"), {qn("w:val"): "single", qn("w:sz"): "6", qn("w:space"): "0",
                                                      qn("w:color"): "000000"}))
            tcPr.append(bb)
        for row in tbl.rows:
            for c in row.cells:
                for p in c.paragraphs:
                    p.paragraph_format.first_line_indent = Cm(0)
                    p.paragraph_format.line_spacing = 1.05
                    for r in p.runs:
                        r.font.size = Pt(10)
    d.save(path)


if __name__ == "__main__":
    main()
