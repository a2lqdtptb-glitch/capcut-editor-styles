# ---- Thư viện phụ đề (kiểu chữ + hiệu ứng chạy) — nạp bằng exec(open(...)) ở đầu phần chữ của project.py (xem PHU_DE.md) ----
# Học từ @lamdiphuc (bộ font, phụ đề chữ máy đánh chữ cắt theo cụm) và @song.soonf (chữ khít "Classic", Wiping In,
# phụ đề hiện từng từ). Thay cho add_subs(...) của engine: phu_de_thu_vien(SUBS, kieu=..., hieu_ung=..., transcript=...).
# Font không có sẵn trong engine được tự tải (một lần) từ kho Google Fonts trên GitHub (OFL) vào ~/.cache/capcut-editor/fonts.
import json as _pj, os as _po, urllib.request as _pu

_PD_CACHE = _po.path.expanduser('~/.cache/capcut-editor/fonts')
_PD_GF = 'https://raw.githubusercontent.com/google/fonts/main/ofl/'
_PD_FILES = {'IBMPlexMono-Regular.ttf': 'ibmplexmono/IBMPlexMono-Regular.ttf', 'IBMPlexMono-SemiBold.ttf': 'ibmplexmono/IBMPlexMono-SemiBold.ttf',
             'CormorantGaramond[wght].ttf': 'cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf',
             'Merriweather[opsz,wdth,wght].ttf': 'merriweather/Merriweather%5Bopsz,wdth,wght%5D.ttf',
             'Prata-Regular.ttf': 'prata/Prata-Regular.ttf'}

def _pd_font(name):
    """Đường dẫn font: có trong engine (FD) thì dùng luôn, không thì tải về cache (Google Fonts, OFL)."""
    base, _, ax = name.partition('@')
    if _po.path.isfile(FD + base): return FD + name
    p = _po.path.join(_PD_CACHE, base)
    if not _po.path.isfile(p):
        _po.makedirs(_PD_CACHE, exist_ok=True)
        try: _pu.urlretrieve(_PD_GF + _PD_FILES[base], p + '.part'); _po.replace(p + '.part', p)
        except Exception as e: sys.exit(f'phụ đề: không tải được font {base} ({e}) — chọn kiểu khác (vd "gon", "hien_dai")')
    return p + ('@' + ax if ax else '')

# kiểu chữ: thuong = chữ thường, dam = *từ nói mạnh* + tiền tố "Khách:", co = cỡ ở khung 1080, gian = khoảng cách chữ (tỉ lệ cỡ chữ),
# mau_dam = màu từ nói mạnh (None = trắng), bong = độ đậm bóng (font nét mảnh cần đậm hơn), viet_hoa = IN HOA cả câu
pd_kieu = {
    'mong':      dict(thuong='Inter-VF.ttf@wght=300,opsz=32', dam='Inter-VF.ttf@wght=600,opsz=32', co=60, gian=0.0, bong=165),
    'gon':       dict(thuong='Inter-VF.ttf@wght=600,opsz=32', dam='Inter-VF.ttf@wght=800,opsz=32', co=60, gian=-0.035, bong=175),
    'may_chu':   dict(thuong='IBMPlexMono-Regular.ttf', dam='IBMPlexMono-SemiBold.ttf', co=46, gian=0.0, bong=190),
    'hien_dai':  dict(thuong='BeVietnamPro-Regular.ttf', dam='BeVietnamPro-SemiBold.ttf', co=56, gian=0.0, bong=170),
    'ke_chuyen': dict(thuong='CormorantGaramond[wght].ttf@wght=600', dam='CormorantGaramond[wght].ttf@wght=700', co=70, gian=0.0, bong=215),
    'bao_chi':   dict(thuong='Merriweather[opsz,wdth,wght].ttf@wght=400,opsz=18', dam='Merriweather[opsz,wdth,wght].ttf@wght=800,opsz=18',
                      co=50, gian=0.0, bong=190),
    'sang':      dict(thuong='Prata-Regular.ttf', dam='Prata-Regular.ttf', co=54, gian=0.02, bong=215, mau_dam=(246, 214, 140)),
}
pd_hieu_ung = ('mo', 'cat', 'quet', 'noi_tu', 'mot_tu')

def _pd_words(txt, khach, K):
    """[(từ, font, đậm?)] — *cụm* = đậm; lời khách có tiền tố 'Khách:' đậm."""
    out = []
    if khach: out.append((KHACH_PREFIX.capitalize() if KHACH_PREFIX.isupper() else KHACH_PREFIX, K['dam'], True))
    for part in re.split(r'(\*[^*]+\*)', txt):
        if not part.strip(): continue
        b = part.startswith('*')
        out.extend((w, K['dam'] if b else K['thuong'], b) for w in part.strip('*').split())
    return out

def _pd_wlen(w, f_, fs, gian):
    return text_len(w, f_, fs) + gian * fs * max(0, len(w) - 1)

def _pd_layout(words, fs, K):
    """chia ≤2 dòng cân nhau trong SUB_MAXW, thu cỡ khi cần -> (cỡ, [[(từ, font, đậm, x)], ...], bề rộng mỗi dòng)."""
    gian = K['gian']
    def wid(ws, s): return sum(_pd_wlen(w, f_, s, gian) for w, f_, _ in ws) + text_len(' ', ws[0][1], s) * max(0, len(ws) - 1)
    def split(s):
        if wid(words, s) <= SUB_MAXW or len(words) < 2: return [words]
        return min(([words[:i], words[i:]] for i in range(1, len(words))), key=lambda L: max(wid(l, s) for l in L))
    lines = split(fs)
    while fs > 32 and max(wid(l, fs) for l in lines) > SUB_MAXW: fs -= 2; lines = split(fs)
    out = []
    for l in lines:
        x, row = 0.0, []
        for w, f_, b in l:
            row.append((w, f_, b, x)); x += _pd_wlen(w, f_, fs, gian) + text_len(' ', f_, fs)
        out.append((row, wid(l, fs)))
    return fs, out

def _pd_comp(sh, tl, K):
    """bóng gần (mờ 5) + quầng tối rộng (mờ 16) để chữ trắng vẫn đọc được trên nền sáng (khăn trắng, phòng spa sáng)."""
    a = np.array(sh)[..., 3].astype(np.float32)
    halo = cv2.GaussianBlur(cv2.dilate(a, np.ones((13, 13), np.uint8)), (0, 0), 15) * K.get('quang', 0.62)
    near = cv2.GaussianBlur(a, (0, 0), 5)
    sa = np.maximum(halo, near); out = np.zeros(a.shape + (4,), np.uint8); out[..., 3] = sa.astype(np.uint8)
    return np.array(Image.alpha_composite(Image.fromarray(out), tl))

def _pd_draw(rows, fs, K, show=None, pad=44):
    """Vẽ khối phụ đề RGBA (bóng mềm). show = số từ được vẽ (chế độ nối từ) — vị trí từ cố định, không nhảy dòng."""
    f0 = font(rows[0][0][0][1], fs); asc, desc = f0.getmetrics(); lh = int(fs * 1.16)
    W = int(max(w for _, w in rows)) + 2 * pad; H = lh * (len(rows) - 1) + asc + desc + 2 * pad
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); tl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ds, dt = ImageDraw.Draw(sh), ImageDraw.Draw(tl)
    gian = K['gian'] * fs; n = 0; boxes = []
    for j, (row, rw) in enumerate(rows):
        x0 = pad + (W - 2 * pad - rw) / 2; y = pad + j * lh
        for w, f_, b, x in row:
            if show is not None and n >= show: return _pd_comp(sh, tl, K), boxes
            fnt = font(f_, fs); col = (K.get('mau_dam') or (255, 255, 255)) + (255,) if b else (255, 255, 255, 255)
            cx_ = x0 + x; yb = y + asc - fnt.getmetrics()[0]
            for ch in w:
                ds.text((cx_ + 2, yb + 2), ch, font=fnt, fill=(0, 0, 0, K['bong'])); dt.text((cx_, yb), ch, font=fnt, fill=col)
                cx_ += fnt.getlength(ch) + gian
            boxes.append((x0 + x, cx_)); n += 1
    return _pd_comp(sh, tl, K), boxes

def _pd_word_times(k, a, b, n, transcript, txt):
    """Giây bắt đầu (trong video ra) của từng từ: lấy từ transcript (transcribe_vi.py) nếu số từ khớp, không thì chia theo độ dài từ."""
    ts = None
    tj = (transcript or {}).get(k)
    if tj:
        d = _pj.load(open(tj, encoding='utf-8')) if isinstance(tj, str) else tj
        ws = [w for s in d.get('segments', []) for w in s.get('words', []) if a - 0.08 <= w[1] < b - 0.02]
        if len(ws) == n: ts = [w[1] for w in ws]
    if ts is None:
        L = [max(1, len(w)) + 1.5 for w in re.sub(r'\*', '', txt).split()][:n]
        L += [3.0] * (n - len(L)); tot = sum(L); acc = 0.0; ts = []
        for l in L: ts.append(a + (b - a) * 0.92 * acc / tot); acc += l
    out = [src2out(k, t) for t in ts]
    return [o if o is not None else src2out(k, a) for o in out]

def phu_de_thu_vien(SUBS, kieu='gon', hieu_ung='mo', transcript=None, co=None):
    """SUBS như add_subs: (đoạn, giây_a, giây_b, 'lời', ['k']). Mỗi dòng có thể ghi đè bằng dict ở cuối:
    (…, {'kieu': 'sang', 'hieu_ung': 'quet'}). transcript = {'đoạn': 'work/A.json'} để từng từ khớp đúng lúc nói."""
    if hieu_ung not in pd_hieu_ung: sys.exit(f'phụ đề: hiệu ứng {hieu_ung!r} không có ({" | ".join(pd_hieu_ung)})')
    for it in SUBS:
        opt = it[-1] if isinstance(it[-1], dict) else {}
        it_ = it[:-1] if opt else it
        k, a, b, txt = it_[:4]; khach = len(it_) > 4 and str(it_[4]).lower() in ('k', 'khach', 'khách', 'kd')
        K = dict(pd_kieu[opt.get('kieu', kieu)]); hu = opt.get('hieu_ung', hieu_ung)
        K['thuong'], K['dam'] = _pd_font(K['thuong']), _pd_font(K['dam'])
        t0, t1 = src2out(k, a), src2out(k, b)
        if t0 is None: warn(f'phụ đề "{txt[:30]}" ({k} {a}-{b}s) không nằm trong đoạn tiếng nào của AUD -> bỏ'); continue
        if t1 is None or t1 <= t0 + 0.3: t1 = t0 + 0.8
        if txt.isupper(): txt = txt.lower()
        words = _pd_words(txt, khach, K)
        fs0 = int((co or K['co']) * _scale())
        if hu == 'mot_tu':                       # một từ một lúc, to hơn, đổi đúng lúc nói (@song.soonf)
            body = [w for w in words if not (khach and w[0].endswith(':'))]
            st = _pd_word_times(k, a, b, len(body), transcript, txt)
            for i, (w, f_, bb) in enumerate(body):
                fs, rows = _pd_layout([(w, f_, bb)], int(fs0 * 1.45), K); img, _ = _pd_draw(rows, fs, K)
                e = st[i + 1] if i + 1 < len(body) else t1
                add_layer(img, st[i], max(e, st[i] + 0.06), TEXT_CX, min(SUB_CY, SUB_Y1_MAX - img.shape[0] / 2 + 30), 'fixed', z=1, kind='sub')
            continue
        fs, rows = _pd_layout(words, fs0, K)
        img, _ = _pd_draw(rows, fs, K)
        cy = min(SUB_CY, SUB_Y1_MAX - img.shape[0] / 2 + 30)
        if hu == 'mo': add_layer(img, t0, t1, TEXT_CX, cy, 'fade', z=1, dur=0.12, kind='sub', dout=0.10)
        elif hu == 'cat': add_layer(img, t0, t1, TEXT_CX, cy, 'fixed', z=1, kind='sub')
        elif hu == 'quet':                       # Wiping In: quét mép mềm trái -> phải, ~0.6 s (@song.soonf)
            _tn_add(img, t0, t1, TEXT_CX, cy, 1, 'quet', min(0.75, max(0.4, 0.35 * (t1 - t0))), 'cat', 'dung', 'sub')
        elif hu == 'noi_tu':                     # từng từ hiện thêm đúng lúc nói, vị trí cố định
            nb = len(words); st = _pd_word_times(k, a, b, nb - int(khach), transcript, txt)
            if khach: st = [t0] + st
            for i in range(nb):
                im_i, _ = _pd_draw(rows, fs, K, show=i + 1)
                if im_i.shape != img.shape: im_i = np.pad(im_i, ((0, img.shape[0] - im_i.shape[0]), (0, img.shape[1] - im_i.shape[1]), (0, 0)))
                e = st[i + 1] if i + 1 < nb else t1
                add_layer(im_i, st[i], max(e, st[i] + 0.04), TEXT_CX, cy, 'fixed', z=1, kind='sub')
