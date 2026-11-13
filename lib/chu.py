# ---- Chữ hiển thị đọc từ chu.json — nạp bằng exec(open(...)) ở đầu phần chữ của project.py (xem CHU.md) ----
# Mọi chữ hiện trên video (phụ đề, text note, nhãn, tiêu đề, câu chốt) nằm trong <dự án>/chu.json;
# project.py chỉ giữ mốc thời gian, vị trí, kiểu chữ. Sửa chữ = sửa chu.json rồi render lại.
# Bản biến thể: CHU=chu_b.json python render_engine.py ...  (chu_b.json có "_ke_thua": "chu.json" để chỉ ghi phần khác).
import json as _cj, os as _co

def _chu_doc(p, seen=()):
    if p in seen: sys.exit(f'chu.json: vòng kế thừa {" -> ".join(seen + (p,))}')
    if not _co.path.isfile(p): sys.exit(f'không thấy file chữ {p} (tạo từ templates/chu.example.json)')
    try: d = _cj.load(open(p, encoding='utf-8'))
    except ValueError as e: sys.exit(f'chu.json lỗi cú pháp ({p}): {e}')
    base = d.pop('_ke_thua', None)
    if not base: return d
    b = _chu_doc(base if _co.path.isabs(base) else _co.path.join(_co.path.dirname(p), base), seen + (p,))
    for k, v in d.items():
        b[k] = {**b.get(k, {}), **v} if isinstance(v, dict) and isinstance(b.get(k), dict) else v
    return b

_chu_dir = _co.path.dirname(_co.path.abspath(PROJECT))
_chu_p = _co.environ.get('CHU') or 'chu.json'
chu_file = _co.path.join(_chu_dir, _chu_p) if not _co.path.isabs(_chu_p) else _chu_p   # tên viết thường: engine dừng khi thấy biến HOA lạ
chu = _chu_doc(chu_file)
_chu_dung = set()

def c(ma):
    """Chữ đơn theo mã trong mục "chu" (nhãn, tiêu đề, câu chốt, dòng công dụng...)."""
    m = chu.get('chu', {})
    if ma not in m: sys.exit(f'chu.json thiếu mã "{ma}" trong mục "chu" (có: {", ".join(sorted(m)) or "trống"})')
    _chu_dung.add('chu.' + ma); return m[ma]

def nc(ma, nhip_tu=None):
    """Một text note / note động theo mã trong mục "note": trả dict khoa/tren/duoi để truyền **nc('ma') vào text_note/note_dong.
    nhip_tu (nếu có) được kiểm số từ khớp chữ trong chu.json — sửa chữ làm lệch số từ thì cảnh báo để sửa mốc."""
    m = chu.get('note', {})
    if ma not in m: sys.exit(f'chu.json thiếu mã "{ma}" trong mục "note" (có: {", ".join(sorted(m)) or "trống"})')
    _chu_dung.add('note.' + ma); n = m[ma]
    if isinstance(n, str): n = {'khoa': n}
    out = {k: n[k] for k in ('khoa', 'tren', 'duoi') if n.get(k)}
    if nhip_tu:
        for r_, ts_ in nhip_tu.items():
            v_ = out.get(r_)
            if isinstance(v_, str) and len(v_.split()) != len(ts_):
                warn(f'chu.json note "{ma}".{r_} có {len(v_.split())} từ nhưng nhip_tu có {len(ts_)} mốc -> sửa nhip_tu trong project.py')
        out['nhip_tu'] = nhip_tu
    return out

def phu_de():
    """Phụ đề: mục "phu_de" = [[đoạn, giây_a, giây_b, "lời", "k"?], ...] -> add_subs."""
    _chu_dung.add('phu_de'); add_subs([tuple(x) for x in chu.get('phu_de', [])])

def chu_kiem():
    """Gọi ở CUỐI phần chữ: cảnh báo mã có trong chu.json mà project.py không dùng (sửa chữ mà video không đổi)."""
    co = {'chu.' + k for k in chu.get('chu', {})} | {'note.' + k for k in chu.get('note', {})} | ({'phu_de'} if chu.get('phu_de') else set())
    du = sorted(co - _chu_dung)
    if du: warn(f'chu.json có mã không dùng trong project.py: {", ".join(du)}')
    print(f'chu: {chu_file} ({len(_chu_dung)} mã đã dùng)', file=sys.stderr)
