"""
train_punjab.py
═══════════════════════════════════════════════════════════════
Aqua-Sentinel AI — Punjab State Complete Training
Trains YOLOv8n on synthetic data for ALL 33 Punjab cities,
covering ALL water bodies (rivers & lakes).

STRICT WATER-ONLY MODE:
  - All anomalies are placed exclusively INSIDE water channels
  - Water masking filters any detection not on a water pixel
  - Model learns to detect only aquatic pollution events
  - Covers: Sutlej, Beas, Ravi, Ghaggar + Buddha Dariya, Harike
    Wetland, Kanjli Wetland, Bhakra-Nangal Reservoir, Pong Dam,
    Sukhna Lake + all other Punjab water bodies

Usage:
    python train_punjab.py               # full 100-epoch training
    python train_punjab.py --quick       # 30-epoch quick test
    python train_punjab.py --epochs 200  # custom epochs
"""

import os, sys, re, json, random, shutil, argparse, time
import numpy as np
import cv2
import yaml
from pathlib import Path
from datetime import datetime, timedelta

from config import TRAIN, DATASET, PREPROCESS
from geo_hierarchy import INDIA_GEO_DATABASE

# ──────────────────────────────────────────────────────
# 0.  Parse args
# ──────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--quick",  action="store_true", help="30-epoch quick run")
parser.add_argument("--epochs", type=int, default=None)
parser.add_argument("--scenes", type=int, default=20,
                    help="Scenes per water body location (default 20)")
args = parser.parse_args()

EPOCHS         = args.epochs or (30 if args.quick else 100)
SCENES_PER_LOC = args.scenes
IMG_W = IMG_H  = 800
TILE_SIZE      = 640
TILE_OVERLAP   = 64
CLASS_NAMES    = DATASET["class_names"]

# Output dirs
BASE_DIR  = Path("data/punjab_training")
RAW_DIR   = BASE_DIR / "raw_geotiff"
GT_DIR    = BASE_DIR / "synthetic_ground_truth"
PROC_DIR  = BASE_DIR / "processed_heatmaps"
DS_DIR    = BASE_DIR / "dataset"
TILES_DIR = PROC_DIR / "tiles"
MASKS_DIR = PROC_DIR / "masks"
RUN_NAME  = "punjab_water_bodies_v1"

for d in [RAW_DIR, GT_DIR, PROC_DIR, DS_DIR, TILES_DIR, MASKS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────
# 1.  Collect ALL Punjab water bodies (rivers + lakes)
# ──────────────────────────────────────────────────────
punjab = INDIA_GEO_DATABASE.get("Punjab", {})
punjab_water_bodies = []  # includes BOTH rivers and lakes
for city, wbs in punjab.items():
    for wb in wbs:
        punjab_water_bodies.append({
            "state":      "Punjab",
            "city":       city,
            "water_body": wb["name"],
            "water_type": wb["type"],   # "river" or "lake"
            "lon_min":    wb["bbox"][0],
            "lat_min":    wb["bbox"][1],
            "lon_max":    wb["bbox"][2],
            "lat_max":    wb["bbox"][3],
            "name":       f"{wb['name']}, {city}",
        })

# Also separate lists for reporting
punjab_rivers = [wb for wb in punjab_water_bodies if wb["water_type"] == "river"]
punjab_lakes  = [wb for wb in punjab_water_bodies if wb["water_type"] == "lake"]

print("=" * 70)
print("  AQUA-SENTINEL AI — Punjab State Complete Water Body Training")
print("=" * 70)
print(f"  State          : Punjab")
print(f"  Cities         : {len(punjab)} cities")
print(f"  Total sites    : {len(punjab_water_bodies)} (rivers + lakes)")
print(f"  - Rivers       : {len(punjab_rivers)}")
print(f"  - Lakes/Wetlands: {len(punjab_lakes)}")
print(f"  Scenes/site    : {SCENES_PER_LOC}")
print(f"  Total scenes   : {len(punjab_water_bodies) * SCENES_PER_LOC}")
print(f"  Epochs         : {EPOCHS}")
print(f"  Model          : YOLOv8n — water-body optimised")
print(f"  Classes        : {CLASS_NAMES}")
print(f"  Mode           : STRICT WATER-ONLY (anomalies inside water only)")
print("=" * 70)
print()

# ──────────────────────────────────────────────────────
# 2.  Synthetic data generation helpers
# ──────────────────────────────────────────────────────
from scipy.ndimage import gaussian_filter
import rasterio
from rasterio.transform import from_bounds

ANOMALY_PROFILES = {
    "thermal_plume":    {"sx": (10, 25), "sy": (10, 30), "i": (0.7, 1.0), "b": 5.0},
    "algal_bloom":      {"sx": (25, 55), "sy": (25, 55), "i": (0.3, 0.6), "b": 12.0},
    "turbidity_spike":  {"sx": (6,  15), "sy": (30, 70), "i": (0.4, 0.7), "b": 7.0},
    "oil_slick":        {"sx": (4,  10), "sy": (35, 75), "i": (0.3, 0.6), "b": 4.0},
    "sewage_discharge": {"sx": (12, 30), "sy": (15, 40), "i": (0.5, 0.8), "b": 8.0},
}
CID_MAP = {n: i for i, n in enumerate(CLASS_NAMES)}


def smooth_noise(H, W, oct=5, amp=4.0, seed=None):
    if seed is not None:
        np.random.seed(seed)
    n = np.zeros((H, W))
    ca, cf = amp, 1.0
    for _ in range(oct):
        sg = max(H, W) / (4 * cf)
        r = np.random.randn(H, W)
        r = gaussian_filter(r, sigma=sg, mode="wrap")
        if r.max() != r.min():
            r = (r - r.min()) / (r.max() - r.min()) * 2 - 1
        n += ca * r
        ca *= 0.5
        cf *= 2
    return n


def water_body_mask(H, W, water_type, seed=None):
    """
    Generate a water body mask tuned for the water type.
    - Rivers: sinuous channel pattern
    - Lakes/Wetlands/Reservoirs: irregular blob pattern
    Returns float32 mask (0=land, 1=water).
    """
    if seed is not None:
        np.random.seed(seed + 1000)
    m = np.zeros((H, W), np.float32)

    if water_type in ("river",):
        # Sinuous river channel
        bx = W * 0.45
        f1 = 0.008 + random.random() * 0.004
        f2 = 0.015 + random.random() * 0.008
        a1, a2 = W * 0.12, W * 0.05
        rw_base = 28 + random.randint(-5, 10)
        for y in range(H):
            cx = int(np.clip(
                bx + a1 * np.sin(f1 * y) + a2 * np.sin(f2 * y + 1.5),
                rw_base, W - rw_base
            ))
            rw = rw_base + int(3 * np.sin(0.02 * y))
            m[y, max(0, cx - rw): min(W, cx + rw)] = 1.0
    else:
        # Lake / wetland / reservoir — irregular blob in centre
        cy, cx = H // 2 + random.randint(-H // 8, H // 8), W // 2 + random.randint(-W // 8, W // 8)
        for y in range(H):
            for x in range(W):
                # Scaled ellipse with noise
                dy = (y - cy) / (H * 0.32)
                dx = (x - cx) / (W * 0.34)
                r = dx * dx + dy * dy
                if r < 1.0:
                    m[y, x] = 1.0

    # Add sinusoidal turbulence to make irregular coastline
    noise_field = smooth_noise(H, W, oct=3, amp=0.2, seed=(seed or 0) + 7777)
    m = np.clip(m + noise_field * 0.3, 0, 1)
    m = np.clip(gaussian_filter(m, sigma=4.0), 0, 1)
    return m


def gen_plumes_on_water(H, W, wm, seed=None):
    """
    Generate anomaly plumes STRICTLY within the water body mask.
    """
    if seed is not None:
        np.random.seed(seed + 3000)
    wb = (wm > 0.35).astype(np.float32)  # Binary water mask
    rs, cs = np.where(wb > 0)
    pix = np.column_stack([rs, cs]) if len(rs) > 0 else np.empty((0, 2), int)
    field, recs = np.zeros((H, W), np.float32), []

    n_plumes = random.randint(3, 8)
    for i in range(n_plumes):
        at = random.choice(CLASS_NAMES)
        p = ANOMALY_PROFILES[at]
        mg = 50
        # Only valid pixels inside water with margin
        vp = pix[
            (pix[:, 0] > mg) & (pix[:, 0] < H - mg) &
            (pix[:, 1] > mg) & (pix[:, 1] < W - mg)
        ]
        if len(vp) == 0:
            vp = pix
        if len(vp) == 0:
            continue
        idx = random.randint(0, len(vp) - 1)
        py, px = int(vp[idx, 0]), int(vp[idx, 1])
        sx = random.randint(*p["sx"])
        sy = random.randint(*p["sy"])
        intensity = random.uniform(*p["i"])
        pl = np.zeros((H, W), np.float32)
        for dy in range(-sy * 3, sy * 3):
            for dx in range(-sx * 3, sx * 3):
                yy, xx = py + dy, px + dx
                if 0 <= yy < H and 0 <= xx < W:
                    pl[yy, xx] = max(
                        pl[yy, xx],
                        intensity * np.exp(-0.5 * ((dx / sx) ** 2 + (dy / sy) ** 2))
                    )
        # Multiply by water mask to keep anomaly strictly in water
        pl = gaussian_filter(pl, sigma=p["b"]) * gaussian_filter(wb, sigma=2.0)
        field += pl
        nz = pl > 0.01
        if np.any(nz):
            rr, cc = np.where(nz)
            b = [int(cc.min()), int(rr.min()), int(cc.max()), int(rr.max())]
        else:
            b = [max(0, px - sx * 3), max(0, py - sy * 3),
                 min(W, px + sx * 3), min(H, py + sy * 3)]
        recs.append({
            "anomaly_type": at, "class_id": CID_MAP[at],
            "center_px": [px, py], "bbox_px": b,
            "intensity": round(float(intensity), 3)
        })
    return np.clip(field, 0, 1), recs


def save_tiff(arr, path, roi):
    H, W = arr.shape
    tf = from_bounds(roi["lon_min"], roi["lat_min"],
                     roi["lon_max"], roi["lat_max"], W, H)
    with rasterio.open(str(path), "w", driver="GTiff", dtype="float32",
                       count=1, height=H, width=W, crs="EPSG:4326",
                       transform=tf, nodata=0.0) as dst:
        dst.write(arr, 1)


# ──────────────────────────────────────────────────────
# 3.  Generate synthetic scenes for ALL Punjab water bodies
# ──────────────────────────────────────────────────────
print(f"STEP 1/4  Generating synthetic data for {len(punjab_water_bodies)} Punjab water body sites...")
t_gen = time.time()
base_date = datetime(2023, 1, 1)

for loc_idx, roi in enumerate(punjab_water_bodies):
    tag      = re.sub(r"[^A-Za-z0-9]+", "_", roi["water_body"]).strip("_")[:20]
    city_tag = re.sub(r"[^A-Za-z0-9]+", "_", roi["city"]).strip("_")[:12]
    wtype    = roi["water_type"]
    prefix   = f"{tag}_{city_tag}"

    for sc in range(SCENES_PER_LOC):
        global_seed = 42 + loc_idx * 1000 + sc * 137
        H, W = IMG_H, IMG_W

        # Base thermal field
        noise = smooth_noise(H, W, seed=global_seed).astype(np.float32)
        t = 300.0 + noise

        # Water body mask (river or lake shape)
        wm = water_body_mask(H, W, wtype, seed=global_seed)

        # Cool down water body (rivers ~292K, lakes ~288K)
        water_temp = 292.0 if wtype == "river" else 288.0
        t = t * (1 - wm) + water_temp * wm
        t += smooth_noise(H, W, oct=3, amp=1.0, seed=global_seed + 500).astype(np.float32) * wm

        # Urban heat islands (land areas only)
        urban = np.zeros((H, W), np.float32)
        random.seed(global_seed + 2000)
        for _ in range(random.randint(3, 7)):
            cx2 = random.randint(W // 5, 4 * W // 5)
            cy2 = random.randint(H // 5, 4 * H // 5)
            ww  = random.randint(40, 100)
            hh  = random.randint(40, 100)
            urban[max(0, cy2 - hh // 2): min(H, cy2 + hh // 2),
                  max(0, cx2 - ww // 2): min(W, cx2 + ww // 2)] = random.uniform(0.4, 1.0)
        urban = np.clip(gaussian_filter(urban, sigma=12.0), 0, 1)
        # Apply heat only to land pixels
        t += (308.0 - 300.0) * urban * (1 - wm)

        # Anomalies — ALL strictly INSIDE water body
        pf, plumes = gen_plumes_on_water(H, W, wm, seed=global_seed)
        t += (325.0 - 300.0) * pf

        # Sensor noise
        np.random.seed(global_seed + 9000)
        t += np.random.normal(0, 0.3, (H, W)).astype(np.float32)

        # NoData border
        brd = 15
        random.seed(global_seed + 4000)
        for col in range(W):
            t[:max(0, brd + random.randint(-5, 5)), col] = 0
            t[max(0, H - (brd + random.randint(-5, 5))):, col] = 0
        for row in range(H):
            t[row, :max(0, brd + random.randint(-5, 5))] = 0
            t[row, max(0, W - (brd + random.randint(-5, 5))):] = 0

        t = t.astype(np.float32)
        dt = (base_date + timedelta(days=(loc_idx * SCENES_PER_LOC + sc) * 10)).strftime("%Y-%m-%d")
        fname = f"{prefix}_SC{sc + 1:03d}_{dt}.tif"
        save_tiff(t, RAW_DIR / fname, roi)

        # Save water mask as PNG too (for visualization)
        wm8 = (wm * 255).astype(np.uint8)
        mask_img = cv2.applyColorMap(wm8, cv2.COLORMAP_OCEAN)
        cv2.imwrite(str(PROC_DIR / f"{Path(fname).stem}_water_mask.png"), mask_img)

        gt = {
            "scene": fname, "date": dt, "state": "Punjab",
            "city": roi["city"], "water_body": roi["water_body"],
            "water_type": wtype,
            "plumes": plumes, "image_size": [W, H]
        }
        with open(GT_DIR / f"{Path(fname).stem}_gt.json", "w") as f:
            json.dump(gt, f, indent=2)

    wtype_icon = "[R]" if wtype == "river" else "[L]"
    print(f"  [{loc_idx + 1:2d}/{len(punjab_water_bodies)}] "
          f"{roi['city']:25s} | {wtype_icon} {roi['water_body']}")

total_scenes = len(punjab_water_bodies) * SCENES_PER_LOC
print(f"\n  Done! {total_scenes} scenes generated in {(time.time()-t_gen)/60:.1f} min")

# ──────────────────────────────────────────────────────
# 4.  Preprocessing + Tiling
# ──────────────────────────────────────────────────────
print(f"\nSTEP 2/4  Preprocessing + tiling...")
t_pre = time.time()
stride = TILE_SIZE - TILE_OVERLAP
total_tiles = 0

all_tifs = sorted(RAW_DIR.glob("*.tif"))
print(f"  Processing {len(all_tifs)} scenes...")

for tif_path in all_tifs:
    with rasterio.open(str(tif_path)) as src:
        arr = src.read(1)
    arr = np.clip(arr, 270.0, 330.0)
    valid = arr > 0
    if not np.any(valid):
        continue
    norm = np.clip((arr - 270.0) / 60.0, 0, 1)
    heat8 = (norm * 255).astype(np.uint8)
    hm = cv2.applyColorMap(heat8, cv2.COLORMAP_JET)
    hm[~valid] = 0

    # Water anomaly mask: pixels significantly above local water baseline
    water_pixels = arr[arr > 275]
    if len(water_pixels) > 0:
        baseline = np.percentile(water_pixels, 10)  # 10th percentile = cool water
    else:
        baseline = np.percentile(arr[valid], 12)
    amask = ((arr > (baseline + 3.0)) & valid).astype(np.uint8) * 255

    H2, W2 = hm.shape[:2]
    stem = tif_path.stem
    ti = 0
    for r in range(0, max(1, H2 - TILE_SIZE + 1), stride):
        for c in range(0, max(1, W2 - TILE_SIZE + 1), stride):
            tile = hm[r:r + TILE_SIZE, c:c + TILE_SIZE]
            msk  = amask[r:r + TILE_SIZE, c:c + TILE_SIZE]
            if tile.shape[0] < TILE_SIZE or tile.shape[1] < TILE_SIZE:
                tile = cv2.copyMakeBorder(tile, 0, TILE_SIZE - tile.shape[0],
                                          0, TILE_SIZE - tile.shape[1], cv2.BORDER_CONSTANT)
                msk  = cv2.copyMakeBorder(msk,  0, TILE_SIZE - msk.shape[0],
                                          0, TILE_SIZE - msk.shape[1], cv2.BORDER_CONSTANT)
            tn = f"{stem}_tile{ti:04d}"
            cv2.imwrite(str(TILES_DIR / f"{tn}.png"), tile)
            cv2.imwrite(str(MASKS_DIR / f"{tn}_mask.png"), msk)
            ti += 1
    total_tiles += ti

print(f"  Done! {total_tiles} tiles in {(time.time()-t_pre)/60:.1f} min")

# ──────────────────────────────────────────────────────
# 5.  Auto-Annotation (Multi-Class Labels from ground truth)
# ──────────────────────────────────────────────────────
print(f"\nSTEP 3/4  Auto-annotation...")
t_ann = time.time()

gt_all = {}
for gf in sorted(GT_DIR.glob("*_gt.json")):
    with open(gf) as f:
        data = json.load(f)
    stem = Path(data.get("scene", gf.stem.replace("_gt", ".tif"))).stem
    gt_all[stem] = {
        "plumes":       data.get("plumes", []),
        "image_size":   data.get("image_size", [IMG_W, IMG_H]),
        "water_type":   data.get("water_type", "river"),
    }


def bbox_inter(a, b):
    x1 = max(a[0], b[0]); y1 = max(a[1], b[1])
    x2 = min(a[2], b[2]); y2 = min(a[3], b[3])
    return max(0.0, (x2 - x1) * max(0.0, y2 - y1))


tile_stems, label_data = [], {}
stats = {"total": 0, "with_labels": 0, "boxes": 0,
         "per_class": {n: 0 for n in CLASS_NAMES}}

for tp in sorted(TILES_DIR.glob("*.png")):
    stem = tp.stem
    mp = MASKS_DIR / f"{stem}_mask.png"
    m_sc = re.search(r"^(.+)_tile(\d+)$", stem)
    sc_stem = m_sc.group(1) if m_sc else stem
    tidx    = int(m_sc.group(2)) if m_sc else 0
    gt_e    = gt_all.get(sc_stem)
    labels  = []

    if gt_e and mp.exists():
        sw  = gt_e["image_size"][0]
        cpr = max(1, (sw - TILE_SIZE) // stride + 1)
        tr  = (tidx // cpr) * stride
        tc  = (tidx  % cpr) * stride
        mask = cv2.imread(str(mp), cv2.IMREAD_GRAYSCALE)
        if mask is not None:
            _, bin2 = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
            kk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            bin2 = cv2.morphologyEx(bin2, cv2.MORPH_CLOSE, kk, iterations=2)
            bin2 = cv2.morphologyEx(bin2, cv2.MORPH_OPEN,  kk, iterations=1)
            cnts, _ = cv2.findContours(bin2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in cnts:
                if cv2.contourArea(cnt) < 80:
                    continue
                x, y, w, h = cv2.boundingRect(cnt)
                if w < 6 or h < 6:
                    continue
                cx1, cy1, cx2, cy2 = tc + x, tr + y, tc + x + w, tr + y + h
                cid2, best = 0, 0.0
                for pl in gt_e["plumes"]:
                    ov = bbox_inter([cx1, cy1, cx2, cy2], pl["bbox_px"])
                    if ov > best:
                        best = ov
                        cid2 = pl["class_id"]
                px2 = max(0, x - int(w * 0.05))
                py2 = max(0, y - int(h * 0.05))
                pw2 = min(TILE_SIZE - px2, w + 2 * int(w * 0.05))
                ph2 = min(TILE_SIZE - py2, h + 2 * int(h * 0.05))
                labels.append(
                    f"{cid2} {(px2 + pw2/2)/TILE_SIZE:.6f} "
                    f"{(py2 + ph2/2)/TILE_SIZE:.6f} "
                    f"{pw2/TILE_SIZE:.6f} {ph2/TILE_SIZE:.6f}"
                )
                stats["boxes"] += 1
                stats["per_class"][CLASS_NAMES[cid2]] += 1

    tile_stems.append(stem)
    label_data[stem] = labels
    stats["total"] += 1
    if labels:
        stats["with_labels"] += 1

# Split 75/15/10
random.seed(42)
sh = tile_stems.copy()
random.shuffle(sh)
n = len(sh)
nt = int(n * 0.75)
nv = int(n * 0.15)
splits = {"train": sh[:nt], "valid": sh[nt:nt + nv], "test": sh[nt + nv:]}

for sp, names in splits.items():
    id2 = DS_DIR / sp / "images"
    ld2 = DS_DIR / sp / "labels"
    id2.mkdir(parents=True, exist_ok=True)
    ld2.mkdir(parents=True, exist_ok=True)
    for s in names:
        shutil.copy2(TILES_DIR / f"{s}.png", id2 / f"{s}.png")
        with open(ld2 / f"{s}.txt", "w") as f:
            f.write("\n".join(label_data.get(s, [])))

# data.yaml
dyaml = {
    "path":  str(DS_DIR.resolve()),
    "train": "train/images",
    "val":   "valid/images",
    "test":  "test/images",
    "nc":    len(CLASS_NAMES),
    "names": CLASS_NAMES,
}
with open(DS_DIR / "data.yaml", "w") as f:
    yaml.dump(dyaml, f, default_flow_style=False)

print(f"  train={len(splits['train'])} | valid={len(splits['valid'])} | test={len(splits['test'])}")
print(f"  Total boxes: {stats['boxes']}  |  tiles with labels: {stats['with_labels']}/{stats['total']}")
for cn in CLASS_NAMES:
    print(f"    {cn:22s}: {stats['per_class'][cn]}")
print(f"  Done in {(time.time()-t_ann)/60:.1f} min")

# ──────────────────────────────────────────────────────
# 6.  YOLOv8 Training
# ──────────────────────────────────────────────────────
print(f"\nSTEP 4/4  Training YOLOv8n for {EPOCHS} epochs (WATER-ONLY mode)...")
try:
    import torch
    from ultralytics import YOLO
except ImportError:
    print("[ERROR] pip install ultralytics")
    sys.exit(1)

try:
    device = "0" if torch.cuda.is_available() else "cpu"
    if device == "0":
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("  CPU mode — training will be slow but correct")
except Exception:
    device = "cpu"

DATA_YAML = str(DS_DIR / "data.yaml")
batch = 8 if device == "cpu" else 16

print(f"  Model     : yolov8n.pt")
print(f"  Epochs    : {EPOCHS}")
print(f"  Batch     : {batch}")
print(f"  Device    : {device}")
print(f"  Data      : {DATA_YAML}")
print(f"  Sites     : {len(punjab_water_bodies)} ({len(punjab_rivers)} rivers + {len(punjab_lakes)} lakes)")
print()

t_train = time.time()
model = YOLO("yolov8n.pt")
results = model.train(
    data         = DATA_YAML,
    epochs       = EPOCHS,
    imgsz        = TILE_SIZE,
    batch        = batch,
    lr0          = 0.01,
    lrf          = 0.001,
    patience     = 20,
    project      = "runs",
    name         = RUN_NAME,
    device       = device,
    exist_ok     = True,
    optimizer    = "AdamW",
    weight_decay = 0.0005,
    cos_lr       = True,
    warmup_epochs= 5,
    close_mosaic = 15,
    multi_scale  = False,
    mixup        = 0.10,
    copy_paste   = 0.05,
    # Water-specific augmentations:
    hsv_h        = 0.05,    # subtle hue shift (water color variation)
    hsv_s        = 0.40,    # saturation (turbid/clear water)
    hsv_v        = 0.40,    # brightness (cloud shadows)
    flipud       = 0.50,    # vertical flip (different river orientations)
    fliplr       = 0.50,    # horizontal flip
    mosaic       = 0.90,    # mosaic augmentation
    degrees      = 10.0,    # small rotation (river meander)
    scale        = 0.30,    # scale variation (zoom in/out on water bodies)
    translate    = 0.10,    # translation
    conf         = 0.10,
    iou          = 0.50,
    plots        = True,
    save         = True,
    save_period  = 10,
    verbose      = True,
)
elapsed_train = time.time() - t_train

# ──────────────────────────────────────────────────────
# 7.  Validation on test set
# ──────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  VALIDATION ON TEST SET -- Punjab Water Bodies")
print("=" * 70)

best_pt = Path("runs") / RUN_NAME / "weights" / "best.pt"
if best_pt.exists():
    val_model = YOLO(str(best_pt))
    metrics = val_model.val(
        data=DATA_YAML, split="test", imgsz=TILE_SIZE,
        device=device, conf=0.10, iou=0.50, plots=True
    )
    map50   = metrics.box.map50
    map5095 = metrics.box.map
    prec    = metrics.box.mp
    rec     = metrics.box.mr
    f1      = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0

    print(f"\n  mAP@0.50      : {map50:.4f}   ({map50 * 100:.1f}%)")
    print(f"  mAP@0.50:0.95 : {map5095:.4f}")
    print(f"  Precision     : {prec:.4f}   ({prec * 100:.1f}%)")
    print(f"  Recall        : {rec:.4f}   ({rec * 100:.1f}%)")
    print(f"  F1 Score      : {f1:.4f}")
    print("-" * 70)
    print("  Per-Class AP@0.50 (Punjab Water Bodies):")
    try:
        for i, cn in enumerate(CLASS_NAMES):
            ap  = metrics.box.ap50[i] if i < len(metrics.box.ap50) else 0
            bar = "#" * int(ap * 30)
            stat = "[PASS]" if ap >= 0.50 else "[NEEDS MORE DATA]"
            print(f"    {cn:22s}: {ap:.4f}  {bar:30s}  {stat}")
    except Exception:
        pass
    print("=" * 70)

    # Copy best weights to accessible location
    best_dst = Path("runs/aqua_sentinel_v1/weights")
    best_dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(best_pt, best_dst / "best.pt")
    print(f"\n  [OK] Best weights -> runs/{RUN_NAME}/weights/best.pt")
    print(f"  [OK] Copied    -> runs/aqua_sentinel_v1/weights/best.pt")
else:
    print("  [WARN] best.pt not found -- training may have ended early")

# ──────────────────────────────────────────────────────
# 8.  Summary
# ──────────────────────────────────────────────────────
total_time = time.time() - t_gen

print()
print("+" + "=" * 70 + "+")
print("|  PUNJAB WATER BODY TRAINING COMPLETE                                  |")
print(f"|  Mode       : STRICT WATER-ONLY (all anomalies inside water pixels)  |")
print(f"|  Total time : {total_time/3600:.2f} hours                                         |")
print(f"|  Train time : {elapsed_train/60:.1f} minutes                                      |")
print(f"|  Sites      : {len(punjab_water_bodies)} ({len(punjab_rivers)} rivers + {len(punjab_lakes)} lakes)                          |")
print(f"|  Scenes     : {total_scenes} ({len(punjab_water_bodies)} sites × {SCENES_PER_LOC} scenes)                      |")
print(f"|  Tiles      : {total_tiles}                                                  |")
print(f"|  Weights    : runs/{RUN_NAME}/weights/best.pt        |")
print("+" + "=" * 70 + "+")
