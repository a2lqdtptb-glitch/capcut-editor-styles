#!/usr/bin/env python3
"""Kiểm chữ/hình có bị giao diện app che không (TikTok, Reels, Facebook Reels, Shorts).

Hai việc:
1. Đọc <tên>_timeline.json của engine (khung mực thật của từng lớp chữ/nhãn/ảnh) và báo lớp nào chồng lên
   vùng giao diện của từng nền tảng (cột nút bên phải, caption dưới, thanh trên, nút CTA quảng cáo).
2. Nếu có thư mục ảnh tĩnh (--stills của engine, tên v3_<giây>.png): vẽ giao diện app đè lên mỗi ảnh,
   ghép 1 tấm/ảnh gồm các nền tảng cạnh nhau (ui_<giây>.jpg) + khoanh đỏ lớp bị che -> agent XEM tấm này.

Chạy:  python ui_overlay.py <tên>_timeline.json [--stills <thư mục>] [--nen tiktok,reels,facebook,shorts] [--organic] [-o <thư mục ra>]
  --organic : bỏ vùng chỉ có ở quảng cáo (nhãn tài trợ, nút CTA). Mặc định kiểm theo bản quảng cáo.
Kết quả: in FAIL / CHÚ Ý / PASS; thoát mã 1 khi có FAIL.
Mức: FAIL = lớp bị che >=15 % diện tích (hoặc cột nút che >=6 %); CHÚ Ý = 2–15 % (phụ đề chỉ báo khi >=15 %).
"""
import sys, os, re, json, glob
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BO_QUA = {'lux_nen'}                       # lớp nền, không phải nội dung cần đọc
W, H = 1080, 1920


def args():
    a = sys.argv[1:]
    if not a or a[0].startswith('-'): sys.exit(__doc__)
    o = dict(tl=a[0], stills=None, nen='tiktok,reels,facebook,shorts', ads=True, out=None)
    i = 1
    while i < len(a):
        if a[i] == '--stills': o['stills'] = a[i + 1]; i += 2
        elif a[i] == '--nen': o['nen'] = a[i + 1]; i += 2
        elif a[i] == '-o': o['out'] = a[i + 1]; i += 2
        elif a[i] == '--organic': o['ads'] = False; i += 1
        else: sys.exit(f'tham số lạ: {a[i]}\n' + __doc__)
    return o


def zones(names, ads):
    z = json.load(open(os.path.join(HERE, 'ui_zones.json'), encoding='utf-8'))
    out = {}
    for n in names:
        if n not in z: sys.exit(f'không có nền tảng "{n}" trong ui_zones.json (có: {", ".join(k for k in z if not k.startswith("_"))})')
        out[n] = dict(ten=z[n]['ten'], vung=[v for v in z[n]['vung'] if ads or not v.get('ads')])
    return out


def nhom_lop(tl):
    """Gộp các khung con của cùng một chữ (gõ phím, trượt ra tạo nhiều lớp 1 khung) thành 1 dòng báo."""
    out = []
    for L in sorted(tl.get('layers', []), key=lambda L: L['t0']):
        if L['kind'] in BO_QUA or L['x1'] <= L['x0'] or L['y1'] <= L['y0']: continue
        G = next((G for G in reversed(out) if G['kind'] == L['kind'] and abs(G['y0'] - L['y0']) < 40
                  and abs(G['y1'] - L['y1']) < 40 and L['t0'] <= G['t1'] + 0.2), None)
        if G: G.update(x0=min(G['x0'], L['x0']), y0=min(G['y0'], L['y0']), x1=max(G['x1'], L['x1']),
                       y1=max(G['y1'], L['y1']), t1=max(G['t1'], L['t1']))
        else: out.append(dict(L))
    return out


def che(L, v):
    ix = max(0, min(L['x1'], v['x1']) - max(L['x0'], v['x0'])); iy = max(0, min(L['y1'], v['y1']) - max(L['y0'], v['y0']))
    return ix * iy / max(1, (L['x1'] - L['x0']) * (L['y1'] - L['y0']))


def kiem(tl, Z):
    lop = nhom_lop(tl); kq = []
    for L in lop:
        for n, z in Z.items():
            for v in z['vung']:
                r = che(L, v)
                if r < 0.02 or (L['kind'] == 'sub' and r < 0.15): continue     # phụ đề ở vị trí chuẩn (y≈1380) chạm mép caption ads là bình thường
                muc = 'FAIL' if r >= 0.15 or (v['loai'] == 'icon' and r >= 0.06) else 'CHÚ Ý'
                kq.append((muc, n, v, L, r))
    return lop, kq


def font(sz):
    for p in glob.glob(os.path.expanduser('~/.local/share/fonts/**/*.ttf'), recursive=True) + \
             glob.glob('/usr/share/fonts/**/*.ttf', recursive=True):
        if re.search(r'(Inter|Montserrat|DejaVuSans)[^/]*\.ttf$', p) and 'Italic' not in p:
            try: return ImageFont.truetype(p, sz)
            except OSError: pass
    return ImageFont.load_default()


def ve_giao_dien(img, z, loi, t):
    """Vẽ giao diện app (mờ) lên khung 1080x1920 + khoanh đỏ lớp bị che tại thời điểm t."""
    im = img.convert('RGBA').resize((W, H)); ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    f = font(30)
    for v in z['vung']:
        x0, y0, x1, y1 = v['x0'], v['y0'], v['x1'], v['y1']
        if v['loai'] == 'icon':
            n = max(3, (y1 - y0) // 150); cx = (x0 + x1) // 2; r = min(46, (x1 - x0) // 2 - 8)
            for i in range(n):
                cy = y0 + (i + 0.5) * (y1 - y0) / n
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255, 150), outline=(0, 0, 0, 160), width=3)
        else:
            d.rectangle((x0, y0, x1, y1), fill=(0, 0, 0, 95))
            if v['ma'] == 'chu_thich':
                for j, w_ in enumerate((0.38, 0.8, 0.55)):
                    yy = y0 + 30 + j * 62; d.rounded_rectangle((x0 + 30, yy, x0 + 30 + (x1 - x0 - 60) * w_, yy + 30), 12, fill=(255, 255, 255, 170))
            elif v['ma'] == 'cta':
                d.rounded_rectangle((x0 + 20, y0 + 14, x1 - 20, y1 - 14), 14, fill=(254, 44, 85, 200))
        d.text((x0 + 10, y0 + 6) if v['loai'] != 'icon' else (x0 - 6, y0 - 36), v['ma'], font=f, fill=(255, 235, 120, 255))
    for (_, _, v, L, r) in loi:
        if L['t0'] - 0.05 <= t <= L['t1'] + 0.05:
            d.rectangle((L['x0'], L['y0'], L['x1'], L['y1']), outline=(255, 40, 40, 255), width=7)
            d.text((L['x0'] + 6, max(0, L['y0'] - 36)), f"{L['kind']} -{int(r * 100)}%", font=f, fill=(255, 60, 60, 255))
    im = Image.alpha_composite(im, ov).convert('RGB')
    ImageDraw.Draw(im).text((24, H - 60), z['ten'], font=font(44), fill=(255, 255, 255))
    return im


def main():
    o = args(); tl = json.load(open(o['tl'], encoding='utf-8'))
    Z = zones([s.strip() for s in o['nen'].split(',') if s.strip()], o['ads'])
    lop, kq = kiem(tl, Z)
    bad = 0
    for muc, n, v, L, r in sorted(kq, key=lambda x: (x[0] != 'FAIL', x[3]['t0'])):
        bad += muc == 'FAIL'
        print(f"{muc} {Z[n]['ten']}: {L['kind']} {L['t0']:.2f}–{L['t1']:.2f}s bị '{v['ma']}' ({v['nhan']}) che {int(r * 100)}% "
              f"[khung {L['x0']},{L['y0']}–{L['x1']},{L['y1']}]")
    if not kq: print(f"PASS {len(lop)} lớp chữ/hình không chồng giao diện ({', '.join(z['ten'] for z in Z.values())}"
                     f"{', bản quảng cáo' if o['ads'] else ', bản thường'})")
    if o['stills']:
        out = o['out'] or o['stills']; os.makedirs(out, exist_ok=True); n_ = 0
        for p in sorted(glob.glob(os.path.join(o['stills'], '*.png')) + sorted(glob.glob(os.path.join(o['stills'], '*.jpg')))):
            b = os.path.basename(p)
            if b.startswith('ui_'): continue
            m = re.search(r'(\d+(?:\.\d+)?)\.(?:png|jpg)$', b); t = float(m.group(1)) if m else -1
            img = Image.open(p); pan = []
            for n, z in Z.items():
                pan.append(ve_giao_dien(img, z, [k for k in kq if k[1] == n], t).resize((W // 2, H // 2)))
            sheet = Image.new('RGB', (len(pan) * W // 2 + (len(pan) - 1) * 12, H // 2), (30, 30, 30))
            for i, pp in enumerate(pan): sheet.paste(pp, (i * (W // 2 + 12), 0))
            dst = os.path.join(out, f"ui_{os.path.splitext(b)[0]}.jpg"); sheet.save(dst, quality=85); n_ += 1
        print(f'NOTE đã vẽ giao diện lên {n_} ảnh tĩnh -> {out}/ui_*.jpg (mở xem từng tấm)')
    print('=> ' + ('ĐẠT' if not bad else f'KHÔNG ĐẠT ({bad} lớp bị che)'))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
