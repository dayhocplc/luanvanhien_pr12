# Bài 11 — bản công nghệ hỗ trợ tâm lý trị liệu (VN + EN): việc tác giả cần làm trước khi nộp

Bản thảo:
- Tiếng Việt: `P11_TL_manuscript.docx` (A4, một cột, APA 7, 23 trang). Nguồn duy nhất cần sửa: `P11_TL_src.md`.
- Tiếng Anh: `../P11_TL_EN/P11_TL_EN_manuscript.docx` (23 trang). Nguồn: `../P11_TL_EN/P11_TL_EN_src.md`.
- Dựng: `python manuscript/P11_TL/build_p11_tl.py [--lang en] [--check-doi]`, rồi `p11_tl_kiem_tra.py [--lang en]` (phải ĐẠT hết).
- Mọi con số đi qua ô `{{...}}` lấy từ `out/reports/p11_tl.json`, `p11_tasks.json`, `p11_tool_demo.json` — không gõ tay.

## Phải làm
1. **Tác giả, đơn vị, email, ORCID** ở đầu bài; thay "[Tác giả], 2026a/b/c" ("[Author]" ở bản EN) trong danh mục tài
   liệu bằng tên thật. Ba bản thảo cùng nhóm: 2026a = bản EN phương pháp `manuscript/P11` (BMC Med Res Methodol);
   2026b = bản JSLHU `out/jslhu/Bai_P11_JSLHU_Tai_lay_mau_hay_dich_chuyen_nguong.docx`; 2026c = Bài 9 bản tâm lý
   `manuscript/P9_TL`. Nếu tên bài của các bản đó đổi khi nộp, sửa mục `nhom2026*` trong `REFS` của `build_p11_tl.py`.
2. **Chọn tạp chí và kiểm thể lệ.** Bản VN hợp với tạp chí tâm lý học trong nước (APA); bản EN viết cho tạp chí về
   công nghệ trong khoa học hành vi / sức khỏe tâm thần số (ví dụ *Journal of Technology in Behavioral Science*; có
   sẵn "Public significance statement" kiểu APA). Nếu giới hạn ~6 000 từ: rút mục 3.1 thành một đoạn (bỏ Bảng 1 sang
   phụ lục), gộp 1.1–1.2, chuyển mục 3.6 sang phụ lục.
3. **Đăng trùng / chồng lấn — quan trọng.**
   - Mục 3.1 và Bảng 1 dùng chung kết quả với bản EN phương pháp (`manuscript/P11`) và bản JSLHU. Hai bài này đã
     được khai báo trong mục "Công bố liên quan / Related publications".
   - Bản VN và bản EN của bài này dùng CÙNG dữ liệu và kết quả mới (mục 3.2–3.6). Nhiều tạp chí coi đây là đăng
     trùng nếu không có sự đồng ý của cả hai ban biên tập. **Nên nộp bản EN trước**, rồi chỉ nộp bản VN nếu tạp chí
     trong nước chấp nhận bản dịch/bản song ngữ đã công bố (ghi rõ trong thư gửi ban biên tập). Nếu không, chọn MỘT.
   - Bản JSLHU cũ của P11 và bài này cùng là tiếng Việt: chỉ nộp một bản tiếng Việt.
4. **Đường dẫn GitHub** ở mục "Dữ liệu và mã nguồn / Data and code availability" sau khi đẩy gói
   `release/p11_tl_github/dist/P11_TL_code_v1.0.0.zip`; điền `CITATION.cff` (tác giả, DOI Zenodo nếu có).
5. **Tài trợ, đóng góp tác giả (CRediT)** ở mục Tuyên bố.

## Nên làm
- Mời một nhà tâm lý lâm sàng trẻ em làm đồng tác giả hoặc đọc góp ý mục 1.1, 4.1 và Bảng 6 — tạp chí tâm lý thường
  hỏi điều này với bài do nhóm kỹ thuật viết.
- Bốn dải nguy cơ, ba mức năng lực (2/5/10 %) và ngưỡng cảnh báo của công cụ là quy ước minh họa. Nếu dịch vụ hợp tác
  có quy ước thật, sửa `BANDS`, `CAPS` trong `src/run_p11_tl.py` (và `src/p11_referral_audit.py`), chạy lại (~10 phút)
  rồi dựng lại bài.
- Nếu phản biện hỏi về các tỷ lệ mắc khác: lưới chính (`p11_tasks.json`) đã có 1/2/3/5 %; chạy `run_p11_tl.py` với
  `PREV` khác là đủ.

## Đã kiểm
- DOI đối chiếu Crossref (năm, họ tác giả đầu, bốn từ đầu tên bài): xem `p11_tl_doi_check.txt` và
  `../P11_TL_EN/p11_tl_en_doi_check.txt`. Ancker 2017 bổ sung tác giả nhóm "the HITEC Investigators" theo Crossref.
  Hai mục không DOI (Elkan 2001 — kỷ yếu IJCAI; QĐ 2254/QĐ-BYT) và luận văn Nguyễn 2026 đã kiểm tay.
- Nhận định trong bài khớp tệp kết quả: `p11_tl_kiem_tra.txt` (bản VN) và `../P11_TL_EN/p11_tl_en_kiem_tra.txt`.
- Số liệu nghiên cứu Vo và cs. (2026) — 3 639 trẻ, AUC 0,983, precision 0,351, tỷ lệ ~2 % — lấy từ tóm tắt bài báo
  (xem `DO_THI_TRI_THUC_CONG_BO.md`, mục C9); nên đối chiếu lại với bản toàn văn trước khi nộp.
- Chạy lại `run_p11_tl.py` và `p11_referral_audit.py --demo` từ gói zip đã giải nén cho JSON trùng từng byte
  (`make_release.py --verify`).
