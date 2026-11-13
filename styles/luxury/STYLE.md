# Phong cách Luxury (người vận hành thêm 2026-11-13, học từ video mẫu clinic laser nâng cơ)

Chỉ học **bố cục chữ, màu, font, cách chữ chạy**. Nội dung chữ viết riêng cho từng clip (từ lời nói, nhãn máy/sản phẩm thấy được, caption của người vận hành; không bịa công dụng, theo `compliance.md`). **Không** có thẻ lời kêu gọi, nút "Book now" hay thẻ CTA cuối trong style này (kể cả khi hồ sơ có hotline); thẻ thương hiệu F6 chỉ là logo, không nút.

**Engine**: engine hiện chỉ nhận `PHONG_CACH` là `'cuon_hut'` hoặc `'nhe_nhang'`, nên Luxury đặt `PHONG_CACH = 'cuon_hut'` (phụ đề Inter Light mảnh trắng hợp style), `HOOK_TITLE = ''`, KHÔNG dùng `text_note`/`kinetic`/`emphasis` (Luxury có hệ chữ riêng), `CUT_SMOOTH` tắt, không `PUNCH_TIMES`, không `WHIP_AT`. Chữ dựng bằng bộ helper `lux_*` dưới đây, nạp vào phần chữ của `project.py` (mục **Nạp helper** bên dưới). Biến phụ viết thường.

**Bảng màu** (đo trên video mẫu): kem chanh `(252, 251, 213)` cho từ khóa hook; be ấm `(246, 234, 212)` cho nhãn công nghệ IN HOA; trắng cho mọi chữ nối/chữ phụ. Không viền. Bóng: từ khóa bóng mềm `(0,0,0,120)` mờ 8; nhãn IN HOA quầng tối đậm `(0,0,0,230)` mờ 16, không lệch; chữ nhỏ bóng `(0,0,0,170–200)` mờ 6.

**Font** (thay thế OFL gần nhất cho font của mẫu): chữ nối mảnh = `inter_light` (mẫu: Montserrat Light); chữ nối nghiêng = `mont_light_it`; từ khóa = `playfair` (Playfair Display Bold); nhãn tên công nghệ = `playfair_it`; nhãn IN HOA và tiêu đề kết quả = Playfair Display Italic đậm 800; chữ trong thanh tìm kiếm = `mont` IN HOA. Tối đa 2 họ font mỗi video: Playfair + Inter/Montserrat.

**4 lớp chữ** (cỡ chữ tính ở khung 1080×1920):

| Lớp | Khi nào | Bố cục | Cách chạy |
| --- | --- | --- | --- |
| 1 · Khối hook | 0 → hết hook (3,5–4,5 s), ra = cắt cùng cảnh | 4–5 dòng xếp so le, căn giữa lệch nhẹ: dòng mảnh trắng 66–76 (câu hỏi dẫn) → **từ khóa** Playfair kem 140–150 (tên dịch vụ/công nghệ) → dòng mảnh trắng 66 → **từ khóa 2** Playfair kem IN HOA 100–110 + 1 từ mảnh trắng 88 cùng hàng ("tại") → thanh tìm kiếm có tên spa (từ hồ sơ; không có hồ sơ thì bỏ thanh). Khe dòng ~100–115 px. Nền tối mềm hình elip sau khối (`lux_nen`). | Frame 0 có sẵn dòng 1 + từ khóa 1; dòng 3 gõ phím ~20 ký tự/s từ 0,8 s; từ khóa 2 hiện mờ nhòe → nét 0,35 s lúc ~2,0 s; từ "tại" + thanh tìm kiếm hiện 0,12–0,15 s lúc ~2,4 s; tên spa gõ trong thanh ~16 ký tự/s, có con trỏ \|. |
| 2 · Nhãn công nghệ | cảnh đầu thân, 4–6 s | Góc dưới trái → phải, 3 tầng: tên dịch vụ Playfair nghiêng trắng 90–96 căn trái (mép trái `SAFE_X0` = 120) → tên máy/công nghệ IN HOA Playfair nghiêng đậm be ấm 100–104 căn phải (mép phải `SAFE_X1` = 880; tên dài thì thu cỡ bằng `fit(...)` cho vừa 120–880), quầng tối → 1 dòng giải thích Inter Light trắng 42–44 căn giữa. | Từng tầng trượt ra từ mép ẩn (`lux_truot`), cách nhau 0,7–0,8 s, mỗi tầng 0,8–1,2 s giảm tốc mạnh; đứng yên tới điểm cắt rồi cắt cùng cảnh (cảnh sau có thể vào bằng chuyển cảnh ánh sáng/đen của dạng video). |
| 3 · Dòng công dụng | mỗi cảnh thân một dòng (2–2,5 s/cảnh) | 1 dòng Inter Light trắng 42–46 căn giữa, ≤7 từ ("Cải thiện da chùng, nếp nhăn", "Thời gian thực hiện nhanh"); dòng cuối loạt có thể nghiêng `mont_light_it`. | Trượt ra từ mép ẩn 0,9–1,0 s, bắt đầu ~0,2 s sau đầu cảnh, cắt cùng cảnh. Không đồng thời với phụ đề lời nói: có lời thì bỏ lớp này, ý công dụng đi vào phụ đề. |
| 4 · Khối kết quả | cảnh kết quả/sau liệu trình | Tiêu đề Playfair nghiêng đậm trắng 88–92 căn trái (mép trái `SAFE_X0`) + dòng phụ `mont_light_it` trắng 42 căn giữa ngay dưới. Dòng phụ đổi nội dung giữa chừng (2 ý, mỗi ý ~1,7–2,5 s). | Tiêu đề trượt ra từ mép ẩn 0,8 s; dòng phụ trượt ra, ý thứ 2 thay ý 1 bằng một lần trượt mới. Chữ kết quả phải đúng tư liệu (số buổi thật, lời khách/chuyên viên), kèm cờ trước–sau như luật dạng. |

**Vị trí** (sửa 2026-11-13 sau khi QA giao diện phát hiện nhãn mép phải x≈1020 nằm dưới cột nút TikTok/Shorts): tọa độ của mẫu (chữ ở 80–92 % chiều cao khung) rơi vào vùng giao diện TikTok, nên Luxury dời lên vùng an toàn: lớp 2–4 đặt trong y 1150–1420 (cảnh có phụ đề lời nói: đáy khối chữ ≤ 1290 để không đè phụ đề ở y≈1380); khối hook giữa màn (y 700–1200). **Không che mặt**: chọn `cy` khối hook và lớp 2–4 theo vị trí mặt trong cảnh (khối hook có thể dời lên trên đầu hoặc xuống ngực, nhãn dời sang khoảng trống), kiểm `--stills` mọi lớp. Không dùng chữ lặn sau người.

**Nền tối sau khối hook** (`lux_nen`): elip tối mềm alpha ≤0,42 chỉ sau khối chữ hook, để chữ mảnh đọc được — đây là lớp đỡ chữ, không phải chỉnh màu; không phủ tối cả khung như mẫu, không dùng ngoài hook.

**SFX** (mức thấp như Nhẹ nhàng): tiếng gõ phím không có trong thư viện → dùng click nhỏ `S13`/`S14` −20 dB ở đầu đoạn gõ (không đặt mỗi ký tự); `sfx_sparkle()` −18 dB lúc từ khóa 2 hiện; swoosh nhẹ (`S18`) −18 dB lúc nhãn IN HOA trượt ra. Nhạc theo dạng video, ưu tiên bài sang/ambient (Mixkit dạng 5, M04/M05).

**Nạp helper** (thay cho việc dán code): dòng đầu phần chữ của `project.py`, ngay sau `# ==== TEXT ====`:

```python
exec(open(os.path.expanduser('~/capcut-editor-styles/styles/luxury/helpers.py'), encoding='utf-8').read())
```

Helper: `lux_f(k)` font theo lớp (`noi`, `noi_it`, `khoa`, `nghieng`, `nghieng_dam`); `lux_nen` nền tối elip sau khối hook; `lux_go` gõ phím căn trái cố định; `lux_truot` trượt ra từ mép ẩn; `lux_tim` thanh tìm kiếm gõ tên spa. Màu: `lux_kem`, `lux_be`, `lux_trang`.

Ví dụ dùng (nội dung chỉ minh họa, chữ lấy từ `chu.json`, thay theo clip; `T0` = hết hook, `e1` = điểm cắt cảnh nhãn):

```python
# chu.json -> "chu": {"cau_dan", "dich_vu", "dong_noi", "tu_khoa_2", "cong_nghe"}
lux_nen(0.0, T_TITLE0)
add_layer(render_line(c('cau_dan'), lux_f('noi'), 74, lux_trang), 0.0, T_TITLE0, 540, 720, 'static', z=5)
add_layer(render_line(c('dich_vu'), lux_f('khoa'), fit(c('dich_vu'), lux_f('khoa'), 150, SAFE_X1 - SAFE_X0), lux_kem, shadow=(0, 0, 0, 120), sh_blur=8), 0.0, T_TITLE0, 500, 830, 'static', z=5)
sz3 = fit(c('dong_noi'), lux_f('noi'), 66, SAFE_X1 - SAFE_X0)                  # câu dài tự thu cỡ, không tràn sang cột nút
lux_go(c('dong_noi'), lux_f('noi'), sz3, 0.8, T_TITLE0, TEXT_CX - text_len(c('dong_noi'), lux_f('noi'), sz3) / 2, 945, cps=21)
add_layer(render_line(c('tu_khoa_2'), lux_f('khoa'), 104, lux_kem, shadow=(0, 0, 0, 120), sh_blur=8), 2.0, T_TITLE0, 440, 1050, 'soft', z=5, dur=0.35)
add_layer(render_line('tại', lux_f('noi'), 88, lux_trang), 2.4, T_TITLE0, 790, 1050, 'soft', z=5, dur=0.12)
lux_tim(BRAND_TEXT, 2.4, T_TITLE0, 480, 1165, t_go=2.6)          # chỉ khi hồ sơ có tên spa
sz = fit(c('cong_nghe'), lux_f('nghieng_dam'), 104, SAFE_X1 - SAFE_X0)
l2 = render_line(c('cong_nghe'), lux_f('nghieng_dam'), sz, lux_be, shadow=(0, 0, 0, 230), sh_off=0, sh_blur=16)
lux_truot(l2, T_TITLE0 + 1.2, e1, SAFE_X1 - l2.shape[1], 1290, dur=1.1)   # mép phải chữ trong vùng an toàn, không nằm dưới cột nút
```

**QA thêm cho Luxury**: (0) `qa/ui_overlay.py` không còn FAIL (khối hook và nhãn công nghệ hay tràn sang cột nút); (a) frame 0 có dòng dẫn + từ khóa kem; (b) đoạn gõ phím không nhảy vị trí (căn trái cố định); (c) chữ trượt ra không giật (`--stills` ở t0 + 0,2 / 0,5 / 1,0 s); (d) không có CTA/nút Book now; (e) không chữ nào che mặt hoặc nằm dưới y 1450; (f) tối đa 2 họ font.

