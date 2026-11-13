# capcut-editor-styles

Thư viện đi kèm skill **capcut-editor** (agent dựng video quảng cáo spa). Skill chỉ giữ luật chung; phần dưới đây nằm ở repo để thêm/sửa không phải động vào SKILL.md:

| Đường dẫn | Là gì |
| --- | --- |
| `styles/index.json` | Danh mục phong cách dựng (Cuốn hút, Nhẹ nhàng có sẵn trong engine; Luxury, Mix nạp từ repo) |
| `styles/<mã>/STYLE.md` | Luật của phong cách: font, màu, lớp chữ, vị trí, SFX, QA |
| `styles/<mã>/helpers.py` | Hàm vẽ chữ riêng của phong cách |
| `lib/note_dong.py` + `NOTE_DONG.md` | 10 kiểu note động (nét bút, gõ phím, gạch đỏ, neon…) |
| `lib/chu.py` + `CHU.md` | Chữ hiển thị đọc từ `chu.json` của dự án |
| `qa/ui_overlay.py` + `ui_zones.json` | Kiểm chữ/hình bị giao diện TikTok/Reels/Facebook/Shorts che |
| `templates/` | Mẫu `chu.json`, bản biến thể |

## Dùng trong phiên

```bash
git clone --depth 1 https://github.com/a2lqdtptb-glitch/capcut-editor-styles ~/capcut-editor-styles
```

Nạp helper ở đầu phần chữ của `project.py` (engine chạy phần chữ trong chính không gian tên của nó nên hàm nạp vào dùng được mọi hàm engine):

```python
# ==== TEXT ====
exec(open(os.path.expanduser('~/capcut-editor-styles/lib/chu.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/capcut-editor-styles/styles/luxury/helpers.py'), encoding='utf-8').read())
```

Quy ước code: biến/hàm viết thường hoặc bắt đầu bằng `_` (engine dừng khi gặp biến HOA lạ).

## Thêm phong cách mới

1. Phân tích video mẫu (chỉ học bố cục chữ, màu, font, chuyển động; không chép nội dung).
2. Tạo `styles/<mã>/STYLE.md` theo mẫu `styles/luxury/STYLE.md`: khi nào dùng, engine (`PHONG_CACH` nền), bảng màu, font, các lớp chữ, vị trí trong vùng an toàn, SFX, nạp helper, QA riêng.
3. Hàm mới (nếu có) vào `styles/<mã>/helpers.py`; chạy thử bằng `--stills` trên engine trước khi đẩy.
4. Thêm một dòng vào `styles/index.json`.
5. Đẩy lên repo: phiên có quyền push (GitHub a2lqdtptb-glitch đã kết nối với Claude, gắn repo bằng `add_repo` quyền `push`) thì agent commit + push; không có quyền thì agent gửi file zip các file đã đổi (giữ đúng thư mục) để người vận hành vào repo → **Add file → Upload files** → kéo thả → Commit.
6. Ghi một dòng vào mục **Lịch sử** dưới đây.

## Lịch sử

- 2026-11-13 — tạo repo (skill v3.27): chuyển Luxury, Mix, 10 kiểu note động ra khỏi SKILL.md; thêm `chu.json` (chữ thành biến, bản biến thể) và QA phủ giao diện app.
