# Phong cách Mix tổng hợp chữ trend (người vận hành thêm 2026-11-13)

Nền là phong cách **Cuốn hút** (nhịp hình, zoom, phụ đề Inter Light, chữ lặn sau người, chuyển cảnh, SFX theo cột Cuốn hút ở bảng **Phong cách dựng** trong SKILL.md). Chỉ khác phần chữ nhấn: **mọi text note dựng bằng `note_dong(...)`** (`lib/NOTE_DONG.md`), phối nhiều kiểu chữ trend trong cùng một video thay vì 1–2 kiểu.

- **Engine**: `PHONG_CACH = 'cuon_hut'`, `HOOK_TITLE = ''`; đầu phần chữ có `nd_mix = True` (biến phụ viết thường, tắt cảnh báo "tới 3 kiểu") và nạp `lib/note_dong.py`:

  ```python
  nd_mix = True
  exec(open(os.path.expanduser('~/capcut-editor-styles/lib/note_dong.py'), encoding='utf-8').read())
  ```

  Ghi `Phong cách: mix` vào `progress.md`.
- **Chọn kiểu theo nghĩa từng note** (lời nguyên văn như mục **Text Note**):

| Nội dung note | Kiểu |
| --- | --- |
| tên dịch vụ, liệu trình, cảm giác | Nét bút `net_but` hoặc Chồng lớp `chong_lop` |
| câu hỏi, kiến thức, lời dẫn | Gõ phím `go_phim` hoặc Bút dạ quang `but_da_quang` |
| sai lầm, việc không nên, cảnh báo | Gạch đỏ `gach_do` |
| ưu đãi, tin vui, câu chốt (cảnh tối) | Đèn neon `den_neon` |
| câu hook 3 nhịp, bí quyết | Bậc thang `bac_thang` |
| tên bước, tên máy/công nghệ | Nhãn dịch vụ `nhan_dich_vu` |
| con số thật (bước, buổi, phút) | Con số `con_so` |
| kết quả, tính từ nhấn | Khoanh tròn `khoanh_tron` |

- **Phối**: mỗi video 3–5 kiểu; hai note liền nhau không cùng kiểu, trừ chuỗi bước liên tiếp (dùng chung `nhan_dich_vu` hoặc `con_so` cho đồng bộ); một kiểu tối đa ~40 % số note. Ghi `Note động: <các kiểu>` vào `progress.md`.
- **Màu**: hồ sơ có màu thương hiệu → mọi kiểu theo màu đó (`gach_do` vẫn đỏ) để cả video đồng bộ dù khác kiểu. Không có hồ sơ → màu riêng của từng kiểu.
- **Hook**: note đầu tiên ở frame 0 (`t0 = 0`, hiện sẵn), ưu tiên `bac_thang`, `chong_lop` hoặc `net_but`; sau đó mỗi 2–4 s một note tới hết video như mục **Text Note**.
- Vị trí, không che mặt, chữ lặn sau người, độ dài từ khóa: theo mục **Text Note** (SKILL.md) và `lib/NOTE_DONG.md`.
- **Đề xuất ở hộp thoại** khi video nhiều ý/nhiều bước, spa muốn chữ trend đa dạng: chia sẻ kiến thức dạng liệt kê, quy trình dịch vụ nhiều bước, vlog vui.

**QA thêm cho Mix**: (a) frame 0 có note động hiện đủ; (b) video dùng 3–5 kiểu, không 2 note liền nhau cùng kiểu (trừ chuỗi bước); (c) mỗi note đúng kiểu theo nghĩa ở bảng trên; (d) `--stills` tại t0 + 0,15 / + 0,6 / + 1,5 s mỗi note — chữ trong vùng an toàn, không che mặt, đọc được trên nền.

