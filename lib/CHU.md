# Chữ hiển thị thành biến (`chu.json`)

Mọi chữ hiện trên video nằm trong `<dự án>/chu.json`, cạnh `project.py`: phụ đề, text note / note động, nhãn bước, tiêu đề, dòng công dụng, câu chốt. `project.py` chỉ giữ **mốc thời gian, vị trí, kiểu chữ, hiệu ứng**. Người vận hành nói "đổi chữ giây 12" → sửa đúng một dòng trong `chu.json`, render lại; không đọc lại cả `project.py`.

## Cấu trúc `chu.json`

| Mục | Dạng | Dùng bằng |
| --- | --- | --- |
| `phu_de` | `[[đoạn, giây_a, giây_b, "lời", "k"?], ...]` (giây theo clip nguồn, `"k"` = lời khách) | `phu_de()` |
| `note` | `{"mã": {"khoa": "...", "tren": "...", "duoi": "..."}}` (hoặc `"mã": "từ khóa"`) | `text_note('manh', t0=.., t1=.., **nc('mã'))`, `note_dong('go_phim', t0=.., t1=.., **nc('mã'))` |
| `chu` | `{"mã": "chuỗi"}` — nhãn, tiêu đề, câu chốt, dòng công dụng | `c('mã')` |

Mẫu: `templates/chu.example.json`. Mã đặt theo nội dung (`hook`, `nguyen_nhan`, `buoc_2`, `cau_chot`), không theo số thứ tự, để chèn thêm note không phải đổi mã cũ.

## Trong `project.py`

```python
# ==== TEXT ====
exec(open(os.path.expanduser('~/capcut-editor-styles/lib/chu.py'), encoding='utf-8').read())
phu_de()
text_note('manh', t0=0.0, t1=3.2, cy=470, sau_nguoi=True, **nc('hook', nhip_tu={'khoa': [1.9, 2.2]}))
step_pill(c('buoc_1'), ...)
chu_kiem()          # dòng cuối phần chữ: báo mã có trong chu.json mà project.py không dùng
```

- Gọi `text_note` / `note_dong` bằng tên tham số (`t0=`, `t1=`) khi dùng `**nc(...)`, vì `khoa` đi trong `nc`.
- `nc('mã', nhip_tu=...)` tự kiểm số từ: sửa chữ trong `chu.json` làm lệch số từ so với `nhip_tu` thì engine cảnh báo → sửa mốc trong `project.py`.
- Tên spa, hotline, logo vẫn lấy từ **hồ sơ khách** (`BRAND_TEXT`, `HOTLINE`), không chép vào `chu.json`.
- Luật nội dung không đổi: lời nói giữ nguyên văn; đổi chữ của note thì vẫn phải là lời người nói (hoặc chữ có nguồn trong tư liệu), theo `compliance.md`.

## Bản biến thể (nhiều ưu đãi / chi nhánh, cùng khung dựng)

`chu_b.json` chỉ ghi phần khác, với `"_ke_thua": "chu.json"` (mẫu: `templates/chu_b.example.json`). Render:

```bash
CHU=chu_b.json python render_engine.py <đoạn> <ảnh> <dự án>/outputs/<slug>_<chude>_b --project=<dự án>/project.py --client=...
```

Thư mục ra khác bản A để không ghi đè. Báo cáo ghi rõ bản nào dùng file chữ nào.
