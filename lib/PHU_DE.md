# Thư viện phụ đề (`lib/phu_de.py`)

Chọn **kiểu chữ** và **hiệu ứng chạy** cho phụ đề giống cách chọn kiểu text note. Thư viện không gắn font với dạng video nào: mỗi video chọn tùy ý, mỗi câu cũng đổi được.
Học từ @song.soonf (chữ khít kiểu "Classic", Wiping In, hiện từng từ) và @lamdiphuc (chữ máy đánh chữ cắt theo cụm, các font Prata / Merriweather / Cormorant / Be Vietnam Pro).

## Dùng

Trong `project.py`, ở phần `# ==== TEXT ====`, thay `add_subs(SUBS)` bằng:

```python
exec(open(os.path.expanduser('~/capcut-editor-styles/lib/phu_de.py'), encoding='utf-8').read())
subs = [('A', 0.4, 2.6, 'Da bạn cứ nổi mụn mãi là vì *sai lầm* này'),
        ('A', 2.8, 4.3, 'Rửa mặt quá nhiều lần mỗi ngày', {'hieu_ung': 'mot_tu'}),   # đổi riêng câu này
        ('B', 1.0, 3.2, 'Đỡ hẳn rồi em ơi', 'k')]                                   # 'k' = lời khách -> "Khách:"
phu_de_thu_vien(subs, kieu='gon', hieu_ung='quet', transcript={'A': 'work/A.json', 'B': 'work/B.json'})
```

- Tên biến phụ viết **chữ thường** (`subs`, không dùng `SUBS`): engine chặn biến in hoa lạ.
- Dòng phụ đề giống `add_subs`: `(đoạn, giây_a, giây_b, 'lời', ['k'])`, `*cụm*` = chữ đậm. Dict ở cuối (tùy chọn) đổi `kieu` / `hieu_ung` cho riêng dòng đó.
- `transcript` = JSON của `transcribe_vi.py`, dùng cho `noi_tu` và `mot_tu` để từng từ hiện đúng lúc nói. Nếu số từ không khớp hoặc không có transcript, thời điểm được chia theo độ dài từ.
- `co=` ghi đè cỡ chữ (khung 1080). Mặc định mỗi kiểu có cỡ riêng, nhân với `SUB_SCALE`. Khi một dòng quá dài, thư viện tự chia 2 dòng cân nhau rồi thu nhỏ chữ cho vừa `SUB_MAXW`.
- Vị trí giữ quy chuẩn engine: `SUB_CY`, đáy không quá `SUB_Y1_MAX`. Lớp có `kind='sub'`, nên `qa/ui_overlay.py` vẫn kiểm được.

## Kiểu chữ (`kieu`)

| kiểu | font | cảm giác | hợp với |
|---|---|---|---|
| `mong` | Inter Light / SemiBold | mảnh, sạch (mặc định của engine) | mọi video |
| `gon` | Inter SemiBold / ExtraBold, khoảng chữ −3,5 % | chữ khít, chắc, giống "Classic" của CapCut (@song.soonf) | hook, video nhịp nhanh |
| `may_chu` | IBM Plex Mono | máy đánh chữ, kể kiểu vlog (@lamdiphuc) | kể chuyện, hậu trường |
| `hien_dai` | Be Vietnam Pro | tròn, hiện đại, dấu tiếng Việt đẹp | tư vấn, giải thích |
| `ke_chuyen` | Cormorant Garamond 600/700 | chữ có chân, mềm, sang | cảm xúc, chăm sóc |
| `bao_chi` | Merriweather 400/800 | chữ có chân dày, đáng tin | chuyên viên, kiến thức |
| `sang` | Prata, từ đậm tô vàng | serif cao cấp; Prata không có bản đậm nên từ nhấn đổi màu | spa cao cấp, kết video |

Các font Cormorant, Merriweather, Prata và IBM Plex Mono được tự tải một lần từ kho Google Fonts trên GitHub (giấy phép OFL, dùng thương mại được) vào `~/.cache/capcut-editor/fonts`. Inter và Be Vietnam Pro có sẵn trong engine. Mọi font đều đủ dấu tiếng Việt.

Mỗi chữ có bóng gần (mờ 5 px) và một quầng tối rộng phía sau (mờ 15 px), nên chữ trắng vẫn đọc được trên khăn trắng hay phòng spa sáng. Độ đậm của quầng chỉnh bằng khóa `quang` trong `pd_kieu` (mặc định 0,62).

## Hiệu ứng (`hieu_ung`)

| hiệu ứng | chạy thế nào | nguồn |
|---|---|---|
| `mo` | hiện mờ dần 0,12 s, tắt mờ 0,1 s (như engine cũ) | — |
| `cat` | hiện và tắt cứng, không chuyển động | @lamdiphuc |
| `quet` | Wiping In: quét mép mềm từ trái sang phải trong 0,4–0,75 s | @song.soonf |
| `noi_tu` | từng từ hiện thêm đúng lúc được nói; vị trí từ cố định, không nhảy dòng | karaoke / TikTok |
| `mot_tu` | mỗi lúc chỉ một từ, to gấp ~1,45 lần, đổi đúng lúc nói | @song.soonf |

Gợi ý: `noi_tu` và `mot_tu` cần transcript mới khớp nhịp. `mot_tu` hợp với câu ngắn (≤ 8 từ) và nhịp nhanh. `quet` hợp với câu dài 1,5 s trở lên.

Chữ ở frame 0 luôn hiện sẵn, theo quy chuẩn hook của engine, nên `quet` ở câu đầu tiên (bắt đầu trước 0,12 s) sẽ không thấy hiệu ứng quét.
