---
title: "KHI CÔNG CỤ SÀNG LỌC ĐƯỢC HUẤN LUYỆN TRÊN DỮ LIỆU “CÂN BẰNG LẠI”: XỬ LÝ MẤT CÂN BẰNG LỚP ẢNH HƯỞNG THẾ NÀO ĐẾN CON SỐ NGUY CƠ NÓI VỚI GIA ĐÌNH VÀ DANH SÁCH CHỜ CỦA DỊCH VỤ TÂM LÝ — NGHIÊN CỨU TRÊN DỮ LIỆU TỔNG HỢP"
---

**Tác giả:** [Họ tên tác giả 1]^1,\*^, [Họ tên tác giả 2]^1^, [Họ tên tác giả 3]^2^

^1^ Khoa Công nghệ Thông tin, Trường Đại học Lạc Hồng, Biên Hòa, Đồng Nai

^2^ [Đơn vị công tác — khuyến nghị có một đồng tác giả là nhà tâm lý lâm sàng trẻ em]

^\*^ Tác giả liên hệ: [email]

# TÓM TẮT

Các công cụ số sàng lọc phát triển thường được huấn luyện trên dữ liệu đã "cân bằng lại" — bằng lấy mẫu thiếu, lấy mẫu thừa, SMOTE hoặc trọng số lớp — vì trẻ có rối loạn chỉ chiếm vài phần trăm. Nghiên cứu này hỏi: lựa chọn kỹ thuật đó làm gì với hai thứ mà một dịch vụ tâm lý trẻ em thực sự dùng, là con số nguy cơ được nói với gia đình và danh sách trẻ được chuyển tới đánh giá chuyên sâu? Chúng tôi dùng dữ liệu tổng hợp sinh từ một mô hình trả lời bảng hỏi 20 câu phủ sáu lĩnh vực phát triển ({{POOL_POS}} hồ sơ dương tính, {{POOL_NEG}} hồ sơ âm tính), tỷ lệ mắc cộng đồng 2 %, hồi quy logistic và rừng ngẫu nhiên, năm cách huấn luyện, {{NREP}} lần lặp và một quần thể đánh giá độc lập {{NEVAL}} trẻ. Huấn luyện sau SMOTE làm xác suất trung bình của hồi quy logistic tăng lên {{T3:LR|SMOTE|raw|mean_p|d3}} (gấp {{INFL_LR_SMOTE}} lần tỷ lệ thật), đưa {{T1:LR|SMOTE|raw|>=20%|share|p1}} số trẻ vào dải "từ 20 % trở lên" trong khi chỉ {{T1:LR|SMOTE|raw|>=20%|obs|k0}} trên 1 000 trẻ trong dải này thật sự mắc; với quy tắc "chuyển khi nguy cơ từ 5 %", gần như mọi trẻ đều bị chuyển. Khi dịch vụ nhận trẻ theo năng lực (5 % trẻ có điểm cao nhất), tái lấy mẫu không giúp hồi quy logistic và làm rừng ngẫu nhiên tìm được ít ca thật hơn — {{T2:RF|SMOTE|cap|0.05|ppv|c1}} so với {{T2:RF|N0|cap|0.05|ppv|c1}} ca thật trên 100 lượt đánh giá — ngoại trừ lấy mẫu thiếu. Hai phép sửa thang không cần nhãn — hiệu chỉnh tiên nghiệm và "khớp trung bình" theo tỷ lệ mắc đã biết — khôi phục gần trọn vẹn hồi quy logistic (sai số hiệu chỉnh kỳ vọng {{LR_MM_ECE_MIN}}–{{LR_MM_ECE_MAX}} phần nghìn), nhưng không sửa được rừng ngẫu nhiên sau lấy mẫu thừa, SMOTE hay trọng số lớp, vì ở đó thang bị biến dạng về hình dạng (hệ số góc hiệu chỉnh {{RF_SLOPE_MIN}}–{{RF_SLOPE_MAX}}). Cập nhật trên 100–200 hồ sơ có nhãn tại chỗ kém hơn khớp trung bình theo tỷ lệ mắc đã biết. Chúng tôi đề xuất sáu câu hỏi dịch vụ tâm lý nên đặt cho nhà cung cấp công cụ và phát hành một công cụ mã nguồn mở kiểm tra đầu ra trước khi triển khai. Mọi kết quả thu được trên dữ liệu tổng hợp và cần được kiểm chứng trên dữ liệu thực địa.

**Từ khóa:** tâm lý lâm sàng trẻ em; công cụ số hỗ trợ quyết định; mất cân bằng lớp; truyền đạt nguy cơ; năng lực dịch vụ.

# ABSTRACT

**When a screening tool is trained on "rebalanced" data: How class-imbalance handling changes the risk figure told to families and the waiting list of a psychological service — a study on synthetic data.** Digital developmental screening tools are often trained on rebalanced data (under-sampling, over-sampling, SMOTE or class weights) because affected children are a small minority. Using synthetic questionnaire data (20 items, six developmental domains), a community prevalence of 2%, logistic regression and random forest, five training strategies, {{NREP}} replications and an independent population of 50,000 children, we examined what these choices do to the risk figure communicated to families and to the list of children referred for specialist assessment. Training after SMOTE raised the mean predicted risk of logistic regression about twentyfold and placed 86% of children in a "20% or higher" band whose true rate was about 2%; a "refer at 5% risk" rule then referred virtually every child. When the service admitted a fixed 5% of children with the highest scores, rebalancing did not help logistic regression and reduced the yield of random forest, except under-sampling. Two label-free repairs — analytical prior correction and "mean matching" to a known prevalence — almost fully restored logistic regression but not random forest after over-sampling, SMOTE or class weighting, where the distortion affected the shape of the risk scale (calibration slope 0.3–0.4). Updating on 100–200 local labelled records was worse than mean matching to a known prevalence. We propose six questions a psychological service should ask a tool vendor and release an open-source audit tool. All findings come from synthetic data and require field validation.

# 1. ĐẶT VẤN ĐỀ

## 1.1. Công cụ số trong chuỗi chăm sóc tâm lý trẻ em

Sàng lọc phát triển là cửa ngõ của chuỗi chăm sóc: bảng hỏi được điền ở cộng đồng hoặc cơ sở y tế ban đầu, trẻ có kết quả đáng lo ngại được chuyển tới nhà tâm lý hoặc nhóm đa chuyên ngành để đánh giá chuyên sâu, và chỉ sau đánh giá đó mới có chẩn đoán và can thiệp [@hyman2020]. Ở Việt Nam, bộ công cụ phát hiện sớm rối loạn phổ tự kỷ đã được Bộ Y tế ban hành [@byt2021], và các ứng dụng số ngày càng được dùng để chấm điểm, lưu trữ và gợi ý chuyển tuyến. Trong tâm lý học, xu hướng này nằm trong trào lưu rộng hơn của chăm sóc dựa trên đo lường và tâm thần học số [@lewis2019; @torous2021]: công cụ không thay nhà lâm sàng mà cung cấp thông tin cho các quyết định của họ, và từ lâu đã có bằng chứng rằng dự báo có cấu trúc thường ít nhất ngang bằng phán đoán không hỗ trợ [@grove2000]. Nhưng một hệ hỗ trợ quyết định chỉ có ích khi đầu ra của nó được đọc đúng nghĩa [@sutton2020].

Đầu ra của một công cụ sàng lọc được dùng theo hai cách, và hai cách này đòi hỏi hai phẩm chất khác nhau. Cách thứ nhất là **nói với gia đình**: nhà tâm lý hoặc cán bộ y tế đọc một con số hay một mức nguy cơ, và cha mẹ hiểu nó như xác suất con mình có rối loạn. Truyền đạt nguy cơ đúng nghĩa là một kỹ năng lâm sàng có cơ sở bằng chứng [@zipkin2014; @spiegelhalter2017]; nó chỉ khả thi nếu con số trên màn hình thật sự là một xác suất — tức là **được hiệu chỉnh** [@vancalster2019]. Cách thứ hai là **xếp danh sách chờ**: dịch vụ tâm lý có năng lực đánh giá hữu hạn, và công cụ quyết định trẻ nào được ưu tiên. Cách này chủ yếu cần công cụ **xếp đúng thứ tự** các trẻ, và — nếu việc chuyển được quyết định bằng một ngưỡng nguy cơ — cần ngưỡng đó mang đúng nghĩa để số trẻ bị chuyển khớp với năng lực của dịch vụ.

## 1.2. Mất cân bằng lớp và thói quen "cân bằng lại" dữ liệu

Trong cộng đồng, trẻ có rối loạn phổ tự kỷ chiếm khoảng 1 % [@zeidan2022], và tỷ lệ dương của các bảng hỏi sàng lọc chỉ vài phần trăm [@robins2014; @aishworiya2023]. Trong tài liệu học máy, tình huống này được gọi là **mất cân bằng lớp**, và phản xạ phổ biến là "cân bằng lại" tập huấn luyện: lấy mẫu thiếu lớp đa số, lấy mẫu thừa lớp thiểu số, sinh mẫu thiểu số nhân tạo bằng SMOTE [@chawla2002], hoặc gán trọng số lớn cho lớp thiểu số [@he2009; @fernandez2018]. Một nghiên cứu thực địa gần đây trên 3 639 trẻ Việt Nam dùng M-CHAT-R bản tiếng Việt báo cáo rừng ngẫu nhiên kết hợp SMOTE đạt AUC 0,983 nhưng độ chính xác dương (precision) chỉ 0,351 ở tỷ lệ mắc khoảng 2 % [@vo2026] — một minh họa rằng một chỉ số xếp hạng rất cao vẫn có thể đi kèm một tỷ lệ báo động nhầm đáng kể.

Y văn thống kê y học đã chỉ ra rằng các phép "sửa mất cân bằng" làm hỏng hiệu chỉnh xác suất mà thường không cải thiện năng lực phân biệt, với hồi quy logistic [@vandengoorbergh2022] và với các mô hình học máy [@carriero2025]. Về mặt lý thuyết, cân bằng lại tập huấn luyện tương đương với thay đổi xác suất tiên nghiệm, và có thể bù lại bằng công thức Bayes nếu biết tỷ lệ gốc [@elkan2001; @saerens2002; @dalpozzolo2015]. Tuy vậy, các kết quả này được viết bằng ngôn ngữ của nhà thống kê — điểm Brier, hệ số góc hiệu chỉnh, AUC — chứ không bằng ngôn ngữ của một dịch vụ tâm lý: bao nhiêu gia đình sẽ nghe một con số nguy cơ bị thổi phồng, danh sách chờ sẽ dài thêm bao nhiêu, và bao nhiêu trẻ mắc thật sẽ không được ưu tiên. Khi một bệnh viện hay trung tâm can thiệp **mua** hoặc **nhận** một công cụ, họ thường không kiểm soát được cách công cụ đã được huấn luyện; họ chỉ thấy đầu ra. Câu hỏi thực hành vì vậy là: **nhìn đầu ra, dịch vụ có nhận ra và sửa được hậu quả của việc cân bằng lại hay không?**

## 1.3. Mục tiêu

Nghiên cứu mô phỏng này trả lời ba câu hỏi, đặt trong bối cảnh một dịch vụ tâm lý nhận trẻ từ sàng lọc cộng đồng với tỷ lệ mắc 2 %:

1. **Con số nói với gia đình.** Cân bằng lại dữ liệu huấn luyện làm thay đổi thế nào tỷ lệ trẻ bị xếp vào mỗi dải nguy cơ, và dải đó còn trung thực không?
2. **Danh sách chờ.** Khi dịch vụ nhận trẻ theo năng lực cố định, cân bằng lại có giúp tìm được nhiều ca thật hơn không? Khi dịch vụ nhận trẻ theo một ngưỡng nguy cơ, bao nhiêu trẻ bị chuyển và lợi ích ròng của quyết định thay đổi ra sao?
3. **Kiểm tra và sửa trước khi dùng.** Khi nhà cung cấp đã cân bằng lại, dịch vụ có thể sửa thang nguy cơ mà không cần — hoặc chỉ cần ít — dữ liệu có nhãn tại chỗ không, và khi nào thì không sửa được?

Nghiên cứu đi kèm một bộ lưới đầy đủ hơn (bảy cách xử lý × bốn mô hình × bốn tỷ lệ mắc) được báo cáo riêng cho độc giả phương pháp học [@nhom2026en; @nhom2026vn]; ở đây chúng tôi chỉ tóm tắt lưới đó (mục 3.1) và tập trung vào ba phân tích mới hướng tới người dùng lâm sàng.

# 2. PHƯƠNG PHÁP

Thiết kế mô phỏng được mô tả theo khung ADEMP (mục tiêu, cơ chế sinh dữ liệu, đại lượng ước lượng, phương pháp, chỉ số đánh giá) [@morris2019]; báo cáo tuân theo các mục liên quan của TRIPOD+AI [@collins2024]. Nghiên cứu **không dùng dữ liệu của trẻ thật** nên không cần phê duyệt đạo đức.

## 2.1. Dữ liệu tổng hợp

Dữ liệu được sinh bằng bộ mô phỏng của một hệ sàng lọc lai luật – học máy đang được phát triển [@nguyen2026]. Bộ sinh mô phỏng câu trả lời của cha mẹ cho một bảng hỏi 20 câu phủ sáu lĩnh vực phát triển (giao tiếp – ngôn ngữ, vận động thô, vận động tinh, bắt chước – học, cá nhân – xã hội, hành vi bất thường), có mức bỏ trống và nhiễu trả lời. Mỗi hồ sơ được tóm thành sáu điểm nguy cơ theo lĩnh vực trên thang 0–1 bằng tầng suy diễn mờ của hệ; sáu điểm này là đầu vào của các mô hình. Chúng tôi sinh riêng một kho hồ sơ dương tính ({{POOL_POS_RAW}} hồ sơ) và một kho âm tính ({{POOL_NEG_RAW}} hồ sơ); sau khi loại hồ sơ bỏ trống quá 30 % số câu hoặc thiếu điểm lĩnh vực theo đúng quy tắc từ chối của công cụ, còn {{POOL_POS}} và {{POOL_NEG}} hồ sơ. Mỗi kho được chia đôi cố định thành phần **phát triển** (dùng để huấn luyện: {{DEV_POS}} dương, {{DEV_NEG}} âm) và phần **triển khai** (dùng để đánh giá). Vì bộ sinh chỉ dùng tỷ lệ mắc ở bước gán nhãn, rút lại từ hai kho theo một tỷ lệ bất kỳ cho đúng phân phối của quần thể ở tỷ lệ đó. Kho hồ sơ giống hệt kho của nghiên cứu đi kèm (dấu vân tay SHA-256 `{{POOLSHA}}…`).

**Quần thể triển khai.** Từ phần triển khai, chúng tôi rút cố định một quần thể {{NEVAL}} trẻ với đúng {{NEVAL_POS}} trẻ mắc (2 %) — đóng vai toàn bộ trẻ được sàng lọc trong một năm ở một địa bàn. Phần còn lại của phần triển khai ({{AUD_POS}} dương, {{AUD_NEG}} âm) chỉ dùng để rút các **mẫu kiểm tra có nhãn** ở mục 2.5, nên không hồ sơ nào vừa được dùng để sửa thang vừa được dùng để đánh giá.

## 2.2. Mô hình và năm cách huấn luyện

Ở mỗi lần lặp, một tập huấn luyện {{NTRAIN}} hồ sơ với tỷ lệ mắc 2 % (100 trẻ mắc) được rút ngẫu nhiên từ phần phát triển. Hai mô hình phổ biến nhất trong y văn sàng lọc bằng học máy được huấn luyện: **hồi quy logistic** (phạt L2, C = 1) và **rừng ngẫu nhiên** [@breiman2001] (200 cây, tối thiểu 5 hồ sơ mỗi lá). Mỗi mô hình được huấn luyện theo năm cách: (i) **nguyên trạng** — dùng dữ liệu như thu thập; (ii) **lấy mẫu thiếu** — bỏ ngẫu nhiên trẻ không mắc đến khi hai lớp bằng nhau (còn 100 + 100 hồ sơ); (iii) **lấy mẫu thừa** — nhân bản ngẫu nhiên trẻ mắc đến khi hai lớp bằng nhau; (iv) **SMOTE** — sinh trẻ mắc nhân tạo bằng nội suy tới một trong năm láng giềng gần nhất cùng lớp [@chawla2002]; (v) **trọng số lớp** — mỗi lớp nhận tổng trọng số bằng nhau. Bốn cách cuối đều đưa tỷ lệ "hiệu dụng" của lớp mắc trong tập huấn luyện lên 50 %.

## 2.3. Hai cách vận hành dịch vụ

**Theo năng lực.** Dịch vụ chỉ đánh giá được K % số trẻ được sàng lọc (K = 2, 5 hoặc 10 %) và nhận K % trẻ có điểm cao nhất. Cách này chỉ dùng **thứ hạng** nên không phụ thuộc thang điểm. Chỉ số là **số ca thật trên 100 lượt đánh giá** (giá trị dự báo dương ở mức năng lực K) và độ nhạy — tỷ lệ trẻ mắc được đưa vào danh sách. Khi nhiều trẻ trùng điểm ở ranh giới năng lực, chúng tôi tính kỳ vọng của việc bốc thăm ngẫu nhiên trong nhóm trùng điểm. Mốc so sánh là đánh giá ngẫu nhiên: 2 ca thật trên 100 lượt.

**Theo ngưỡng nguy cơ.** Trẻ được chuyển khi nguy cơ hiển thị từ ngưỡng $p_t$ trở lên, $p_t \in \{2, 5, 10\,\%\}$. Ngưỡng mã hóa đánh đổi mà dịch vụ chấp nhận: chọn $p_t = 5\,\%$ nghĩa là chấp nhận đánh giá tối đa 19 trẻ không mắc để phát hiện một trẻ mắc [@wynants2019]. Chúng tôi báo cáo tỷ lệ trẻ bị chuyển — thước đo trực tiếp của **tải** lên danh sách chờ — và lợi ích ròng theo phân tích đường cong quyết định [@vickers2006; @vickers2016]:

$$\mathrm{NB}(p_t) = \frac{\mathrm{TP}}{n} - \frac{\mathrm{FP}}{n} \cdot \frac{p_t}{1 - p_t}, \qquad (1)$$

với TP và FP là số trẻ được chuyển có và không có rối loạn, $n$ là số trẻ được sàng lọc. Hai chiến lược tham chiếu là "không chuyển ai" (NB = 0) và "chuyển tất cả" (NB = $\pi - (1-\pi)\,p_t/(1-p_t)$, với $\pi = 0{,}02$; bằng đúng 0 khi $p_t = 2\,\%$). Một quy tắc chỉ có giá trị ở ngưỡng $p_t$ nếu lợi ích ròng của nó vượt cả hai chiến lược tham chiếu.

## 2.4. Con số nói với gia đình

Để mô phỏng cách trao đổi kết quả, nguy cơ được chia thành bốn dải: dưới 1 %, 1–5 %, 5–20 % và từ 20 % trở lên — một quy ước minh họa của nghiên cứu, không phải chuẩn lâm sàng. Với mỗi cách huấn luyện, chúng tôi đo tỷ trọng trẻ trong mỗi dải và tỷ lệ mắc thật trong dải, viết dưới dạng tần suất tự nhiên "trên 1 000 trẻ" vốn dễ hiểu hơn xác suất có điều kiện đối với cả nhà chuyên môn lẫn gia đình [@gigerenzer1995]. Một dải là trung thực nếu số trẻ mắc thật trên 1 000 nằm trong khoảng mà tên dải hứa hẹn.

## 2.5. Kiểm tra và sửa thang trước khi triển khai

Chúng tôi giả định dịch vụ nhận một mô hình đã huấn luyện xong và so sánh năm cách xử lý đầu ra $p$ của nó. Kí hiệu $\sigma(z) = 1/(1+e^{-z})$ và $\mathrm{logit}(p) = \ln[p/(1-p)]$.

(a) **Dùng nguyên xác suất** của mô hình.

(b) **Hiệu chỉnh tiên nghiệm** [@elkan2001; @saerens2002]. Nếu nhà cung cấp khai báo tỷ lệ mắc gốc $\pi$ của tập huấn luyện và tỷ lệ sau cân bằng $\pi_s$ (ở đây 0,5), xác suất được đổi về tỷ lệ gốc bằng công thức Bayes

$$p' = \frac{p\,\pi/\pi_s}{p\,\pi/\pi_s + (1-p)(1-\pi)/(1-\pi_s)}. \qquad (2)$$

Công thức (2) đúng khi việc cân bằng lại chỉ làm dịch xác suất tiên nghiệm và mô hình ước lượng đúng xác suất có điều kiện dưới tỷ lệ $\pi_s$. Nó không cần nhãn nhưng cần thông tin mà nhà cung cấp thường không công bố.

(c) **Khớp trung bình** (không cần nhãn, không cần thông tin từ nhà cung cấp). Dịch vụ chạy công cụ trên chính quần thể trẻ của mình (không cần biết trẻ nào mắc) và chọn một độ dịch log-odds $\delta$ sao cho nguy cơ trung bình bằng tỷ lệ mắc $\hat\pi$ mà dịch vụ ước tính từ số liệu dịch tễ:

$$\frac{1}{n}\sum_{i=1}^{n} \sigma\big(\mathrm{logit}(p_i) + \delta\big) = \hat\pi, \qquad p_i' = \sigma\big(\mathrm{logit}(p_i) + \delta\big). \qquad (3)$$

Để đo hậu quả của ước tính sai tỷ lệ mắc, chúng tôi dùng $\hat\pi$ = 2 % (đúng), 1 % và 4 % (sai gấp đôi theo hai chiều).

(d) **Cập nhật hệ số chặn** trên $n$ hồ sơ có nhãn tại chỗ [@steyerberg2004; @janssen2008]: như (3) nhưng $\delta$ được chọn sao cho tổng nguy cơ bằng số trẻ mắc quan sát trong mẫu — đây chính là ước lượng hợp lý cực đại của hệ số chặn khi giữ nguyên hệ số góc.

(e) **Khớp lại Platt** trên cùng $n$ hồ sơ: hồi quy logistic của nhãn theo $\mathrm{logit}(p)$ (phạt L2 mặc định), học cả hệ số chặn và hệ số góc.

Mẫu có nhãn gồm $n \in \{100, 200, 500\}$ hồ sơ rút từ phần triển khai dành riêng, số trẻ mắc ngẫu nhiên theo phân phối nhị thức (trung bình {{NPOS_100}}, {{NPOS_200}} và {{NPOS_500}} trẻ mắc), như khi dịch vụ lấy $n$ hồ sơ liên tiếp đã có kết quả đánh giá chuyên sâu. Các phép (b)–(d) là biến đổi tăng nghiêm ngặt nên **không đổi thứ hạng**; kết quả ở chế độ năng lực vì vậy không phụ thuộc cách sửa.

## 2.6. Chỉ số và phân tích thống kê

**Nguy cơ trung bình** so với tỷ lệ mắc thật đo độ lệch tổng thể — tầng thấp nhất của phân cấp hiệu chỉnh [@vancalster2016]. **Sai số hiệu chỉnh kỳ vọng** (ECE) chia quần thể thành 10 nhóm theo phân vị của nguy cơ và lấy trung bình có trọng số của độ lệch giữa nguy cơ trung bình và tỷ lệ mắc quan sát trong mỗi nhóm. **Hệ số góc hiệu chỉnh** là hệ số của $\mathrm{logit}(p)$ trong hồi quy logistic không phạt của nhãn theo $\mathrm{logit}(p)$; giá trị 1 là lý tưởng, nhỏ hơn 1 nghĩa là nguy cơ **quá phân tán** (quá cao ở trẻ điểm cao và quá thấp ở trẻ điểm thấp) — một biến dạng về **hình dạng** mà không phép dịch nào sửa được. **Điểm Brier** [@brier1950] và PR-AUC (diện tích dưới đường cong độ chính xác – độ nhạy) được dùng ở lưới chính.

Mọi chỉ số là trung bình qua {{NREP}} lần lặp; mỗi lần lặp rút lại tập huấn luyện và các mẫu có nhãn, còn quần thể triển khai giữ cố định. Với mỗi mô hình, chúng tôi so sánh từng cách huấn luyện (và từng cách sửa thang) với cách nguyên trạng bằng hiệu số ghép cặp theo lần lặp và kiểm định t một mẫu. Họ phép kiểm gồm {{NTESTS_TL}} so sánh (số ca thật trên 100 lượt ở ba mức năng lực; lợi ích ròng của đầu ra thô, sau hiệu chỉnh tiên nghiệm và sau khớp trung bình ở ba ngưỡng), được hiệu chỉnh so sánh bội bằng thủ tục Benjamini–Hochberg ở mức tỷ lệ phát hiện sai 0,05 [@benjamini1995]; họ này có giữ 6 so sánh tầm thường (hiệu chỉnh tiên nghiệm của mô hình nguyên trạng là phép đồng nhất), làm thủ tục bảo thủ hơn một chút. Hạt giống ngẫu nhiên được cố định và ghi lại cùng dấu vân tay của mã nguồn; chạy lại cho kết quả trùng từng byte (mục Dữ liệu và mã nguồn).

## 2.7. Công cụ kiểm tra đầu ra

Từ kết quả của mục 2.5, chúng tôi viết một công cụ dòng lệnh chỉ phụ thuộc thư viện numpy. Đầu vào là tệp CSV điểm của công cụ sàng lọc trên các trẻ tại chỗ (có hoặc không có nhãn), tỷ lệ mắc ước tính và năng lực của dịch vụ. Công cụ báo: (1) **hệ số thổi phồng** — nguy cơ trung bình chia cho tỷ lệ mắc, cảnh báo khi vượt 1,5; (2) tỷ lệ trẻ bị chuyển ở mỗi ngưỡng, so với năng lực; (3) điểm cắt tương ứng với năng lực và số trẻ trùng điểm ở ranh giới; (4) thang sau khớp trung bình (hoặc hiệu chỉnh tiên nghiệm nếu có thông tin từ nhà cung cấp) và bảng dải nguy cơ trước – sau; (5) nếu có nhãn: tỷ lệ mắc quan sát kèm khoảng tin cậy Wilson 95 %, hệ số góc hiệu chỉnh (chỉ khi có ít nhất 10 trẻ mắc) và lợi ích ròng trước – sau. Các ngưỡng cảnh báo là quy ước rút ra từ mô phỏng, không phải chuẩn lâm sàng.

# 3. KẾT QUẢ

## 3.1. Lưới chính: cân bằng lại hầu như không giúp phân biệt nhưng luôn làm hỏng xác suất

Bảng 1 tóm tắt lưới chính của nghiên cứu đi kèm ở tỷ lệ mắc 2 % ({{G_NREP}} lần lặp, tập kiểm thử {{G_NTEST}} hồ sơ mỗi tỷ lệ; {{G_NCONF}} cấu hình, {{G_NTESTS}} phép kiểm có hiệu chỉnh Benjamini–Hochberg). Trên cả bốn tỷ lệ mắc và bốn mô hình, bốn cách cân bằng lại làm điểm Brier xấu đi có ý nghĩa ở {{G_BRIER_WORSE}} ô. PR-AUC chỉ tăng có ý nghĩa ở {{G_PR_UP}} ô — tất cả thuộc Fuzzy k-NN (một mô hình gần như không phân biệt được trên dữ liệu này) hoặc rừng ngẫu nhiên với lấy mẫu thiếu, mức tăng lớn nhất {{G_PR_UP_MAX}} phần nghìn — và giảm có ý nghĩa ở {{G_PR_DOWN}} ô. Lợi ích ròng ở ngưỡng 2 % giảm có ý nghĩa ở {{G_NB_DOWN}}/{{G_NB_N}} ô và tăng ở {{G_NB_UP}} ô, chủ yếu ở Fuzzy k-NN và ở tỷ lệ mắc 5 %, nơi "chuyển tất cả" đã là chiến lược tốt ở ngưỡng 2 %. Hồi quy logistic và mô hình lai huấn luyện sau cân bằng lại gắn cờ gần như mọi trẻ ở cả bốn tỷ lệ mắc.

**Bảng 1.** *Lưới chính ở tỷ lệ mắc 2 %: PR-AUC, điểm Brier, tỷ lệ trẻ bị chuyển và lợi ích ròng với quy tắc "chuyển khi nguy cơ ≥ 2 %". Dịch chuyển ngưỡng dùng đúng mô hình nguyên trạng, chỉ chọn lại điểm cắt trên một tập hiệu chỉnh 2 000 hồ sơ, nên PR-AUC và Brier của nó trùng với nguyên trạng theo xây dựng. Trung bình {{G_NREP}} lần lặp. Mốc: Brier của dự báo hằng số 0,02 là 19,6 phần nghìn; PR-AUC của dự báo ngẫu nhiên là 20 phần nghìn.*

{{TABLE1}}

Phần còn lại của mục Kết quả đi sâu vào hồi quy logistic và rừng ngẫu nhiên — hai mô hình có năng lực phân biệt thực (AUC khoảng {{G:0.02|RF|N0|roc_auc|d2}}–{{G:0.02|LR|N0|roc_auc|d2}}) và phổ biến nhất trong thực hành.

## 3.2. Con số nói với gia đình

Cân bằng lại làm nguy cơ trung bình của hồi quy logistic tăng lên {{INFL_LR_RUS}} lần (lấy mẫu thiếu), {{INFL_LR_ROS}} lần (lấy mẫu thừa), {{INFL_LR_SMOTE}} lần (SMOTE) và {{INFL_LR_CW}} lần (trọng số lớp) so với tỷ lệ mắc thật; với rừng ngẫu nhiên, hệ số tương ứng là {{INFL_RF_RUS}}, {{INFL_RF_ROS}}, {{INFL_RF_SMOTE}} và {{INFL_RF_CW}}. Bảng 2 và Hình 1 chuyển điều này sang ngôn ngữ tư vấn.

**Bảng 2.** *Hồi quy logistic, tỷ lệ mắc 2 %: số trẻ trên 1 000 được xếp vào mỗi dải nguy cơ và số trẻ trên 1 000 trong dải đó thật sự có rối loạn. Trung bình {{NREP}} lần lặp trên quần thể {{NEVAL}} trẻ; "—": không có trẻ nào trong dải.*

{{TABLE2}}

![**Hình 1.** Dải nguy cơ của hồi quy logistic ở tỷ lệ mắc 2 %. (a) Huấn luyện nguyên trạng: phần lớn trẻ ở dải 1–5 %, và tỷ lệ mắc thật trong mỗi dải nằm trong khoảng tên dải hứa hẹn. (b) Huấn luyện sau SMOTE: {{T1:LR|SMOTE|raw|>=20%|share|p1}} số trẻ bị báo "từ 20 % trở lên" trong khi chỉ {{T1:LR|SMOTE|raw|>=20%|obs|k0}}/1 000 trẻ trong nhóm này thật sự mắc. (c) Sau khớp trung bình theo tỷ lệ mắc 2 %, các dải trở lại trung thực mà không dùng nhãn nào.](p11tl_fig1.png){width=16cm}

Ở cột nguyên trạng, các dải trung thực: trong 1 000 trẻ được báo "1–5 %", khoảng {{T1:LR|N0|raw|1-5%|obs|k0}} trẻ mắc, và trong 1 000 trẻ ở dải "5–20 %", khoảng {{T1:LR|N0|raw|5-20%|obs|k0}} trẻ. Sau SMOTE, cứ 1 000 trẻ được sàng lọc thì {{LR_SM_HI_1000}} trẻ bị báo "từ 20 % trở lên", nhưng tỷ lệ mắc thật trong nhóm đó ({{T1:LR|SMOTE|raw|>=20%|obs|k0}}/1 000) gần như bằng tỷ lệ mắc của cả cộng đồng. Nói cách khác, dải nguy cơ "cao" không còn chứa thông tin gì về đứa trẻ cụ thể, nhưng vẫn truyền tới gia đình một thông điệp đáng lo ngại. Khớp trung bình theo tỷ lệ 2 % (cột cuối) đưa phân bố dải về gần cột nguyên trạng.

## 3.3. Dịch vụ theo năng lực: cân bằng lại không giúp tìm thêm ca thật

Khi dịch vụ nhận K % trẻ điểm cao nhất, hồi quy logistic nguyên trạng tìm được {{T2:LR|N0|cap|0.05|ppv|c2}} ca thật trên 100 lượt đánh giá ở K = 5 % — gấp {{LIFT_LR_5}} lần đánh giá ngẫu nhiên (Bảng 3, Hình 2). Lấy mẫu thừa, SMOTE và trọng số lớp không làm thay đổi có ý nghĩa con số này ({{LR_CAP_NS}} so sánh không có ý nghĩa sau hiệu chỉnh bội); lấy mẫu thiếu làm nó giảm nhẹ nhưng có ý nghĩa (q ≤ {{Q_LR_RUS_CAP}}), vì mô hình chỉ còn 200 hồ sơ để học. Với rừng ngẫu nhiên, lấy mẫu thừa, SMOTE và trọng số lớp làm **giảm** số ca thật trên 100 lượt ở mọi mức năng lực ({{RF_CAP_SIG}} so sánh có ý nghĩa), từ {{RF_CAP5_LOSS_MIN}} đến {{RF_CAP5_LOSS_MAX}} ca ở K = 5 %. Quy về 10 000 trẻ được sàng lọc, với cùng 500 lượt đánh giá, SMOTE làm dịch vụ bỏ lỡ thêm khoảng {{RF_CAP5_MISSED}} trẻ mắc. Ngoại lệ duy nhất là lấy mẫu thiếu với rừng ngẫu nhiên, tăng từ {{T2:RF|N0|cap|0.05|ppv|c2}} lên {{T2:RF|RUS|cap|0.05|ppv|c2}} ca ở K = 5 % (q = {{Q_RF_RUS_CAP5}}): mỗi cây học trên một tập nhỏ, cân bằng hơn, và rừng ít học thuộc hơn — một cơ chế điều chuẩn, không phải lợi ích riêng của "cân bằng".

**Bảng 3.** *Số ca thật trên 100 lượt đánh giá (trung bình ± độ lệch chuẩn qua {{NREP}} lần lặp) khi dịch vụ nhận K % trẻ có điểm cao nhất, và độ nhạy ở K = 5 %. \*: khác nguyên trạng có ý nghĩa sau hiệu chỉnh Benjamini–Hochberg. Mốc: đánh giá ngẫu nhiên cho 2 ca thật trên 100 lượt.*

{{TABLE3}}

![**Hình 2.** Số ca thật trên 100 lượt đánh giá khi dịch vụ nhận 5 % (a) hoặc 10 % (b) số trẻ được sàng lọc có điểm cao nhất; thanh sai số là độ lệch chuẩn qua {{NREP}} lần lặp. Đường đứt: đánh giá ngẫu nhiên.](p11tl_fig2.png){width=16cm}

## 3.4. Dịch vụ theo ngưỡng nguy cơ: danh sách chờ bùng nổ

Bảng 4 và Hình 3 cho thấy điều xảy ra khi dịch vụ áp một ngưỡng nguy cơ lên xác suất mà công cụ xuất ra. Với hồi quy logistic huấn luyện sau bất kỳ cách cân bằng lại nào, tỷ lệ trẻ bị chuyển ở ngưỡng 2 % và 5 % không dưới {{LR_REFER_MIN}}: quy tắc suy biến thành "chuyển tất cả", với lợi ích ròng đúng bằng của chiến lược đó ({{NB_ALL_5}} phần nghìn ở ngưỡng 5 %, tức tệ hơn không chuyển ai). Ở ngưỡng 10 %, hồi quy logistic sau cân bằng lại vẫn chuyển {{T2:LR|SMOTE|raw|0.1|refer|p1}} số trẻ. Một dịch vụ có năng lực 5 % sẽ nhận một danh sách dài gấp khoảng hai mươi lần năng lực của mình. Rừng ngẫu nhiên sau SMOTE chuyển {{T2:RF|SMOTE|raw|0.05|refer|p1}} số trẻ ở ngưỡng 5 %, với lợi ích ròng {{T2:RF|SMOTE|raw|0.05|nb|k2}} phần nghìn so với {{T2:RF|N0|raw|0.05|nb|k2}} của mô hình nguyên trạng.

**Bảng 4.** *Tỷ lệ trẻ bị chuyển · lợi ích ròng ×1 000 với quy tắc "chuyển khi nguy cơ ≥ p~t~", tỷ lệ mắc 2 %. Trung bình {{NREP}} lần lặp. Lợi ích ròng dương và lớn hơn của "chuyển tất cả" nghĩa là quy tắc có ích ở ngưỡng đó.*

{{TABLE4}}

![**Hình 3.** Đường cong quyết định ở tỷ lệ mắc 2 %: (a) hồi quy logistic, (b) rừng ngẫu nhiên. Với hồi quy logistic, đường của SMOTE thô trùng với "chuyển tất cả"; hiệu chỉnh tiên nghiệm và khớp trung bình trùng với đường nguyên trạng. Với rừng ngẫu nhiên, không cách sửa thang nào đưa SMOTE về đường nguyên trạng.](p11tl_fig3.png){width=16cm}

## 3.5. Sửa thang trước khi dùng: được với hồi quy logistic, không được với rừng ngẫu nhiên

Bảng 5 so sánh các cách xử lý đầu ra của hai mô hình huấn luyện sau SMOTE.

**Bảng 5.** *Sửa thang của mô hình huấn luyện sau SMOTE, tỷ lệ mắc 2 %: nguy cơ trung bình (đúng: 0,0200), ECE (trung bình ± độ lệch chuẩn qua {{NREP}} lần lặp), hệ số góc hiệu chỉnh (lý tưởng: 1; không báo cho Platt vì không ổn định khi hệ số khớp gần 0), tỷ lệ trẻ bị chuyển và lợi ích ròng ở ngưỡng 5 %. Hàng cuối mỗi mô hình là mốc huấn luyện nguyên trạng, dùng nguyên xác suất.*

{{TABLE5}}

**Hồi quy logistic: sửa được, và không cần nhãn.** Với hồi quy logistic, cân bằng lại chủ yếu làm dịch hệ số chặn: hệ số góc hiệu chỉnh vẫn quanh 1 ở mọi cách huấn luyện ({{LR_SLOPE_MIN}}–{{LR_SLOPE_MAX}}), tức thang bị dịch chứ không bị kéo giãn. Hiệu chỉnh tiên nghiệm đưa ECE về {{LR_PC_ECE_MIN}}–{{LR_PC_ECE_MAX}} phần nghìn, khớp trung bình về {{LR_MM_ECE_MIN}}–{{LR_MM_ECE_MAX}} phần nghìn ở cả bốn cách cân bằng lại, và lợi ích ròng sau hai phép sửa này chênh với mô hình nguyên trạng không quá {{LR_REPAIR_MAXDIFF}} phần nghìn ở cả ba ngưỡng — nhỏ hơn nhiều so với độ lớn của các quyết định được bàn ở đây, dù một vài hiệu số rất nhỏ vẫn có ý nghĩa thống kê nhờ thiết kế ghép cặp.

**Rừng ngẫu nhiên: không sửa được bằng phép dịch.** Sau lấy mẫu thừa, SMOTE và trọng số lớp, hệ số góc hiệu chỉnh của rừng ngẫu nhiên chỉ còn {{RF_SLOPE_MIN}}–{{RF_SLOPE_MAX}} (so với {{RF_N0_SLOPE}} ở mô hình nguyên trạng, vốn cũng đã quá phân tán): các cây học thuộc những trẻ mắc được nhân bản hoặc nội suy, nên xác suất không chỉ bị dịch mà còn bị kéo giãn. Hiệu chỉnh tiên nghiệm khi đó **sửa quá tay**: nguy cơ trung bình rơi xuống {{T3:RF|SMOTE|pc|mean_p|d4}}, tỷ lệ chuyển ở ngưỡng 2 % chỉ còn {{T2:RF|SMOTE|pc|0.02|refer|p1}} và lợi ích ròng {{T2:RF|SMOTE|pc|0.02|nb|k2}} so với {{T2:RF|N0|raw|0.02|nb|k2}} phần nghìn của mô hình nguyên trạng. Khớp trung bình đưa nguy cơ trung bình về đúng 0,0200 nhưng không sửa được hình dạng: ECE vẫn {{RF_MM_ECE_MIN}}–{{RF_MM_ECE_MAX}} phần nghìn và lợi ích ròng ở ngưỡng 5 % âm. Ngoại lệ đáng chú ý là rừng ngẫu nhiên với **lấy mẫu thiếu**: hệ số góc {{T3:RF|RUS|raw|slope|d2}}, và sau hiệu chỉnh tiên nghiệm, lợi ích ròng ở ngưỡng 2 % là {{T2:RF|RUS|pc|0.02|nb|k2}} phần nghìn — cao hơn mô hình nguyên trạng một cách có ý nghĩa, phù hợp với {@dalpozzolo2015}.

**Ước tính sai tỷ lệ mắc.** Khớp trung bình cần một ước tính tỷ lệ mắc. Với hồi quy logistic sau SMOTE, dùng 4 % thay cho 2 % làm tỷ lệ chuyển ở ngưỡng 5 % tăng lên {{T2:LR|SMOTE|mm_0.04|0.05|refer|p1}} và lợi ích ròng thành âm ({{T2:LR|SMOTE|mm_0.04|0.05|nb|k2}}); dùng 1 % làm tỷ lệ chuyển giảm còn {{T2:LR|SMOTE|mm_0.01|0.05|refer|p1}} với lợi ích ròng {{T2:LR|SMOTE|mm_0.01|0.05|nb|k2}} (so với {{T2:LR|SMOTE|mm_0.02|0.05|nb|k2}} khi dùng tỷ lệ đúng). Ở các ngưỡng từ 5 % trở lên, đánh giá thấp tỷ lệ mắc gây hại ít hơn đánh giá cao.

**Ít nhãn tại chỗ không tốt hơn một tỷ lệ mắc đáng tin.** Với hồi quy logistic sau SMOTE, cập nhật hệ số chặn trên 100 hoặc 200 hồ sơ có nhãn — chỉ khoảng {{NPOS_100}} và {{NPOS_200}} trẻ mắc — cho ECE {{T3:LR|SMOTE|icpt_100|ece|k1}} và {{T3:LR|SMOTE|icpt_200|ece|k1}} phần nghìn, kém hơn khớp trung bình theo tỷ lệ đúng ({{T3:LR|SMOTE|mm_0.02|ece|k1}}), vì số trẻ mắc trong một mẫu nhỏ dao động mạnh theo phân phối nhị thức. Với hồi quy logistic, khớp lại Platt đầy đủ còn kém hơn và bấp bênh: hệ số góc Platt ra âm — tức phép sửa **đảo ngược** thứ hạng — ở {{PLATT_NEG_100}} lần khớp với n = 100, {{PLATT_NEG_200}} với n = 200 và {{PLATT_NEG_500}} với n = 500; ở n = 100, {{SKIP_100}} lần lặp không có trẻ mắc nào trong mẫu nên không khớp được. Với 500 hồ sơ (khoảng {{NPOS_500}} trẻ mắc), cập nhật hệ số chặn thu hẹp khoảng cách ({{T3:LR|SMOTE|icpt_500|ece|k1}} phần nghìn) nhưng vẫn chưa bằng khớp trung bình theo tỷ lệ mắc đúng. Với rừng ngẫu nhiên sau SMOTE, khớp lại Platt trên 500 hồ sơ là cách duy nhất trong Bảng 5 sửa được phần lớn biến dạng hình dạng (ECE {{T3:RF|SMOTE|platt_500|ece|k1}} phần nghìn), nhưng lợi ích ròng ở ngưỡng 5 % vẫn chỉ {{T2:RF|SMOTE|platt_500|0.05|nb|k2}} so với {{T2:RF|N0|raw|0.05|nb|k2}} của mô hình nguyên trạng: hiệu chỉnh không trả lại được phần thứ hạng đã mất ở mục 3.3.

## 3.6. Công cụ kiểm tra trên ba nhà cung cấp giả định

Chúng tôi chạy công cụ ở mục 2.7 trên ba mô hình giả định, năng lực dịch vụ 5 %. **Nhà cung cấp A** (hồi quy logistic sau SMOTE, dịch vụ chỉ có 5 000 điểm không nhãn): công cụ báo hệ số thổi phồng {{DA_INFL}}, tỷ lệ chuyển ở ngưỡng 5 % là {{DA_REF5}} (vượt năng lực), và sau khớp trung bình tỷ lệ này còn {{DA_REF5_AFTER}}; số trẻ trên 1 000 ở dải "từ 20 %" giảm từ {{DA_HI_BEFORE}} xuống {{DA_HI_AFTER}}. **Nhà cung cấp B** (rừng ngẫu nhiên sau SMOTE, có 1 000 hồ sơ có nhãn với {{DB_NPOS}} trẻ mắc): hệ số thổi phồng {{DB_INFL}}; sau khớp trung bình, lợi ích ròng ở ngưỡng 5 % tăng từ {{DB_NB5_BEFORE}} lên {{DB_NB5_AFTER}} phần nghìn, nhưng hệ số góc hiệu chỉnh chỉ {{DB_SLOPE}} và công cụ cảnh báo biến dạng hình dạng — tức cần yêu cầu mô hình không cân bằng lại. **Nhà cung cấp C** (hồi quy logistic nguyên trạng, cùng 1 000 hồ sơ có nhãn): hệ số thổi phồng {{DC_INFL}}, hệ số góc {{DC_SLOPE}}, tỷ lệ mắc dự kiến 2 % nằm trong khoảng tin cậy Wilson {{DC_LO}}–{{DC_HI}}; cảnh báo duy nhất là ở ngưỡng 5 % quy tắc chuyển {{DC_REF5}} số trẻ, vượt năng lực 5 % — một quyết định về ngưỡng mà dịch vụ phải tự đưa ra, không phải lỗi của công cụ.

# 4. BÀN LUẬN

## 4.1. Ý nghĩa cho dịch vụ tâm lý

Kết quả có thể tóm thành một câu: **cân bằng lại dữ liệu huấn luyện là quyết định kỹ thuật của nhà phát triển, nhưng hậu quả của nó rơi vào phòng tư vấn và danh sách chờ.** Ba hậu quả cụ thể là:

*Thứ nhất, con số nói với gia đình mất nghĩa.* Một công cụ huấn luyện sau SMOTE xếp phần lớn trẻ vào dải nguy cơ "cao" mà không có trẻ nào ở dải thấp (Bảng 2). Nếu con số đó được đọc cho cha mẹ, hầu hết gia đình ra về với một mức lo âu không tương xứng với nguy cơ thật — một tác hại tâm lý mà các hướng dẫn truyền đạt nguy cơ cố gắng tránh [@zipkin2014; @spiegelhalter2017]. Ngược lại, khi hầu như mọi trẻ đều bị gắn cờ, cảnh báo mất tác dụng với chính nhà chuyên môn — hiện tượng mệt mỏi vì cảnh báo đã được mô tả ở các hệ hỗ trợ quyết định lâm sàng [@ancker2017].

*Thứ hai, danh sách chờ bị quyết định bởi thang điểm chứ không bởi năng lực.* Nếu dịch vụ áp một ngưỡng nguy cơ lên đầu ra của mô hình đã cân bằng lại, số trẻ bị chuyển có thể gấp hàng chục lần năng lực (Bảng 4). Trong thực tế điều này hiếm khi dẫn tới việc đánh giá tất cả; nó dẫn tới hàng chờ dài, thứ tự phục vụ theo ngày đăng ký thay vì theo nguy cơ, và mất đi chính lợi ích mà công cụ được mua để mang lại.

*Thứ ba, cân bằng lại không mua được thêm ca thật.* Khi dịch vụ nhận trẻ theo năng lực — cách vận hành duy nhất không phụ thuộc thang điểm — cân bằng lại không giúp hồi quy logistic và làm rừng ngẫu nhiên kém đi, trừ lấy mẫu thiếu (Bảng 3). Nhận định "cân bằng lại để mô hình nhạy hơn với lớp thiểu số" nhầm lẫn giữa **độ nhạy ở một điểm cắt mặc định 0,5** và **khả năng xếp hạng**: với hồi quy logistic, cân bằng lại về thực chất chỉ dời điểm cắt — điều mà dịch vụ có thể làm trực tiếp bằng cách chọn ngưỡng hoặc năng lực; với rừng ngẫu nhiên, nó còn làm hỏng chính thứ hạng.

Từ đó, chúng tôi đề xuất sáu câu hỏi mà một dịch vụ tâm lý nên đặt cho nhà cung cấp trước khi triển khai (Bảng 6). Các câu hỏi không đòi hỏi nhà tâm lý hiểu thuật toán; chúng đòi hỏi nhà cung cấp minh bạch về những gì đã làm với dữ liệu, và cho phép dịch vụ tự kiểm tra bằng công cụ ở mục 2.7.

**Bảng 6.** *Sáu câu hỏi dịch vụ tâm lý nên đặt cho nhà cung cấp công cụ sàng lọc, và cách dùng câu trả lời.*

| Câu hỏi | Vì sao hỏi | Nếu câu trả lời là… |
|:------------------------------|:------------------------------|:------------------------------|
| 1\. Mô hình có được huấn luyện trên dữ liệu đã cân bằng lại (lấy mẫu thiếu/thừa, SMOTE, trọng số lớp) không? | Cân bằng lại làm thổi phồng mọi xác suất (mục 3.2). | "Có": không đọc xác suất cho gia đình trước khi sửa thang. |
| 2\. Tỷ lệ mắc trong dữ liệu huấn luyện gốc và sau cân bằng là bao nhiêu? | Cần cho hiệu chỉnh tiên nghiệm, công thức (2). | Không có thông tin: dùng khớp trung bình, công thức (3). |
| 3\. Mô hình là loại gì? | Hồi quy logistic sửa được bằng phép dịch; rừng ngẫu nhiên sau lấy mẫu thừa, SMOTE hoặc trọng số lớp thì không (mục 3.5). | Mô hình dạng cây sau lấy mẫu thừa, SMOTE hoặc trọng số lớp: yêu cầu phiên bản không cân bằng lại, hoặc lấy mẫu thiếu kèm hiệu chỉnh tiên nghiệm. |
| 4\. Công cụ đã được kiểm tra hiệu chỉnh ở tỷ lệ mắc nào? | Tỷ lệ mắc cộng đồng khác tỷ lệ trong mẫu phát triển. | Không ở tỷ lệ cộng đồng: tự chạy công cụ kiểm tra trên điểm không nhãn của dịch vụ. |
| 5\. Ngưỡng chuyển mặc định là bao nhiêu và tương ứng với bao nhiêu phần trăm trẻ? | Tải chuyển phải khớp năng lực đánh giá. | Vượt năng lực: chọn lại ngưỡng, hoặc vận hành theo năng lực (nhận K % điểm cao nhất). |
| 6\. Có cần nhãn tại chỗ không, và bao nhiêu? | Dưới vài trăm hồ sơ có nhãn, cập nhật kém hơn một tỷ lệ mắc đáng tin (mục 3.5). | Ưu tiên một ước tính tỷ lệ mắc đáng tin; chỉ cân nhắc khớp lại khi có từ khoảng 500 hồ sơ và ít nhất 10 trẻ mắc. |

## 4.2. Vì sao hồi quy logistic sửa được còn rừng ngẫu nhiên thì không

Với một mô hình ước lượng đúng xác suất có điều kiện, cân bằng lại tập huấn luyện chỉ thay xác suất tiên nghiệm; trên thang log-odds, điều đó là một phép cộng hằng số, và công thức (2) hay (3) trừ lại đúng hằng số đó [@elkan2001; @saerens2002]. Hồi quy logistic gần với giả định này: trọng số lớp và lấy mẫu thừa gần như chỉ thay hệ số chặn. Rừng ngẫu nhiên thì không. Lấy mẫu thừa và SMOTE đặt nhiều bản sao hoặc gần-bản-sao của cùng một trẻ mắc vào tập huấn luyện; các lá của cây trở nên "tinh khiết" quanh những điểm đó, và xác suất ra khỏi rừng bị đẩy về hai đầu. Biến dạng này là **hình dạng**, thể hiện ở hệ số góc hiệu chỉnh xa 1, và không phép dịch đơn điệu nào — kể cả công thức Bayes đúng về lý thuyết — sửa được; hiệu chỉnh tiên nghiệm còn sửa quá tay vì giả định của nó bị vi phạm. Kết quả này thống nhất với các mô phỏng của {@vandengoorbergh2022} cho hồi quy logistic và {@carriero2025} cho học máy, và với khuyến nghị kết hợp lấy mẫu thiếu với hiệu chỉnh tiên nghiệm cho mô hình dạng cây của {@dalpozzolo2015}.

## 4.3. Đặt trong bối cảnh

Nghiên cứu thực địa ở Việt Nam [@vo2026] báo cáo rừng ngẫu nhiên với SMOTE có AUC rất cao; nghiên cứu mô phỏng này không phản bác kết quả đó — dữ liệu và mô hình khác nhau — nhưng gợi ý rằng khi đưa một mô hình như vậy vào dịch vụ, cần báo cáo thêm tỷ lệ trẻ bị chuyển, lợi ích ròng ở ngưỡng mà dịch vụ thực sự dùng, và hiệu chỉnh ở tỷ lệ mắc cộng đồng. Bài học tương tự từ M-CHAT-R/F: giá trị dự báo dương gộp ở cộng đồng thấp hơn đáng kể so với các mẫu có tỷ lệ mắc cao [@aishworiya2023]. Nghiên cứu đi kèm về hiệu chỉnh xác suất [@nhom2026p9] cho thấy điểm của hệ suy diễn mờ cũng không phải xác suất; bài này bổ sung một nguồn sai lệch khác, có thể xuất hiện ở bất kỳ mô hình học máy nào và do chính quá trình huấn luyện gây ra.

## 4.4. Hạn chế

Thứ nhất, mọi kết quả đến từ **dữ liệu tổng hợp**: các hiện tượng cơ học (thổi phồng, suy biến thành "chuyển tất cả", hiệu chỉnh tiên nghiệm đúng cho mô hình dạng hồi quy) không phụ thuộc bộ sinh, nhưng độ lớn cụ thể — số ca thật trên 100 lượt, mức giảm của rừng ngẫu nhiên — phụ thuộc cấu trúc dữ liệu mô phỏng và có thể khác trên trẻ thật. Thứ hai, năng lực phân biệt của cả hai mô hình trên dữ liệu này chỉ ở mức trung bình (AUC khoảng {{G:0.02|RF|N0|roc_auc|d2}}–{{G:0.02|LR|N0|roc_auc|d2}}); với mô hình phân biệt tốt hơn, khoảng cách giữa các cách vận hành có thể khác. Thứ ba, chúng tôi chỉ xét một tỷ lệ mắc (2 %) ở ba phân tích mới và hai mô hình; lưới đầy đủ ở nghiên cứu đi kèm xét bốn tỷ lệ và bốn mô hình. Thứ tư, siêu tham số được cố định (200 cây, 5 hồ sơ mỗi lá); một rừng ngẫu nhiên được điều chuẩn mạnh hơn có thể ít quá phân tán hơn. Thứ năm, "nhãn" trong mẫu kiểm tra được giả định là kết quả đánh giá chuyên sâu không sai; trong thực tế nhãn cũng có sai số và thường chỉ có ở trẻ đã được chuyển (thiên lệch xác minh), làm cập nhật trên nhãn tại chỗ còn khó hơn mức mô phỏng. Thứ sáu, bốn dải nguy cơ, các mức năng lực và các ngưỡng cảnh báo của công cụ là quy ước minh họa; một dịch vụ cụ thể nên thay bằng quy ước của mình. Cuối cùng, nghiên cứu không đo tác động tâm lý thực sự lên gia đình; lập luận về lo âu và mệt mỏi vì cảnh báo dựa trên y văn, không trên dữ liệu của nghiên cứu này.

# 5. KẾT LUẬN

Trên dữ liệu tổng hợp ở tỷ lệ mắc 2 %, huấn luyện công cụ sàng lọc trên dữ liệu đã cân bằng lại không giúp dịch vụ tâm lý tìm thêm trẻ mắc, nhưng làm con số nguy cơ nói với gia đình bị thổi phồng tới hơn hai mươi lần và làm quy tắc chuyển theo ngưỡng gửi gần như mọi trẻ vào danh sách chờ. Với hồi quy logistic, dịch vụ có thể sửa gần như hoàn toàn bằng một phép dịch log-odds không cần nhãn, chỉ cần một ước tính đáng tin về tỷ lệ mắc; với rừng ngẫu nhiên sau lấy mẫu thừa, SMOTE hay trọng số lớp thì không, và cần yêu cầu nhà cung cấp một phiên bản không cân bằng lại. Khuyến nghị thực hành: hỏi nhà cung cấp sáu câu hỏi ở Bảng 6, kiểm tra hệ số thổi phồng và tải chuyển trên chính quần thể của dịch vụ trước khi triển khai, và khi có thể, vận hành theo năng lực thay vì theo một ngưỡng xác suất chưa được kiểm tra. Các kết luận cần được kiểm chứng trên dữ liệu sàng lọc thật trước khi áp dụng.

# TUYÊN BỐ

**Đạo đức.** Nghiên cứu chỉ dùng dữ liệu tổng hợp do máy sinh; không có dữ liệu của trẻ hay gia đình nào, nên không thuộc diện phải thẩm định đạo đức.

**Dữ liệu và mã nguồn.** Toàn bộ mã, kho hồ sơ tổng hợp (tệp `_p11_pool.npz`), tệp kết quả, công cụ kiểm tra và mã dựng bản thảo được công bố tại [đường dẫn GitHub — điền sau khi đẩy gói]. Lệnh `python src/run_p11_tl.py` tái tạo mọi con số của mục 3.2–3.5 (khoảng 10 phút); `python src/p11_referral_audit.py --demo` tái tạo mục 3.6. Hai lần chạy cho tệp kết quả trùng từng byte.

**Công bố liên quan.** Lưới chính ở mục 3.1 và Bảng 1 được báo cáo đầy đủ trong hai bản thảo đi kèm của cùng nhóm tác giả [@nhom2026en; @nhom2026vn]; các phân tích ở mục 3.2–3.6, Bảng 2–6 và Hình 1–3 là mới. Một bản tiếng Anh của bài này đang được chuẩn bị cho tạp chí quốc tế với cùng dữ liệu; quan hệ giữa các bản thảo sẽ được khai báo với ban biên tập.

**Xung đột lợi ích.** Các tác giả không có xung đột lợi ích.

**Tài trợ.** [Điền nếu có.]

**Đóng góp của tác giả.** [Điền theo CRediT.]

# TÀI LIỆU THAM KHẢO

{{REFERENCES}}
