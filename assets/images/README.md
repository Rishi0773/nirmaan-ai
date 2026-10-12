# NIRMAAN AI: Image Assets Guide

Place your image files in this folder (`assets/images/`). The application is pre-configured with graceful fallbacks (e.g. dark navy gradient for the hero banner, vector glyphs for avatars and logos), so the application runs seamlessly even if images are omitted.

---

## Required & Supported Image Asset Paths

| Filename | Path | Recommended Dimensions / Format | Purpose & Description | Fallback Behavior if Absent |
|:---|:---|:---|:---|:---|
| **`bengaluru_hero.jpg`** | `assets/images/bengaluru_hero.jpg` | **1920 × 1080 px** (or 2560 × 1440 px), High-res JPEG/PNG | Clean, wide photograph of Vidhana Soudha, Bengaluru City Hall, or an iconic civic cityscape. Used as the main backdrop behind the translucent hero banner. | Beautiful dark navy and emerald gradient overlay (`linear-gradient(135deg, #0A1128, #101F42, #0F3854)`). |
| **`nirmaan_logo.png`** | `assets/images/nirmaan_logo.png` | **256 × 256 px** (Transparent PNG) | Primary NIRMAAN AI municipal logo or civic emblem. Displayed in the top navigation bar and sidebar. | Styled ♻️ emerald civic insignia and typographic logo. |
| **`nirmaan_avatar.png`** | `assets/images/nirmaan_avatar.png` | **128 × 128 px** (Transparent PNG or SVG) | Civic Assistant chat avatar icon for the floating assistant panel. | Stylized 🤖/🛡️ civic agent avatar badge. |
| **`empty_state.png`** | `assets/images/empty_state.png` | **400 × 300 px** (Transparent PNG) | Clean empty-state illustration for zero-complaint states or empty search queries. | Clean typography card with informational guidance. |

---

## Configuration Note
The hero image path is also configurable in `src/config.py` via `HERO_IMAGE_PATH`. To use a different photo, either place your file at `assets/images/bengaluru_hero.jpg` or adjust the setting in `src/config.py`.
