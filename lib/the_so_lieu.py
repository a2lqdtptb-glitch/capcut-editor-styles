#!/usr/bin/env python3
"""THẺ SỐ LIỆU NHẢY SỐ — dựng sẵn một đoạn video dọc 1080x1920 (không tiếng) để engine dùng như một đoạn nguồn.

Học từ video mẫu (thẻ "DOANH THU / 1 SỰ KIỆN 0 → 300 TRIỆU → 1 TỶ", đo từng khung 10 fps, 2026-11-13):
  - nền: chính clip đó, làm mờ rất mạnh + tối đi (lớp đỡ chữ, không đổi màu clip)
  - thẻ bo góc giữa màn: clip mờ nhẹ, phóng chậm, nửa dưới tối dần; viền sáng mảnh
  - nhãn nhỏ IN HOA giãn chữ -> số to đậm trắng -> thanh tiến độ (nền trắng, phần chạy vàng đồng)
  - số giữ ở giá trị đầu ~0,5 s, rồi đếm ~1,9 s nhanh đầu chậm cuối, thanh chạy cùng nhịp
  - cú nhấn 2: dòng số thu nhỏ đẩy lên dưới nhãn, dòng vàng to hiện mờ -> nét ("→ 1 TỶ"), hạt sáng bung ra
  - hạt vàng/trắng nhỏ trôi chậm trong thẻ; phụ đề nằm trong thẻ, phía dưới
  - vào/ra thẻ: cắt thẳng (engine lo chuyển cảnh + tiếng)

Chạy:  python the_so_lieu.py spec.json out.mp4 [--stills t1,t2,...]
spec.json (giây tính từ đầu thẻ):
{
  "bg": "duong/dan/clip.mp4", "bg_start": 0.0, "dur": 5.2,
  "bg_anchor": [0.5, 0.45],            # tâm cắt khung dọc (tỉ lệ 0..1) khi clip nguồn quay ngang
  "nhan": "KHÁCH HÀNG ĐÃ CHĂM SÓC",
  "tu": 0, "den": 12000, "don_vi": "KHÁCH", "thap_phan": 0,
  "t_dem": [0.7, 2.6],                  # bắt đầu / kết thúc đếm
  "nhan_2": "TRONG 10 NĂM", "t_nhan_2": 3.6,   # cú nhấn 2 (bỏ trống = không có)
  "phu_de": [[0.0, 2.6, "dòng 1\\ndòng 2"], ...],
  "mau_nhan": [242, 212, 136]           # màu vàng chủ đạo (mặc định vàng đồng của mẫu; có thể dùng màu thương hiệu)
}
Số liệu phải là số thật trong lời nói / tư liệu của spa (compliance.md). Font: thư mục fonts của engine
(ADKIT_FONTS hoặc tự tìm cạnh render_engine.py).
"""
import sys, os, json, glob, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
CARD = (110, 300, 970, 1580)          # x0,y0,x1,y1 — rộng ~80 % khung; chữ nằm trong vùng an toàn (y 520–1460)
R = 46


def font_dir():
    for d in [os.environ.get('ADKIT_FONTS', ''), *glob.glob(os.path.expanduser('~/**/ffmpeg_render/fonts'), recursive=True),
              *glob.glob('/root/.claude/skills/**/ffmpeg_render/fonts', recursive=True)]:
        if d and os.path.isfile(os.path.join(d, 'Montserrat-ExtraBold.ttf')): return d
    sys.exit('không thấy thư mục fonts của engine (đặt ADKIT_FONTS)')


FD = font_dir()
_fc = {}
def F(name, size):
    k = (name, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(os.path.join(FD, name), size)
    return _fc[k]


def ease_out(x, p=3.0): x = min(1.0, max(0.0, x)); return 1 - (1 - x) ** p
def ease_in_out(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)


def txt_rgba(text, fname, size, fill=(255, 255, 255), track=0, grad=None, glow=None, shadow=0.55):
    """Chữ RGBA: giãn chữ (track px), tô 1 màu hoặc gradient trên->dưới, bóng tối mềm + quầng sáng (glow)."""
    f = F(fname, size); asc, desc = f.getmetrics()
    ws = [f.getlength(ch) for ch in text]; tw = int(sum(ws) + track * max(0, len(text) - 1)) + 2
    pad = int(size * 0.6); h = asc + desc
    m = Image.new('L', (tw + 2 * pad, h + 2 * pad), 0); d = ImageDraw.Draw(m); x = pad
    for ch, w_ in zip(text, ws): d.text((x, pad), ch, font=f, fill=255); x += w_ + track
    a = np.array(m).astype(np.float32)
    rgb = np.zeros(a.shape + (3,), np.float32)
    if grad:
        ys = np.nonzero(a.max(1) > 30)[0]; y0, y1 = (ys[0], ys[-1]) if len(ys) else (0, a.shape[0])
        k = np.clip((np.arange(a.shape[0]) - y0) / max(1, y1 - y0), 0, 1)[:, None, None]
        rgb[:] = np.array(grad[0], np.float32) * (1 - k) + np.array(grad[1], np.float32) * k
    else: rgb[:] = fill
    out_a = a / 255.0; out_rgb = rgb * out_a[..., None]
    if glow is not None:
        g = np.clip(cv2.GaussianBlur(a, (0, 0), size * 0.12) / 255.0 * 0.9, 0, 1)
        out_rgb = out_rgb + np.array(glow, np.float32) * g[..., None] * (1 - out_a[..., None]); out_a = out_a + g * (1 - out_a)
    if shadow:
        s = np.clip(cv2.GaussianBlur(a, (0, 0), size * 0.10) / 255.0 * shadow, 0, 1)
        out_a = out_a + s * (1 - out_a)
    rgb_f = np.where(out_a[..., None] > 1e-4, out_rgb / np.maximum(out_a[..., None], 1e-4), 0)
    return np.dstack([rgb_f, out_a * 255]).clip(0, 255).astype(np.uint8)


def fit_size(text, fname, size, maxw, track=0):
    while size > 20:
        f = F(fname, size)
        if f.getlength(text) + track * len(text) <= maxw: return size
        size -= 4
    return size


def paste(dst, im, cx, cy, alpha=1.0, scale=1.0, blur=0.0):
    """Dán ảnh RGBA (float dst 0..1, HxWx3) tâm (cx,cy), có thu/phóng, mờ nhòe, độ đục."""
    if alpha <= 0.003: return
    if abs(scale - 1) > 1e-3:
        im = cv2.resize(im, (max(1, int(im.shape[1] * scale)), max(1, int(im.shape[0] * scale))), interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC)
    if blur > 0.3:
        im = im.astype(np.float32); pa = im[..., 3:4] / 255.0
        pre = np.dstack([im[..., :3] * pa, im[..., 3:4]]); pre = cv2.GaussianBlur(pre, (0, 0), blur)
        a_ = pre[..., 3:4] / 255.0; im = np.dstack([pre[..., :3] / np.maximum(a_, 1e-4), pre[..., 3:4]]).clip(0, 255).astype(np.uint8)
    h, w = im.shape[:2]; x0 = int(round(cx - w / 2)); y0 = int(round(cy - h / 2))
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xb <= xa or yb <= ya: return
    src = im[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32) / 255.0
    a = src[..., 3:4] * alpha
    dst[ya:yb, xa:xb] = dst[ya:yb, xa:xb] * (1 - a) + src[..., :3] * a


def round_mask(w, h, r, ss=3):
    m = Image.new('L', (w * ss, h * ss), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), r * ss, fill=255)
    return np.array(m.resize((w, h), Image.LANCZOS)).astype(np.float32) / 255.0


def fmt(v, dec=0):
    s = f'{v:,.{dec}f}'
    return s.replace(',', '#').replace('.', ',').replace('#', '.')       # 12.000 / 1,5


def frames(path, start, dur, anchor):
    """Đọc khung nguồn, cắt phủ kín 1080x1920 quanh anchor, 30 fps."""
    pr = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=width,height:stream_side_data=rotation',
                                    '-of', 'json', path], capture_output=True, text=True).stdout)['streams'][0]
    sw, sh = pr['width'], pr['height']
    sc = max(W / sw, H / sh); nw, nh = int(math.ceil(sw * sc / 2) * 2), int(math.ceil(sh * sc / 2) * 2)
    cx = int(min(max(anchor[0] * nw - W / 2, 0), nw - W)); cy = int(min(max(anchor[1] * nh - H / 2, 0), nh - H))
    vf = f'fps={FPS},scale={nw}:{nh}:flags=lanczos,crop={W}:{H}:{cx}:{cy},format=rgb24'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str(start), '-t', str(dur + 0.5), '-i', path, '-vf', vf, '-f', 'rawvideo', '-'],
                         stdout=subprocess.PIPE)
    last = None
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        last = np.frombuffer(b, np.uint8).reshape(H, W, 3); yield last
    while last is not None: yield last          # clip ngắn hơn thẻ: giữ khung cuối


def main():
    if len(sys.argv) < 3: sys.exit(__doc__)
    S = json.load(open(sys.argv[1], encoding='utf-8')); out = sys.argv[2]
    stills = []
    if '--stills' in sys.argv: stills = [float(x) for x in sys.argv[sys.argv.index('--stills') + 1].split(',')]
    dur = S['dur']; n = int(round(dur * FPS)); gold = tuple(S.get('mau_nhan', [242, 212, 136]))
    gold_hi = tuple(min(255, int(c * 1.08 + 18)) for c in gold); gold_lo = tuple(int(c * 0.78) for c in gold)
    x0, y0, x1, y1 = CARD; cw, ch = x1 - x0, y1 - y0; ccx, ccy = (x0 + x1) / 2, (y0 + y1) / 2
    mask = round_mask(cw, ch, R)
    shade = np.clip(np.linspace(-0.1, 1.15, ch), 0, 1) ** 1.3; shade = (0.38 + 0.54 * shade)[:, None, None]   # nửa dưới tối dần
    band = np.exp(-((np.arange(ch) - (520 - y0 + 270)) / 230.0) ** 2)[:, None, None] * 0.22   # dải tối mềm sau khối số (đọc rõ trên cảnh sáng)
    shade = np.clip(shade + band, 0, 0.92)
    border = (round_mask(cw, ch, R) - np.pad(round_mask(cw - 4, ch - 4, R - 2), 2))[..., None].clip(0, 1) * 0.16
    shadow_card = cv2.GaussianBlur(np.pad(mask, 60), (0, 0), 28)[..., None] * 0.55

    # chữ dựng sẵn
    lab_sz = 30; lab = txt_rgba(S['nhan'], 'Montserrat-SemiBold.ttf', lab_sz, (255, 255, 255), track=4, shadow=0.4)
    unit = S.get('don_vi', ''); dec = S.get('thap_phan', 0)
    widest = fmt(S['den'], dec) + (' ' + unit if unit else '')
    num_sz = fit_size(widest, 'Montserrat-ExtraBold.ttf', 132, cw - 150)
    n2 = S.get('nhan_2'); t2 = S.get('t_nhan_2', dur)
    n2_img = txt_rgba(n2, 'Montserrat-ExtraBold.ttf', fit_size(n2, 'Montserrat-ExtraBold.ttf', 128, cw - 140), grad=(gold_hi, gold_lo),
                      glow=gold, shadow=0.5) if n2 else None
    subs = [(a, b, [txt_rgba(l, 'Montserrat-Bold.ttf', 42, (255, 255, 255), shadow=0.7) for l in t.upper().split('\n')]) for a, b, t in S.get('phu_de', [])]
    num_cache = {}
    def num_img(v):
        s = fmt(v, dec) + (' ' + unit if unit else '')
        if s not in num_cache: num_cache[s] = txt_rgba(s, 'Montserrat-ExtraBold.ttf', num_sz, (255, 255, 255), shadow=0.6)
        return num_cache[s]

    Y_LAB, Y_NUM, Y_BAR, Y_SUB = 640, 760, 885, 1290
    Y_NUM_SMALL, Y_N2 = 712, 800
    bar_w, bar_h = 540, 7
    rng = np.random.default_rng(7)
    parts = [dict(x=rng.uniform(x0 + 40, x1 - 40), y=rng.uniform(y0 + 60, y1 - 60), v=rng.uniform(14, 38), s=rng.uniform(1.6, 3.6),
                  ph=rng.uniform(0, 6.28), gold=rng.random() < 0.7) for _ in range(28)]
    burst = [dict(a=rng.uniform(0, 6.28), sp=rng.uniform(160, 420), s=rng.uniform(2, 4.5)) for _ in range(22)]
    t_d0, t_d1 = S.get('t_dem', [0.7, 2.6])

    enc = None
    if not stills:
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p',
                                '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', out], stdin=subprocess.PIPE)
    want = {int(round(t * FPS)) for t in stills}
    for i, fr in enumerate(frames(S['bg'], S.get('bg_start', 0), dur, S.get('bg_anchor', [0.5, 0.5]))):
        if i >= n: break
        if stills and i not in want: continue
        t = i / FPS; src = fr.astype(np.float32) / 255.0
        # nền: mờ rất mạnh + tối (đỡ chữ), không đổi màu
        small = cv2.resize(src, (W // 8, H // 8), interpolation=cv2.INTER_AREA)
        bg = cv2.resize(cv2.GaussianBlur(small, (0, 0), 5), (W, H), interpolation=cv2.INTER_LINEAR) * 0.55
        # bóng thẻ
        sx0, sy0 = x0 - 60, y0 - 60 + 18
        sub_ = bg[max(0, sy0):sy0 + shadow_card.shape[0], max(0, sx0):sx0 + shadow_card.shape[1]]
        sh_ = shadow_card[:sub_.shape[0], :sub_.shape[1]]; sub_ *= (1 - sh_)
        # thẻ: clip mờ nhẹ, phóng chậm 1.00 -> 1.06, vào thẻ 1.05 -> 1.0 trong 0.3 s
        z = 1.0 + 0.06 * t / dur
        zc = cv2.resize(src, (int(W * z), int(H * z)), interpolation=cv2.INTER_LINEAR)
        ox, oy = (zc.shape[1] - W) // 2, (zc.shape[0] - H) // 2
        card = cv2.GaussianBlur(zc[oy + y0:oy + y1, ox + x0:ox + x1], (0, 0), 3.2) * (1 - shade) + 0.0 * shade
        card = card + border
        k_in = 1.05 - 0.05 * ease_out(t / 0.3)
        if abs(k_in - 1) > 1e-3:
            cs = cv2.resize(card, (int(cw * k_in), int(ch * k_in))); ms = cv2.resize(mask, (cs.shape[1], cs.shape[0]))
            cx_, cy_ = int(ccx - cs.shape[1] / 2), int(ccy - cs.shape[0] / 2)
        else: cs, ms, cx_, cy_ = card, mask, x0, y0
        reg = bg[cy_:cy_ + cs.shape[0], cx_:cx_ + cs.shape[1]]; reg[:] = reg * (1 - ms[..., None]) + cs * ms[..., None]
        img = bg
        # hạt sáng trôi chậm (lấp lánh)
        for p_ in parts:
            py = (p_['y'] - p_['v'] * t - y0) % (ch - 80) + y0 + 40; tw = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(p_['ph'] + t * 3.1))
            c = np.array(gold if p_['gold'] else (255, 255, 255), np.float32) / 255.0
            cv2.circle(img, (int(p_['x']), int(py)), int(round(p_['s'])), tuple(float(v * tw) for v in c), -1, lineType=cv2.LINE_AA)
        # chữ vào: mờ -> nét 0,25 s
        e_in = ease_out(t / 0.25)
        paste(img, lab, ccx, Y_LAB, alpha=0.88 * e_in, blur=(1 - e_in) * 8)
        # số đếm
        u = ease_out((t - t_d0) / (t_d1 - t_d0), 3.2) if t >= t_d0 else 0.0
        val = S['tu'] + (S['den'] - S['tu']) * u
        val = round(val, dec) if dec else int(round(val))
        nimg = num_img(val)
        if n2_img is not None and t >= t2:
            k = ease_out((t - t2) / 0.3)
            paste(img, nimg, ccx, Y_NUM + (Y_NUM_SMALL - Y_NUM) * k, scale=1 - 0.6 * k, alpha=1 - 0.12 * k)
            paste(img, n2_img, ccx, Y_N2 + 24 * (1 - k) + 70, scale=1.12 - 0.12 * k, alpha=k, blur=(1 - k) * 10)
            for b_ in burst:                      # hạt bung quanh dòng vàng
                kb = (t - t2) / 0.9
                if kb > 1: break
                r_ = b_['sp'] * ease_out(kb, 2.2); bx = ccx + math.cos(b_['a']) * r_; by = Y_N2 + 70 + math.sin(b_['a']) * r_ * 0.55
                cv2.circle(img, (int(bx), int(by)), int(b_['s'] * (1 - kb) + 0.5), tuple(v / 255 * (1 - kb) for v in gold_hi), -1, lineType=cv2.LINE_AA)
            ybar = Y_BAR + 70 * k
        else:
            paste(img, nimg, ccx, Y_NUM, alpha=e_in, blur=(1 - e_in) * 10); ybar = Y_BAR
        # thanh tiến độ
        bx0 = int(ccx - bar_w / 2); fill = int(bar_w * (1.0 if (n2_img is not None and t >= t2) else u))
        tr = img[int(ybar):int(ybar) + bar_h, bx0:bx0 + bar_w]; tr[:] = tr * (1 - 0.9 * e_in) + 0.95 * 0.9 * e_in
        if fill > 2:
            gl = np.linspace(0, 1, fill)[None, :, None]
            gcol = (np.array(gold_lo) * (1 - gl) + np.array(gold_hi) * gl) / 255.0
            fr_ = img[int(ybar):int(ybar) + bar_h, bx0:bx0 + fill]; fr_[:] = gcol
            gw = cv2.GaussianBlur(np.pad(np.ones((bar_h, fill), np.float32), 14), (0, 0), 6)[..., None] * 0.35
            gy0, gx0 = int(ybar) - 14, bx0 - 14
            rg = img[gy0:gy0 + gw.shape[0], gx0:gx0 + gw.shape[1]]
            rg[:] = rg + (np.array(gold, np.float32) / 255)[None, None] * gw[:rg.shape[0], :rg.shape[1]] * (1 - rg)
            cv2.circle(img, (bx0 + fill, int(ybar + bar_h / 2)), 6, tuple(v / 255 for v in gold_hi), -1, lineType=cv2.LINE_AA)
        # phụ đề trong thẻ
        for a, b, lines in subs:
            if a <= t < b:
                k = ease_out((t - a) / 0.15)
                for j, li in enumerate(lines): paste(img, li, ccx, Y_SUB + j * 58 - (len(lines) - 1) * 29, alpha=k)
        o = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        if stills: Image.fromarray(o).save(os.path.splitext(out)[0] + f'_{t:05.2f}.png')
        else: enc.stdin.write(o.tobytes())
    if enc: enc.stdin.close(); enc.wait(); print('xong', out)


if __name__ == '__main__':
    main()
