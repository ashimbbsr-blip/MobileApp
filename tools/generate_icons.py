"""
generate_icons.py — Generates Android mipmap app icons from the logo.

Creates a square icon with the brand green background (#2ECC71) and the
logo centred at 80% fill. Outputs PNG at every Android mipmap density.
Also creates round icon variants for Android 8+.
"""

from PIL import Image, ImageDraw
import os, sys

LOGO_SRC = "assets/images/infinitehealthtrackerlogo.png"
RES_DIR  = "android/app/src/main/res"

BRAND_GREEN = (46, 204, 113)   # #2ECC71

# (folder, size_px)
DENSITIES = [
    ("mipmap-mdpi",     48),
    ("mipmap-hdpi",     72),
    ("mipmap-xhdpi",    96),
    ("mipmap-xxhdpi",  144),
    ("mipmap-xxxhdpi", 192),
]

def make_icon(logo: Image.Image, size: int) -> Image.Image:
    """Creates square icon: green bg + logo centred at 80% fill."""
    icon = Image.new("RGBA", (size, size), (*BRAND_GREEN, 255))

    # Scale logo to 80% of icon size, keeping aspect ratio
    fill = int(size * 0.80)
    logo_copy = logo.copy()
    logo_copy.thumbnail((fill, fill), Image.LANCZOS)
    lw, lh = logo_copy.size
    x = (size - lw) // 2
    y = (size - lh) // 2

    if logo_copy.mode == "RGBA":
        icon.paste(logo_copy, (x, y), logo_copy)
    else:
        icon.paste(logo_copy, (x, y))

    return icon

def make_round_icon(logo: Image.Image, size: int) -> Image.Image:
    """Creates circular icon: green circle bg + logo centred."""
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    bg = Image.new("RGBA", (size, size), (*BRAND_GREEN, 255))
    icon.paste(bg, mask=mask)

    fill = int(size * 0.72)
    logo_copy = logo.copy()
    logo_copy.thumbnail((fill, fill), Image.LANCZOS)
    lw, lh = logo_copy.size
    x = (size - lw) // 2
    y = (size - lh) // 2

    if logo_copy.mode == "RGBA":
        icon.paste(logo_copy, (x, y), logo_copy)
    else:
        icon.paste(logo_copy, (x, y))

    return icon

def main():
    if not os.path.exists(LOGO_SRC):
        print(f"ERROR: {LOGO_SRC} not found"); sys.exit(1)

    logo = Image.open(LOGO_SRC).convert("RGBA")
    print(f"Loaded logo: {logo.size[0]}x{logo.size[1]} {logo.mode}")

    for folder, size in DENSITIES:
        out_dir = os.path.join(RES_DIR, folder)
        os.makedirs(out_dir, exist_ok=True)

        square = make_icon(logo, size)
        square_path = os.path.join(out_dir, "ic_launcher.png")
        square.convert("RGB").save(square_path, "PNG", optimize=True)

        round_icon = make_round_icon(logo, size)
        round_path = os.path.join(out_dir, "ic_launcher_round.png")
        round_icon.save(round_path, "PNG", optimize=True)

        print(f"  {folder}/{size}px  square={os.path.getsize(square_path)//1024}KB  round={os.path.getsize(round_path)//1024}KB")

    print(f"\nDone — {len(DENSITIES)} densities written.")

if __name__ == "__main__":
    main()
