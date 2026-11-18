from PIL import Image, ImageDraw
import customtkinter as ctk


def make_icon(kind, size=64, accent="#00E5FF"):
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    inset = max(3, size // 10)

    draw.rounded_rectangle(
        (inset, inset, size - inset - 1, size - inset - 1),
        radius=max(5, size // 7),
        fill=(12, 20, 28, 255),
        outline=accent,
        width=max(1, size // 32),
    )

    cx = size // 2
    cy = size // 2
    stroke = max(2, size // 20)

    if kind in ("search", "device"):
        radius = size // 4
        draw.ellipse((cx - radius, cy - radius - size // 12, cx + radius,
                      cy + radius - size // 12), outline=accent, width=stroke)
        draw.line((cx + radius // 2, cy + radius // 2 - size // 12,
                   cx + radius + size // 8, cy + radius + size // 6),
                  fill=accent, width=stroke)
    elif kind == "refresh":
        box = (size // 4, size // 5, size * 3 // 4, size * 4 // 5)
        draw.arc(box, 20, 300, fill=accent, width=stroke)
        draw.polygon([(size * 3 // 4, size // 5),
                      (size * 3 // 4 + size // 8, size // 3),
                      (size * 5 // 8, size // 3)], fill=accent)
    elif kind == "clean":
        draw.line((cx - size // 5, cy - size // 5,
                   cx - size // 7, cy + size // 4),
                  fill=accent, width=stroke)
        draw.line((cx - size // 7, cy + size // 4,
                   cx + size // 5, cy + size // 4),
                  fill=accent, width=stroke)
        draw.line((cx - size // 5, cy - size // 5,
                   cx + size // 5, cy - size // 5),
                  fill=accent, width=stroke)
        draw.polygon([(cx - size // 8, cy - size // 8),
                      (cx + size // 8, cy - size // 8),
                      (cx + size // 11, cy + size // 3),
                      (cx - size // 11, cy + size // 3)], fill=accent)
    elif kind == "diagnostics":
        draw.line((size // 4, cy + size // 5, cx - size // 9, cy),
                  fill=accent, width=stroke)
        draw.line((cx - size // 9, cy, cx + size // 12, cy - size // 5),
                  fill=accent, width=stroke)
        draw.line((cx + size // 12, cy - size // 5, size * 3 // 4, cy + size // 7),
                  fill=accent, width=stroke)
        draw.ellipse((cx - size // 18, cy - size // 18,
                      cx + size // 18, cy + size // 18),
                     fill=accent)
    elif kind == "apps":
        box = size // 4
        for dx, dy in ((0, 0), (box, 0), (0, box), (box, box)):
            draw.rounded_rectangle((size // 4 + dx, size // 4 + dy,
                                    size // 2 + dx, size // 2 + dy),
                                   radius=size // 16, outline=accent, width=stroke)
    elif kind == "performance":
        draw.polygon([(cx - size // 7, cy - size // 3),
                      (cx + size // 4, cy - size // 12),
                      (cx + size // 12, cy + size // 3),
                      (cx - size // 3, cy + size // 12)], outline=accent)
        draw.line((cx - size // 3, cy + size // 12,
                   cx + size // 12, cy + size // 3),
                  fill=accent, width=stroke)
    elif kind == "tools":
        draw.line((size // 4, size * 3 // 4,
                   size * 3 // 4, size // 4),
                  fill=accent, width=stroke)
        draw.ellipse((size // 3, size // 5,
                      size * 2 // 3, size // 2),
                     outline=accent, width=stroke)
    elif kind == "theme":
        draw.arc((size // 4, size // 4, size * 3 // 4, size * 3 // 4),
                 80, 280, fill=accent, width=stroke)
        draw.ellipse((cx - size // 12, cy - size // 12,
                      cx + size // 12, cy + size // 12),
                     fill=accent)

    return ctk.CTkImage(light_image=image, dark_image=image, size=(size, size))

