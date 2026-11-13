# ---- Luxury helpers — nạp bằng exec(open(...)) ở đầu phần chữ của project.py (xem STYLE.md) ----
import numpy as np
from PIL import Image, ImageDraw
lux_kem = (252, 251, 213, 255)          # kem chanh: từ khóa hook
lux_be = (246, 234, 212, 255)           # be ấm: nhãn công nghệ IN HOA
lux_trang = (255, 255, 255, 255)
def lux_f(k):                           # font Luxury: chữ nối mảnh / từ khóa serif / nghiêng
    return {'noi': FL('inter_light'), 'noi_it': FL('mont_light_it'), 'khoa': FL('playfair'),
            'nghieng': FL('playfair_it'), 'nghieng_dam': FL('playfair_it').replace('wght=500', 'wght=800')}[k]
def _lux_fr(t): return round(t * FPS) / FPS
def lux_nen(t0, t1, cx=540, cy=945, w=1300, h=820, a=0.42):
    """Nền tối mềm hình elip sau khối chữ hook (chỉ để chữ đọc được, không đổi màu cả khung)."""
    yy, xx = np.mgrid[0:h, 0:w]; d = ((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2
    im = np.zeros((h, w, 4), np.uint8); im[..., 3] = (255 * a * np.clip(1 - d, 0, 1) ** 0.8).astype(np.uint8)
    add_layer(im, t0, t1, cx, cy, 'static', z=4, kind='lux_nen')
def lux_go(txt, path, size, t0, t1, x0, cy, fill=lux_trang, cps=20, con_tro=False, z=5):
    """Gõ phím: từng ký tự hiện (cps ký tự/giây), căn trái tại x0. con_tro=True: vạch | sau chữ khi đang gõ."""
    n = len(txt); full = render_line(txt, path, size, fill); pad = (full.shape[1] - text_len(txt, path, size)) / 2
    for i in range(1, n + 1):
        a = _lux_fr(t0 + (i - 1) / cps); b = _lux_fr(t0 + i / cps) if i < n else t1
        if b <= a: continue
        im = render_line(txt[:i] + ('|' if con_tro and i < n else ''), path, size, fill)
        add_layer(im, a, b, x0 - pad + im.shape[1] / 2, cy, 'fixed', z=z, kind='lux_go')     # 'fixed': khung ngắn không bị mờ (sửa 2026-11-13)
def lux_truot(im, t0, t1, x0, cy, dur=1.0, lo=0.70, z=5, mem=18):
    """Trượt ra từ mép ẩn: chữ nằm sau một mép thẳng tại x0 (mép trái khối chữ khi đứng yên), trượt sang phải lộ dần,
    giảm tốc mạnh. lo = phần bề rộng còn ẩn lúc đầu. Ra: cắt cùng cảnh (t1 = điểm cắt)."""
    h, w = im.shape[:2]; nfr = max(2, int(round(dur * FPS)))
    for k in range(nfr):
        a = _lux_fr(t0 + k / FPS); b = _lux_fr(t0 + (k + 1) / FPS) if k < nfr - 1 else t1
        s = int(round(lo * w * (1 - k / (nfr - 1)) ** 3))
        piece = im[:, s:].copy()
        if piece.shape[1] < 4 or b <= a: continue
        ramp = np.clip(np.arange(piece.shape[1]) / mem, 0, 1)
        piece[..., 3] = (piece[..., 3] * ramp[None] * min(1.0, 0.35 + k / (nfr * 0.4))).astype(np.uint8)
        add_layer(piece, a, b, x0 + piece.shape[1] / 2, cy, 'fixed', z=z, kind='lux_truot')
def lux_tim(ten, t0, t1, cx, cy, w=440, h=74, t_go=None, cps=16, z=5):
    """Thanh tìm kiếm: viên thuốc viền trắng + kính lúp bên phải; tên gõ dần trong ô có con trỏ."""
    S = 4; im = Image.new('RGBA', ((w + h) * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((2 * S, 2 * S, w * S - 2 * S, h * S - 2 * S), radius=h * S // 2, outline=(255, 255, 255, 255), width=3 * S)
    gx, gy, r = (w + h // 2) * S, h * S // 2 - 5 * S, 13 * S
    d.ellipse((gx - r, gy - r, gx + r, gy + r), outline=(255, 255, 255, 255), width=3 * S)
    d.line((gx + 9 * S, gy + 9 * S, gx + 20 * S, gy + 20 * S), fill=(255, 255, 255, 255), width=4 * S)
    add_layer(np.array(im.resize((w + h, h), Image.LANCZOS)), t0, t1, cx + h / 2, cy, 'soft', z=z, dur=0.15, kind='lux_tim')
    fs = int(h * 0.40); p = FL('mont'); tw = text_len(ten.upper(), p, fs)
    lux_go(ten.upper(), p, fs, t_go if t_go is not None else t0 + 0.2, t1, cx - tw / 2, cy, cps=cps, con_tro=True, z=z + 1)
