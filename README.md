# Khi công cụ sàng lọc được huấn luyện trên dữ liệu "cân bằng lại" — mã nguồn, kết quả và công cụ kiểm tra đầu ra

Mã nguồn, kết quả đã tính, công cụ kiểm tra đầu ra cho dịch vụ tâm lý và công cụ dựng bản thảo (tiếng Việt và tiếng
Anh) cho bài báo *Khi công cụ sàng lọc được huấn luyện trên dữ liệu "cân bằng lại": xử lý mất cân bằng lớp ảnh hưởng
thế nào đến con số nguy cơ nói với gia đình và danh sách chờ của dịch vụ tâm lý — nghiên cứu trên dữ liệu tổng hợp*
(bản tiếng Anh: *When a screening tool is trained on rebalanced data: class-imbalance handling, the risk figure told
to families, and the waiting list of a child psychological service — a simulation study*). Trích dẫn APA 7.

*English summary.* Screening tools are often trained after under-sampling, over-sampling, SMOTE or class weighting.
On synthetic questionnaire data at 2% prevalence (logistic regression and random forest, five training strategies,
20 replications, a fixed population of 50,000 children), rebalancing inflated the mean predicted risk up to ~22-fold,
put 86% of children in a "20% or higher" band whose true rate was ~2%, and turned a "refer at 5% risk" rule into
"refer everyone" — without finding more true cases when the service admits a fixed share of children. Prior
correction and label-free "mean matching" to a known prevalence repaired logistic regression almost completely but
not random forest after over-sampling/SMOTE/class weights (calibration slope 0.3–0.4). `src/p11_referral_audit.py`
implements the resulting pre-deployment check for a service's own CSV of scores.

**Mọi kết quả đều từ dữ liệu tổng hợp.** Kho này không chứa và không dùng dữ liệu của trẻ thật nào. Các mô hình ở
đây là nguyên mẫu nghiên cứu, không phải công cụ chẩn đoán, và chưa được thẩm định lâm sàng.

## Nội dung

| Đường dẫn | Nội dung |
|---|---|
| `src/p11_referral_audit.py` | **Công cụ kiểm tra đầu ra** cho dịch vụ tâm lý: đọc CSV điểm (nhãn tuỳ chọn), báo hệ số thổi phồng, tải chuyển so với năng lực, điểm cắt theo năng lực và số trẻ trùng điểm, sửa thang (khớp trung bình hoặc hiệu chỉnh tiên nghiệm), bảng dải nguy cơ trước–sau "trên 1 000 trẻ", và nếu có nhãn: KTC Wilson, hệ số góc hiệu chỉnh, lợi ích ròng; `--demo` chạy ba nhà cung cấp giả định của mục 3.6 |
| `src/run_p11_tl.py` | Ba phân tích của bài: dải nguy cơ (TL1), dịch vụ theo năng lực và theo ngưỡng (TL2), sửa thang trước triển khai (TL3), Benjamini–Hochberg 108 phép kiểm → `out/reports/p11_tl.json`, `p11_tl.txt`, `p11_tl_config_log.json` |
| `src/run_p11_tasks.py`, `src/run_imbalance.py` | Lưới chính của nghiên cứu đi kèm (11 cách × 4 mô hình × 4 tỷ lệ, 20 lần lặp, tập kiểm thử 50 000) → `out/reports/p11_tasks.json` (mục 3.1, Bảng 1) |
| `src/fig_p11_tl.py`, `src/figstyle.py` | Hình 1–3 (`--en`: nhãn tiếng Anh) |
| `src/ts_*.py`, `src/config.py`, `src/data/questions.csv` | Bộ sinh dữ liệu, hệ suy diễn mờ và phiếu nghiên cứu 20 câu |
| `out/reports/_p11_pool.npz` | Kho hồ sơ tổng hợp đã tóm thành sáu điểm lĩnh vực (1,3 MB) — để chạy nhanh; xoá đi thì `run_p11_tl.py` sinh lại (~1–3 phút) |
| `tests/test_p11_tl.py` | Kiểm thử: hiệu chỉnh tiên nghiệm, khớp trung bình, hệ số góc, nhận theo năng lực có trùng điểm, lợi ích ròng, KTC Wilson, các nhánh cảnh báo của công cụ |
| `manuscript/P11_TL/` | **Bản tiếng Việt**: `P11_TL_src.md` (ô `{{...}}` điền từ JSON; trích dẫn `[@khoá]`) → `build_p11_tl.py [--check-doi]` → `P11_TL_manuscript.docx`; `p11_tl_kiem_tra.py` tự kiểm 85 nhận định |
| `manuscript/P11_TL_EN/` | **Bản tiếng Anh**: `P11_TL_EN_src.md` → `build_p11_tl.py --lang en [--check-doi]` → `P11_TL_EN_manuscript.docx`; `p11_tl_kiem_tra.py --lang en` tự kiểm 86 nhận định |

## Dùng công cụ kiểm tra đầu ra

Chỉ cần Python 3 và NumPy. Tệp CSV có một cột điểm là xác suất 0–1 do công cụ sàng lọc xuất và, nếu có, một cột nhãn
0/1 từ đánh giá chuyên sâu.

```
python src/p11_referral_audit.py diem.csv --prevalence 0.02 --capacity 0.05
python src/p11_referral_audit.py diem_co_nhan.csv --label-col label --prevalence 0.02 --capacity 0.05 --out bao_cao.json
python src/p11_referral_audit.py diem.csv --prevalence 0.02 --train-prev 0.02 --balanced-prev 0.5   # nhà cung cấp khai báo tỷ lệ
python src/p11_referral_audit.py --demo
```

Các ngưỡng cảnh báo (hệ số thổi phồng 1,5; hệ số góc ngoài [0,7; 1,4]; tối thiểu 10 trẻ mắc để ước lượng hệ số góc)
là quy ước rút ra từ nghiên cứu mô phỏng, không phải chuẩn lâm sàng.

## Tái lập

Python 3.12.10, CPU; thư viện trong `requirements-p11.txt`; dựng .docx cần pandoc 3 trở lên. Mọi hạt giống cố định.

```
python -m venv .venv
.venv/Scripts/pip install -r requirements-p11.txt        # Linux/macOS: .venv/bin/pip
python tests/test_p11_tl.py                              # vài giây
python src/run_p11_tl.py                                 # khoảng 10 phút → p11_tl.json
python src/p11_referral_audit.py --demo                  # → p11_tool_demo.json
python src/fig_p11_tl.py && python src/fig_p11_tl.py --en
python manuscript/P11_TL/build_p11_tl.py                 # → manuscript/P11_TL/P11_TL_manuscript.docx
python manuscript/P11_TL/p11_tl_kiem_tra.py
python manuscript/P11_TL/build_p11_tl.py --lang en       # → manuscript/P11_TL_EN/P11_TL_EN_manuscript.docx
python manuscript/P11_TL/p11_tl_kiem_tra.py --lang en
python src/run_p11_tasks.py                              # tuỳ chọn: lưới chính, khoảng 30–90 phút
```

Chạy lại `run_p11_tl.py` và `p11_referral_audit.py --demo` cho `p11_tl.json` và `p11_tool_demo.json` trùng từng byte
với bản đóng gói (đã kiểm bằng cách giải nén gói vào thư mục trống và chạy lại). Rừng ngẫu nhiên được huấn luyện song
song nhưng dự báo đơn luồng để tổng qua các cây có thứ tự cố định. Riêng lưới chính `run_p11_tasks.py` dự báo song
song nên hai lần chạy khớp tới sai số làm tròn chứ không trùng từng bit (xem `out/reports/p11_determinism.txt`). Trên
Windows, tiến trình Python chạy nền có thể bị hạ ưu tiên (EcoQoS) nên thời gian chạy dao động; kết quả không đổi.

## Giấy phép

Mã nguồn: MIT (xem `LICENSE`). Văn bản bản thảo thuộc các tác giả; xin trích dẫn bài báo khi dùng.
