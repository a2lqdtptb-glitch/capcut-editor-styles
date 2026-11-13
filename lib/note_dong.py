# ---- 10 kiểu note động — nạp bằng exec(open(...)) ở đầu phần chữ của project.py (xem NOTE_DONG.md) ----
import numpy as np, cv2, re, math, unicodedata
from PIL import Image, ImageDraw
nd_mau = {'net_but': ((255, 200, 84), (255, 132, 30)), 'chong_lop': ((255, 236, 130), (255, 208, 70)), 'go_phim': ((140, 240, 255), (64, 204, 250)),
          'gach_do': ((255, 84, 84), (236, 32, 32)), 'den_neon': ((255, 150, 228), (255, 70, 196)), 'bac_thang': ((255, 244, 160), (222, 236, 120)),
          'nhan_dich_vu': ((84, 178, 255), (36, 136, 250)), 'but_da_quang': ((250, 118, 126), (240, 88, 100)), 'con_so': ((255, 170, 244), (220, 84, 232)),
          'khoanh_tron': ((200, 255, 124), (104, 232, 70))}
nd_trang = (255, 255, 255)
def _nd_fr(t): return round(t * FPS) / FPS
def _nd_txt(txt, fk, size, col=nd_trang, glow=None, gs=1.0, dark=0.5, rows=None):
    """Một dòng chữ: nét chữ (1 màu hoặc 2 sắc trên -> dưới) + quầng tối mềm (đọc được trên nền sáng) + quầng sáng cùng màu."""
    P, G = int(size * 0.55) + 30, 40; path = FL(fk)
    core = render_line(txt, path, size, (255, 255, 255, 255), shadow=None, pad=P); h, w = core.shape[:2]
    a = np.zeros((h + 2 * G, w + 2 * G), np.float32); a[G:G + h, G:G + w] = core[..., 3]
    ys = np.nonzero(a.max(1) > 40)[0]; y0, y1 = rows or ((int(ys[0]), int(ys[-1])) if len(ys) else (G, G + h))
    c0, c1 = col if isinstance(col[0], (tuple, list)) else (col, col)
    k = np.clip((np.arange(h + 2 * G) - y0) / max(1, y1 - y0), 0, 1)[:, None, None]
    rgb = np.array(c0[:3], np.float32) * (1 - k) + np.array(c1[:3], np.float32) * k
    pa = np.clip(cv2.GaussianBlur(a, (0, 0), 8) * 1.6, 0, 255) / 255 * dark; pr = np.zeros(a.shape + (3,), np.float32)
    if glow is not None:
        ga = np.clip((cv2.GaussianBlur(a, (0, 0), 5) * 0.8 + cv2.GaussianBlur(a, (0, 0), 16) * 1.2) * gs, 0, 255) / 255
        pr = np.array(glow[:3], np.float32) * ga[..., None] + pr * (1 - ga[..., None]); pa = ga + pa * (1 - ga)
    halo = np.dstack([pr / np.maximum(pa, 1e-4)[..., None], pa * 255]).clip(0, 255).astype(np.uint8)          # quầng không có nét chữ
    ta = a[..., None] / 255; pr = rgb * ta + pr * (1 - ta); pa = ta[..., 0] + pa * (1 - ta[..., 0])
    im = np.dstack([pr / np.maximum(pa, 1e-4)[..., None], pa * 255]).clip(0, 255).astype(np.uint8)
    return dict(im=im, halo=halo, L=P + G, w=text_len(txt, path, size), y0=y0, y1=y1, h=y1 - y0, a=a, base=G + P + font(path, size).getmetrics()[0])
def _nd_pos(r, x, ytop):                      # tâm ảnh để mép trái chữ nằm ở x và đỉnh mực nằm ở ytop
    return x - r['L'] + r['im'].shape[1] / 2, ytop - r['y0'] + r['im'].shape[0] / 2
def _nd_tn(nd, im, a, cx, cy, vao, dur, z=5, key=False, flicker=False):
    _tn_add(im, a, nd['t1'], cx, cy, z, vao, dur, nd['ra'], 'dung', 'kin' if key else 'note_sub', flicker=flicker)
def _nd_fx(im, a, b, cx, cy, z=5):            # một khung dựng sẵn, không hiệu ứng (chuyển động dựng từng khung)
    if b > a + 1e-6: LAYERS.append(dict(img=im, t0=a, t1=b, cx=cx, cy=cy, anim='fixed', z=z, dur=0.1, kind='note_sub', dout=0.05))
def _nd_let(txt, fk, size, rows, **kw):
    p = FL(fk); return [(_nd_txt(ch, fk, size, rows=rows, **kw), text_len(txt[:i], p, size)) for i, ch in enumerate(txt) if not ch.isspace()]
def _nd_bat(nd, txt, fk, size, a, x, ytop, ref, step=0.045, dur=0.26, z=5, flicker=False, **kw):
    """Từng chữ cái bật nảy lần lượt (mẫu "Tăng cao", "Đăng Ký"). ref = dòng đầy đủ đã vẽ, để mọi chữ cùng đường chân."""
    _nd_tn(nd, ref['halo'], a, *_nd_pos(ref, x, ytop), 'mo_dan', step * len(txt) + 0.2, z - 1)          # quầng sáng chung nằm dưới, không làm nhòe chữ bên cạnh
    for i, (r, xo) in enumerate(_nd_let(txt, fk, size, (ref['y0'], ref['y1']), **dict(kw, glow=None, dark=0))):
        cx, cy = _nd_pos(r, x + xo, ytop); _nd_tn(nd, r['im'], a + step * i, cx, cy, 'bat', dur, z, key=i == 0, flicker=flicker)
    return a + step * len(txt)
def _nd_gian(nd, txt, fk, size, a, x, ytop, ref, dur=0.33, k0=0.45, z=5, key=False, **kw):
    """Giãn chữ rồi khép lại (mẫu "Bất động sản", "Khóa Học"): chữ hiện với khoảng cách rộng, nhỏ và mờ, khép về bình thường."""
    lets = _nd_let(txt, fk, size, (ref['y0'], ref['y1']), **kw); n = max(3, int(round(dur * FPS))); cx, cy = _nd_pos(ref, x, ytop)
    H_, W_ = ref['im'].shape[0], int(ref['im'].shape[1] + ref['w'] * k0) + 8; a = _nd_fr(a)
    if a < 0.12: n = 0                         # frame 0 của hook: chữ có sẵn
    for k in range(n):
        e = 1 - (1 - k / n) ** 3; sp = 1 + k0 * (1 - e); cv_ = np.zeros((H_, W_, 4), np.uint8)
        for r, xo in lets:
            li = r['im']; lw = li.shape[1]; mid = xo + lw / 2 - r['L'] - ref['w'] / 2          # tâm chữ cái so với tâm dòng
            xs = int(round(W_ / 2 + mid * sp - lw / 2)); x0_, x1_ = max(0, xs), min(W_, xs + lw)
            if x1_ <= x0_: continue
            reg = cv_[:, x0_:x1_]; src = li[:, x0_ - xs:x1_ - xs]; m = src[..., 3] > reg[..., 3]; reg[m] = src[m]
        cv_[..., 3] = (cv_[..., 3] * min(1.0, 0.3 + e)).astype(np.uint8)
        _nd_fx(cv_, a + k / FPS, a + (k + 1) / FPS, cx + (ref['L'] + ref['w'] / 2 - ref['im'].shape[1] / 2), cy, z)
    _nd_tn(nd, ref['im'], a + n / FPS, cx, cy, 'hien', 0.1, z, key=key)
    return a + n / FPS
def _nd_go(nd, txt, fk, size, a, x, ytop, ref, cps=26, cur=True, z=5, key=False, **kw):
    """Gõ phím (mẫu "CĂN HỘ CAO CẤP"): từng ký tự hiện, có con trỏ | khi đang gõ; căn trái cố định nên không nhảy vị trí."""
    n = len(txt); a = _nd_fr(a); cy = _nd_pos(ref, x, ytop)[1]; rows = (ref['y0'], ref['y1'])
    if a < 0.12: _nd_tn(nd, ref['im'], 0.0, *_nd_pos(ref, x, ytop), 'hien', 0.1, z, key=key); return 0.0
    st = [i for i in range(1, n) if not txt[i - 1].isspace()]; te = _nd_fr(a + (n - 1) / cps)
    for j, i in enumerate(st):
        r = _nd_txt(txt[:i] + ('|' if cur else ''), fk, size, rows=rows, **kw)
        _nd_fx(r['im'], _nd_fr(a + (i - 1) / cps), _nd_fr(a + (st[j + 1] - 1) / cps) if j + 1 < len(st) else te, x - r['L'] + r['im'].shape[1] / 2, cy, z)
    _nd_tn(nd, ref['im'], te, *_nd_pos(ref, x, ytop), 'hien', 0.1, z, key=key)
    return te
def _nd_truot(nd, r, a, x, ytop, dur=0.5, z=5, key=False, mem=14):
    """Trượt ra từ sau thanh dọc (mẫu "SEDAN HẠNG C"): chữ nằm sau một mép thẳng ở bên trái, trượt sang phải lộ dần, giảm tốc mạnh."""
    im = r['im']; cx, cy = _nd_pos(r, x, ytop); w = im.shape[1]; c_ = max(0, r['L'] - 10); n = max(3, int(round(dur * FPS))); a = _nd_fr(a)
    if a < 0.12: n = 0
    for k in range(n):
        s = int(round((w - c_) * (1 - k / n) ** 3)); piece = im[:, c_ + s:].copy()
        if piece.shape[1] < 4: continue
        piece[..., 3] = (piece[..., 3] * np.clip(np.arange(piece.shape[1]) / mem, 0, 1)[None]).astype(np.uint8)
        _nd_fx(piece, a + k / FPS, a + (k + 1) / FPS, cx - w / 2 + c_ + piece.shape[1] / 2, cy, z)
    _nd_tn(nd, im, a + n / FPS, cx, cy, 'hien', 0.1, z, key=key)
def _nd_sang(r, a, x, ytop, dur=0.7, z=6):
    """Vệt sáng quét ngang qua nét chữ (mẫu "Bất động sản"): chỉ sáng trong nét chữ, không sáng nền."""
    cx, cy = _nd_pos(r, x, ytop); h, w = r['a'].shape; bw = int(r['h'] * 1.1) + 20; n = max(4, int(round(dur * FPS))); a = _nd_fr(a)
    for k in range(n):
        c_ = int(-bw + (w + bw) * k / (n - 1)); x0_, x1_ = max(0, c_), min(w, c_ + bw)
        if x1_ - x0_ < 4: continue
        band = np.zeros((h, x1_ - x0_, 4), np.uint8); band[..., :3] = (255, 255, 228)
        band[..., 3] = (r['a'][:, x0_:x1_] * (np.sin(np.pi * (np.arange(x0_, x1_) - c_) / bw) ** 2)[None] * 0.85).astype(np.uint8)
        _nd_fx(band, a + k / FPS, a + (k + 1) / FPS, cx - w / 2 + (x0_ + x1_) / 2, cy, z)
def _nd_hinh(draw_fn, w, h, col, glow=True, pad=26):
    """Hình vẽ nét (ô màu, gạch, vòng khoanh): vẽ gấp 3 rồi thu nhỏ cho mịn, thêm quầng sáng cùng màu."""
    S = 3; im = Image.new('RGBA', ((w + 2 * pad) * S, (h + 2 * pad) * S), (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(im), S, pad * S)
    im = np.array(im.resize((w + 2 * pad, h + 2 * pad), Image.LANCZOS))
    if glow:
        g = np.clip(cv2.GaussianBlur(im[..., 3].astype(np.float32), (0, 0), 7) * 1.1, 0, 255); t_ = im[..., 3:4] / 255.0
        im[..., :3] = (im[..., :3] * t_ + np.array(col[:3]) * (1 - t_)).astype(np.uint8); im[..., 3] = np.maximum(im[..., 3], g.astype(np.uint8))
    return im
def _nd_o(w, h, col, bo, a=245, glow=True):    # ô màu bo góc
    return _nd_hinh(lambda d, S, p: d.rounded_rectangle((p, p, p + w * S, p + h * S), bo * S, fill=tuple(col[:3]) + (a,)), w, h, col, glow)
def _nd_mix(c, k): return tuple(int(v + (255 - v) * k) for v in c[:3])

def _nd_net_but(nd, K, T, D, a, cy, c, cm, s):
    sz = fit(K, FL('oswald'), int(124 * s), TEXT_MAXW - 40); k = _nd_txt(K, 'oswald', sz, c, glow=cm, gs=0.8)
    d = _nd_txt(D, 'allura', int(sz * 0.92), glow=nd_trang, gs=0.35) if D else None
    dy = k['base'] - k['y0'] - sz * 0.16                                         # dòng viết tay chạm chân dòng chữ đậm
    tot = max(k['h'], dy + d['h']) if d else k['h']; ytop = cy - tot / 2; x = TEXT_CX - k['w'] / 2
    _nd_gian(nd, K, 'oswald', sz, a, x, ytop, k, key=True, col=c, glow=cm, gs=0.8)
    if d:
        xd = min(max(x + k['w'] - d['w'] + 26, SAFE_X0), SAFE_X1 - d['w'] + 20)
        _nd_tn(nd, d['im'], a + 0.15, *_nd_pos(d, xd, ytop + dy), 'quet', 0.5, z=6)
    if a + 1.6 < nd['t1']: _nd_sang(k, max(a, 0.0) + 0.75, x, ytop)
    return ytop
def _nd_chong_lop(nd, K, T, D, a, cy, c, cm, s):
    sz = fit(K, FL('oswald'), int(180 * s), TEXT_MAXW - 20); k = _nd_txt(K, 'oswald', sz, glow=nd_trang, gs=0.4)
    f_ = np.clip(1 - (np.arange(k['im'].shape[0]) - (k['base'] - sz * 0.50)) / (sz * 0.62), 0.10, 1)          # nửa dưới thân chữ mờ dần
    k['im'][..., 3] = (k['im'][..., 3] * f_[:, None]).astype(np.uint8)
    d = _nd_txt(D, 'script', int(sz * 0.78), c, glow=cm, gs=0.6) if D else None
    dy = k['base'] - k['y0'] - sz * 0.40                                         # chữ viết tay đè lên nửa dưới thân chữ lớn
    tot = max(k['h'], dy + d['h']) if d else k['h']; ytop = cy - tot / 2
    if d: _nd_tn(nd, d['im'], a, *_nd_pos(d, TEXT_CX - d['w'] / 2 + k['w'] * 0.05, ytop + dy), 'mo_net', 0.25, z=6)
    _nd_tn(nd, k['im'], a + (0.3 if d else 0), *_nd_pos(k, TEXT_CX - k['w'] / 2, ytop), 'troi_len', 0.32, z=4, key=True)
    return ytop
def _nd_go_phim(nd, K, T, D, a, cy, c, cm, s):
    K = K.upper(); sz = fit(K + '|', FL('oswald'), int(108 * s), TEXT_MAXW - 20); k = _nd_txt(K, 'oswald', sz, c, glow=cm, gs=0.8)
    dsz = int(sz * 0.48); d = _nd_txt(D, 'playfair_it', dsz) if D else None
    tot = k['h'] + (18 + d['h'] if d else 0); ytop = cy - tot / 2; x = TEXT_CX - k['w'] / 2
    te = _nd_go(nd, K, 'oswald', sz, a, x, ytop, k, key=True, col=c, glow=cm, gs=0.8)
    if d: _nd_gian(nd, D, 'playfair_it', dsz, max(a + 0.3, te - 0.15), min(x + k['w'] - d['w'], SAFE_X1 - d['w']), ytop + k['h'] + 18, d, dur=0.36, k0=0.55)
    return ytop
def _nd_gach_do(nd, K, T, D, a, cy, c, cm, s):
    sz = fit(K, FL('inter_bold'), int(116 * s), TEXT_MAXW - 60); kw = _nd_txt(K, 'inter_bold', sz); kr = _nd_txt(K, 'inter_bold', sz, (_nd_mix(c[0], 0.45), c[0]), glow=cm, gs=0.8)
    ssz = int(sz * 0.46); t = _nd_txt(T, 'inter_light', ssz) if T else None; d = _nd_txt(D, 'inter_light', ssz) if D else None
    tot = kw['h'] + sum(r['h'] + 20 for r in (t, d) if r); y = cy - tot / 2; ytop = y; x = TEXT_CX - kw['w'] / 2
    if t: _nd_tn(nd, t['im'], a, *_nd_pos(t, TEXT_CX - t['w'] / 2, y), 'mo_net', 0.2); y += t['h'] + 20; a += 0.18
    pk = _nd_pos(kw, x, y); _nd_tn(nd, kw['im'], a, *pk, 'tung_chu', 0.4, z=4, key=True)
    th = max(7, int(sz * 0.07)); ln = _nd_hinh(lambda d_, S, p: d_.rounded_rectangle((p, p, p + (int(kw['w']) + 40) * S, p + th * S), th * S // 2, fill=cm + (255,)), int(kw['w']) + 40, th, cm)
    _nd_tn(nd, ln, a + 0.55, TEXT_CX, pk[1] - kw['im'].shape[0] / 2 + kw['base'] - sz * 0.27, 'quet', 0.4, z=6)      # gạch ngang giữa thân chữ thường
    _nd_tn(nd, kr['im'], a + 0.8, *pk, 'mo_dan', 0.4, z=5)                                                           # chữ trắng ngả đỏ
    if d: _nd_tn(nd, d['im'], a + 0.45, *_nd_pos(d, TEXT_CX - d['w'] / 2, y + kw['h'] + 20), 'mo_net', 0.2)
    nd['sfx'] += [(a + 0.55, 'swoosh', -19)]
    return ytop, True
def _nd_den_neon(nd, K, T, D, a, cy, c, cm, s):
    sz = fit(K, FL('black'), int(112 * s), TEXT_MAXW - 60); kw = dict(col=(_nd_mix(c[0], 0.6), c[1]), glow=cm, gs=1.15, dark=0.3)
    k = _nd_txt(K, 'black', sz, **kw); d = _nd_txt(D, 'allura', int(sz * 0.86), glow=nd_trang, gs=0.35) if D else None
    dy = k['base'] - k['y0'] - sz * 0.08; tot = max(k['h'], dy + d['h']) if d else k['h']; ytop = cy - tot / 2; x = TEXT_CX - k['w'] / 2
    te = _nd_bat(nd, K, 'black', sz, a, x, ytop, k, flicker=True, **kw)
    if d: _nd_tn(nd, d['im'], max(a + 0.25, te - 0.2), *_nd_pos(d, min(x + k['w'] - d['w'] + 30, SAFE_X1 - d['w'] + 20), ytop + dy), 'quet', 0.45, z=6)
    return ytop
def _nd_bac_thang(nd, K, T, D, a, cy, c, cm, s):
    sz = fit(K, FL('playfair_reg'), int(150 * s), TEXT_MAXW - 130); k = _nd_txt(K, 'playfair_reg', sz, c, glow=cm, gs=0.55)
    t = _nd_txt(T, 'allura', int(sz * 0.52), glow=nd_trang, gs=0.3) if T else None; dsz = int(sz * 0.36); d = _nd_txt(D, 'inter_light_it', dsz) if D else None
    tot = k['h'] + (t['h'] * 0.86 if t else 0) + (d['h'] + 14 if d else 0); y = cy - tot / 2; x = TEXT_CX - k['w'] / 2
    if t: _nd_tn(nd, t['im'], a, *_nd_pos(t, max(SAFE_X0 - 10, x - 56), y), 'quet', 0.35, z=6); y += t['h'] * 0.86; a += 0.3
    _nd_tn(nd, k['im'], a, *_nd_pos(k, x, y), 'tung_chu', 0.6, key=True)
    if d: _nd_go(nd, D, 'inter_light_it', dsz, a + 0.5, min(x + k['w'] - d['w'] + 50, SAFE_X1 + 10 - d['w']), y + k['h'] + 14, d, cps=30, cur=False)
    return cy - tot / 2, True
def _nd_nhan_dich_vu(nd, K, T, D, a, cy, c, cm, s):
    K = K.upper(); T = (T or '').upper(); pre = T + '  ' if T else ''; x = SAFE_X0 + 40
    sz = fit(pre + K, FL('oswald'), int(76 * s), TEXT_MAXW - 110); l1 = _nd_txt(pre + K, 'oswald', sz, dark=0.45)
    kx = text_len(pre, FL('oswald'), sz); kwid = int(text_len(K, FL('oswald'), sz)); bh = int(sz * 1.22); bx = int(sz * 0.22)
    d = _nd_txt(D, 'allura', int(sz * 0.92), _nd_mix(cm, 0.5)) if D else None
    tot = bh + (d['h'] + 16 if d else 0); ytop = cy - tot / 2; base = ytop + bh / 2 + sz * 0.36          # đường chân dòng 1 (chữ in hoa cao ~0,72 cỡ chữ)
    bar = _nd_o(6, int(tot + 16), cm, 3); _nd_tn(nd, bar, a, x - 26, cy, 'mo_dan', 0.12, z=6)
    cy1 = base - l1['base'] + l1['im'].shape[0] / 2; r1 = dict(l1, y0=0); ytop1 = cy1 - l1['im'].shape[0] / 2
    _nd_truot(nd, r1, a, x, ytop1, key=True)
    _nd_tn(nd, _nd_o(kwid + 2 * bx, bh, cm, int(sz * 0.2)), a + 0.28, x + kx + kwid / 2, ytop + bh / 2, 'quet', 0.3, z=4)
    if d: _nd_truot(nd, d, a + 0.45, x + 4, ytop + bh + 16)
    return ytop, True
def _nd_but_da_quang(nd, K, T, D, a, cy, c, cm, s):
    sz = fit(K, FL('playfair_reg'), int(86 * s), TEXT_MAXW - 110); k = _nd_txt(K, 'playfair_reg', sz, dark=0)
    t = _nd_txt(T, 'inter_light_it', int(sz * 0.74)) if T else None; d = _nd_txt(D, 'allura', int(sz * 1.0), glow=nd_trang, gs=0.3) if D else None
    bw, bh = int(k['w']) + 44, int(sz * 1.34); tot = bh + (t['h'] + 16 if t else 0) + (d['h'] * 0.8 if d else 0); y = cy - tot / 2
    x = TEXT_CX - (bw + (d['w'] * 0.35 if d else 0)) / 2
    if t: _nd_tn(nd, t['im'], a, *_nd_pos(t, x + 4, y), 'nghieng', 0.22); y += t['h'] + 16; a += 0.3
    cyk = y + bh / 2 + sz * 0.34 - k['base'] + k['im'].shape[0] / 2                                          # chữ nằm giữa ô theo đường chân
    _nd_tn(nd, k['im'], a, x + 22 - k['L'] + k['im'].shape[1] / 2, cyk, 'quet', 0.4, z=6, key=True)
    _nd_tn(nd, _nd_o(bw, bh, cm, 7, glow=False), a + 0.08, x + bw / 2, y + bh / 2, 'quet', 0.5, z=5)        # ô màu quét theo sau chữ
    if d: _nd_tn(nd, d['im'], a + 0.6, *_nd_pos(d, min(x + bw - d['w'] * 0.65, SAFE_X1 + 10 - d['w']), y + bh - d['h'] * 0.1), 'quet', 0.4, z=6)
    return cy - tot / 2, True
def _nd_con_so(nd, K, T, D, a, cy, c, cm, s):
    m = re.match(r'\s*(\S*\d\S*)\s*(.*)', K); N, R = m.groups() if m else (K.split()[0], ' '.join(K.split()[1:]))
    kw = dict(col=c, glow=cm, gs=0.7); n = _nd_txt(N, 'mont_xb_it', int(236 * s), **kw)
    rsz = fit(R, FL('oswald'), int(112 * s), TEXT_MAXW - n['w'] - 60) if R else 0; r = _nd_txt(R, 'oswald', rsz, **kw) if R else None
    d = _nd_txt(D, 'allura', int((rsz or 100 * s) * 0.92), glow=nd_trang, gs=0.3) if D else None
    t = _nd_txt(T, 'inter_light_it', int(50 * s)) if T else None
    rw = max(r['w'] if r else 0, (d['w'] + 24) if d else 0); tot_w = n['w'] + 18 + rw; x = max(SAFE_X0 - 10, TEXT_CX - tot_w / 2)
    tot = n['h'] + (t['h'] + 14 if t else 0); y = cy - tot / 2; ytop = y
    if t: _nd_tn(nd, t['im'], a, *_nd_pos(t, x + n['w'] * 0.5, y), 'mo_dan', 0.25); y += t['h'] + 14
    _nd_tn(nd, n['im'], a, *_nd_pos(n, x, y), 'phong_len', 0.45, key=True); rx = x + n['w'] + 18; te = a + 0.2
    if r: te = _nd_bat(nd, R, 'oswald', rsz, a + 0.18, rx, y + n['h'] * 0.04, r, **kw)
    if d: _nd_tn(nd, d['im'], te, *_nd_pos(d, rx + 22, y + (r['h'] + n['h'] * 0.04 + 6 if r else n['h'] * 0.3)), 'quet', 0.45, z=6)
    W_ = int(tot_w + 40); pts = [(W_ * u, 46 - 40 * u - 26 * math.sin(math.pi * u) * (1 - u)) for u in np.linspace(0, 1, 40)]          # nét cong mảnh dưới con số
    cur = _nd_hinh(lambda d_, S, p: d_.line([(p + px * S, p + py * S) for px, py in pts], fill=cm + (255,), width=3 * S, joint='curve'), W_, 56, cm)
    _nd_tn(nd, cur, te + 0.2, x + tot_w / 2, y + n['h'] + 34, 'quet', 0.55, z=4)
    return ytop, True
def _nd_khoanh_tron(nd, K, T, D, a, cy, c, cm, s):
    ws = K.split(); w1, w2 = (ws[0], ' '.join(ws[1:])) if len(ws) > 1 else (K, ''); kw = dict(col=c, glow=cm, gs=0.8)
    sz = fit(max(w1, w2, key=len), FL('mont_xb_it'), int(112 * s), TEXT_MAXW * 0.66); r1 = _nd_txt(w1, 'mont_xb_it', sz, **kw); r2 = _nd_txt(w2, 'mont_xb_it', sz, **kw) if w2 else None
    dsz = int(sz * 0.6); d = _nd_txt(D, 'playfair_reg', dsz) if D else None; ow, oh = (int(d['w']) + 84, int(dsz * 1.5)) if d else (0, 0)
    sx = r1['w'] * 0.70 if r2 else 0; tot_w = max(r1['w'], sx + (r2['w'] if r2 else 0)); x = TEXT_CX - tot_w / 2
    y2 = (r1['base'] - r1['y0'] + sz * 0.84 - (r2['base'] - r2['y0'])) if r2 else 0; kh = (y2 + r2['h']) if r2 else r1['h']; oy = (kh + 14) if (r2 and ow > sx - 14) else r1['h'] + 14
    tot = max(kh, oy + oh) if d else kh; ytop = cy - tot / 2
    te = _nd_bat(nd, w1, 'mont_xb_it', sz, a, x, ytop, r1, step=0.04, **kw)
    if r2: te = _nd_bat(nd, w2, 'mont_xb_it', sz, te, x + sx, ytop + y2, r2, step=0.04, **kw)
    if d:
        ocx, ocy = x + ow / 2 - 8, ytop + oy + oh / 2; n = int(0.45 * FPS); t0_ = _nd_fr(te + 0.1)
        for k_ in range(1, n + 1):                                  # vòng khoanh vẽ dần như nét bút
            e = 1 - (1 - k_ / n) ** 2; im = _nd_hinh(lambda d_, S, p: d_.arc((p, p, p + ow * S, p + oh * S), -215, -215 + 376 * e, fill=cm + (255,), width=3 * S), ow, oh, cm)
            im = _tn_rot(im, 3)
            if k_ < n: _nd_fx(im, t0_ + (k_ - 1) / FPS, t0_ + k_ / FPS, ocx, ocy, 5)
            else: _nd_tn(nd, im, t0_ + (n - 1) / FPS, ocx, ocy, 'hien', 0.1)
        _nd_tn(nd, d['im'], te + 0.2, ocx - d['w'] / 2 - d['L'] + d['im'].shape[1] / 2, ocy + dsz * 0.33 - d['base'] + d['im'].shape[0] / 2, 'tung_chu', 0.3, z=6)
    return ytop
nd_kieu = dict(net_but=_nd_net_but, chong_lop=_nd_chong_lop, go_phim=_nd_go_phim, gach_do=_nd_gach_do, den_neon=_nd_den_neon, bac_thang=_nd_bac_thang,
               nhan_dich_vu=_nd_nhan_dich_vu, but_da_quang=_nd_but_da_quang, con_so=_nd_con_so, khoanh_tron=_nd_khoanh_tron)
nd_sfx = dict(net_but='sparkle', chong_lop='pop', go_phim='click', gach_do='pop', den_neon='pop', bac_thang='pop', nhan_dich_vu='swoosh',
              but_da_quang='pop', con_so='pop', khoanh_tron='pop')
def note_dong(kieu, khoa, t0, t1, tren=None, duoi=None, cy=480, mau=None, ra='nhoe_tan', sau_nguoi=False, toi_thieu=2.4):
    """NOTE ĐỘNG 10 kiểu (học từ bộ 40 text preset CapCut, 2026-11-13). kieu = net_but | chong_lop | go_phim | gach_do | den_neon |
    bac_thang | nhan_dich_vu | but_da_quang | con_so | khoanh_tron. khoa = từ khóa; tren / duoi = dòng phụ (bảng trong SKILL.md).
    mau = '#hex' hoặc (sắc trên, sắc dưới); mặc định màu thương hiệu của hồ sơ, không có thì màu riêng của kiểu (gach_do luôn đỏ).
    ra = nhoe_tan | cat | mo_dan | thu_nho; sau_nguoi=True: chữ lặn sau người như text_note."""
    if kieu not in nd_kieu: sys.exit(f"note_dong: kiểu {kieu!r} không có ({' | '.join(nd_kieu)})")
    if kieu not in TN_USED:
        TN_USED.append(kieu)
        if len(TN_USED) == 3 and not globals().get('nd_mix'): warn(f'note: video dùng tới 3 kiểu ({", ".join(TN_USED)}) — quy chuẩn tối đa 2 kiểu/video')
    nf = lambda v: unicodedata.normalize('NFC', v.strip()) if v else None
    n0 = len(LAYERS); t0 = _nd_fr(max(0.0, t0)); t1 = min(TOTAL, max(t1, t0 + toi_thieu))
    c = nd_mau[kieu] if kieu == 'gach_do' else _tn_grad(dict(brand=True, key=(0, 0, 0, nd_mau[kieu])), mau)
    c = (tuple(c[0])[:3], tuple(c[1])[:3]); cm = tuple(int((p + q) / 2) for p, q in zip(*c)); nd = dict(t1=t1, ra=ra, sfx=[])
    res = nd_kieu[kieu](nd, nf(khoa), nf(tren), nf(duoi), t0, cy, c, cm, _scale())
    if tren and not isinstance(res, tuple):                         # kiểu không có chỗ riêng cho dòng trên: dòng nhỏ trắng phía trên khối
        t = _nd_txt(nf(tren), 'inter_light', int(50 * _scale())); _nd_tn(nd, t['im'], t0, *_nd_pos(t, TEXT_CX - t['w'] / 2, res - t['h'] - 22), 'mo_net', 0.2)
    if t0 < 0.12:                                                   # note ở frame 0 của hook: cả khối hiện sẵn, bỏ khung chuyển động
        keep = [L_ for L_ in LAYERS[n0:] if L_['anim'] != 'fixed']
        for L_ in keep:
            if L_['t0'] < 1.6: L_.update(t0=0.0, vao='hien', flicker=False)
        del LAYERS[n0:]; LAYERS.extend(keep)
    if sau_nguoi:
        for L_ in LAYERS[n0:]: L_['behind'] = True
    if t0 > 0.05: AUTO_SFX.extend([(t0, nd_sfx[kieu], -18)] + nd['sfx'])
