# Note động — 10 kiểu (v3.25, người vận hành yêu cầu 2026-11-13)

Bộ chữ chính của phong cách **Mix tổng hợp chữ trend**. Học từ reel "40 text presets CapCut" (Kobe Media, Facebook), đo từng khung bản 1080×1920. Chỉ học **cách chữ chạy, bố cục, phối font**; font CapCut gốc không đóng gói nên thay bằng font OFL có sẵn. Nội dung chữ luôn là lời nguyên văn / tư liệu của từng video (luật mục **Text Note**).

Điểm chung rút ra từ mẫu: mỗi note gồm 1 từ khóa lớn (gradient 2 sắc gần nhau + quầng sáng cùng màu) và 1–2 dòng phụ nhỏ, thường là chữ viết tay chạm hoặc đè lên chân từ khóa; dòng phụ hiện sau từ khóa 0,15–0,5 s; vào nhanh 0,25–0,6 s rồi đứng yên.

| Tên kiểu (mã) | Nhìn thấy | Cách chạy | Dùng cho |
| --- | --- | --- | --- |
| 1 · **Nét bút** `net_but` | chữ đậm hẹp màu ấm + dòng viết tay trắng chạm chân, lệch phải | chữ giãn rộng rồi khép lại 0,33 s; viết tay quét ra; vệt sáng lướt qua chữ | tên dịch vụ + cảm giác ("Gội đầu dưỡng sinh / thư giãn sâu") |
| 2 · **Chồng lớp** `chong_lop` | chữ đậm hẹp rất lớn màu trắng, nửa dưới mờ dần + chữ viết tay màu đè ngang thân | viết tay hiện trước, chữ lớn trồi lên sau 0,3 s | tên liệu trình, tiêu đề hook ("Chăm Sóc Da / chuyên sâu") |
| 3 · **Gõ phím** `go_phim` | chữ IN HOA đậm hẹp màu sáng + dòng nghiêng có chân nhỏ dưới phải | gõ từng ký tự có con trỏ \|, dòng phụ giãn rồi khép | câu kiến thức, lời dẫn, câu hỏi hook |
| 4 · **Gạch đỏ** `gach_do` | từ khóa trắng đậm, vạch đỏ gạch ngang, chữ ngả đỏ phát sáng | từng chữ cái hiện; 0,55 s sau vạch đỏ quét qua, chữ ngả đỏ | sai lầm, việc không nên ("Đừng / tự nặn mụn / tại nhà") |
| 5 · **Đèn neon** `den_neon` | chữ tròn rất đậm phát sáng + viết tay trắng | từng chữ cái bật nảy, nhấp nháy như bật đèn | ưu đãi, tin vui, câu chốt (cảnh đủ tối/tương phản) |
| 6 · **Bậc thang** `bac_thang` | viết tay nhỏ trên-trái → chữ có chân mảnh lớn → nghiêng nhỏ dưới-phải | 3 nhịp: quét → hiện từng chữ cái → gõ | câu hook 3 nhịp, bí quyết ("Bạn đã biết / Bí quyết / da căng bóng?") |
| 7 · **Nhãn dịch vụ** `nhan_dich_vu` | thanh dọc màu bên trái; dòng IN HOA trắng, từ khóa nằm trong ô màu; viết tay bên dưới | chữ trượt ra từ sau thanh dọc, ô màu quét theo | tên bước, tên máy/công nghệ ("BƯỚC 1 · TẨY TRANG") |
| 8 · **Bút dạ quang** `but_da_quang` | dòng hỏi nghiêng nhỏ + từ khóa có chân trên ô màu như tô dạ quang + viết tay dưới phải | dòng hỏi nghiêng vào; chữ và ô màu quét trái → phải | hỏi – đáp, ý chính cần nhớ ("Vì sao? / Chống nắng / quan trọng") |
| 9 · **Con số** `con_so` | số rất lớn nghiêng đậm + chữ đậm hẹp cạnh bên + viết tay + nét cong mảnh bên dưới | số phóng lên, chữ cạnh bên bật từng chữ cái, nét cong vẽ ra | số bước, số buổi, số phút (từ khóa bắt đầu bằng số thật: "5 bước") |
| 10 · **Khoanh tròn** `khoanh_tron` | 2 từ nghiêng đậm xếp so le + từ phụ có chân trong vòng khoanh tay | bật từng chữ cái, vòng khoanh vẽ dần như nét bút | nhấn 1 kết quả/tính từ ("Làn da tươi / tự nhiên") |

Gọi: `note_dong(kieu, khoa, t0, t1, tren=None, duoi=None, cy=480, mau=None, ra='nhoe_tan', sau_nguoi=False, toi_thieu=2.4)` — `tren` / `duoi` là dòng phụ trên / dưới (kiểu nào không có chỗ riêng cho `tren` thì vẽ một dòng nhỏ trắng phía trên khối).

**Luật dùng**
- Dùng thay hoặc song song với `text_note`, cùng mọi luật nội dung, vị trí, không che mặt, mật độ của mục **Text Note**. Ngoài phong cách Mix: tối đa **2 kiểu mỗi video, tính chung** `text_note` + `note_dong` (engine cảnh báo khi tới kiểu thứ 3; phong cách Mix đặt `nd_mix = True` để tắt cảnh báo này).
- Theo phong cách: **Mix tổng hợp chữ trend** dùng 3–5 kiểu phối trong một video (mục **Phong cách Mix tổng hợp chữ trend**); **Cuốn hút** dùng được cả 10 kiểu; **Nhẹ nhàng** chỉ `bac_thang`, `but_da_quang`, `net_but`, `nhan_dich_vu` (không nhấp nháy, không bật nảy dồn); **Luxury** không dùng (có hệ chữ riêng).
- Gợi ý theo dạng: tư vấn `go_phim` + `gach_do`; feedback `khoanh_tron` + `con_so` hoặc `net_but`; vlog `chong_lop` + `net_but`; quy trình dịch vụ `nhan_dich_vu` + `con_so` hoặc `net_but`; kiến thức `go_phim` hoặc `but_da_quang` + `gach_do` hoặc `con_so`. Người vận hành/spa gọi tên kiểu ("dùng kiểu Đèn neon") thì dùng đúng kiểu đó. Ghi `Note động: <kiểu> + <kiểu>` vào `progress.md`.
- Màu: mặc định theo màu thương hiệu trong hồ sơ, không có thì màu riêng của kiểu; `gach_do` luôn đỏ. Màu nhạt (kem, hồng phấn) trên cảnh sáng khó đọc → chọn sắc đậm hơn hoặc đặt trên vùng tối; `den_neon` chỉ dùng trên cảnh đủ tối.
- Độ dài: từ khóa 1–4 từ (dài hơn chữ tự thu nhỏ, mất vẻ đẹp); dòng phụ ≤5 từ.
- Note bắt đầu ở frame 0 (`t0 < 0,12`) thì hiện sẵn, không chạy hiệu ứng vào (quy chuẩn hook). Note kết thúc đúng điểm cắt → `ra='cat'`. Cảnh toàn màn có người → `sau_nguoi=True` như `text_note`.
- Tiếng tự kèm: lấp lánh (`net_but`), click (`go_phim`), vút (`nhan_dich_vu`, vạch của `gach_do`), pop (các kiểu còn lại).
- QA: `--stills` tại t0 + 0,15 / + 0,6 / + 1,5 s mỗi note — chữ trong vùng an toàn, không che mặt, đọc được trên nền.

**Nạp helper**: dòng đầu phần chữ của `project.py`, ngay sau `# ==== TEXT ====` (cùng chỗ với helper phong cách nếu có):

```python
exec(open(os.path.expanduser('~/capcut-editor-styles/lib/note_dong.py'), encoding='utf-8').read())
```

Ví dụ (nội dung chỉ minh họa, thay theo lời trong clip):

```python
note_dong('go_phim', 'da khỏe từ gốc', 0.0, 3.2, duoi='bắt đầu từ làm sạch', cy=470, sau_nguoi=True)
note_dong('gach_do', 'tự nặn mụn', src2out('B', 6.1), src2out('B', 8.6), tren='Đừng', duoi='tại nhà', cy=470, ra='cat')
```

