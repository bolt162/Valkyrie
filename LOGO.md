# Valkyrie Logo Integration Guide

## Logo Placement

Your Valkyrie logo has been integrated into the application with **theme-aware switching** in the following locations:

### 1. **Application Sidebar** (Main Navigation)
- **Location:** Top-left of the sidebar
- **Size:** 40×40px
- **Files:**
  - Dark Mode: `/frontend/public/white_logo.png`
  - Light Mode: `/frontend/public/black_logo.png`
- **Fallback:** Shield icon (if logo not found)

### 2. **Landing Page**
- **Location:** Navigation bar (top-left)
- **Size:** 40×40px
- **Files:**
  - Dark Mode: `/frontend/public/white_logo.png`
  - Light Mode: `/frontend/public/black_logo.png`
- **Also in:** Footer (28×28px, theme-aware)
- **Fallback:** Shield icon (if logo not found)

### 3. **Login Page**
- **Location:** Center, above "Sign in to Valkyrie" text
- **Size:** 64×64px
- **Files:**
  - Dark Mode: `/frontend/public/white_logo.png`
  - Light Mode: `/frontend/public/black_logo.png`
- **Fallback:** Shield icon (if logo not found)

### 4. **PDF Reports**
- **Location:** Cover page, centered at top
- **Size:** 1.5×1.5 inches (108×108px at 72 DPI)
- **File Path:** `/frontend/public/black_logo.png` (fixed for printing)
- **Fallback:** Text-only if logo not found

---

## How to Add Your Logo

### Step 1: Prepare Your Logos

**You need TWO logo versions for theme-aware switching:**

1. **White Logo** (for dark mode)
   - Light/white colored logo that shows well on dark backgrounds
   - Filename: `white_logo.png`

2. **Black Logo** (for light mode and PDFs)
   - Dark/black colored logo that shows well on light backgrounds
   - Filename: `black_logo.png`

**Recommended Specifications (for both files):**
- **Format:** PNG with transparent background (preferred)
- **Dimensions:** Square aspect ratio (1:1)
- **Minimum Size:** 512×512px (will be scaled down automatically)
- **Background:** Transparent is REQUIRED for proper theme switching
- **File Size:** Keep under 200KB each for optimal loading performance

### Step 2: Place the Logo Files

1. Navigate to your project directory:
   ```bash
   cd /Users/kartikeysharma/Downloads/LLM-Canvas/frontend/public/
   ```

2. Place BOTH logo files with exact names:
   ```
   white_logo.png  (for dark mode)
   black_logo.png  (for light mode)
   ```

   **Full paths should be:**
   ```
   /Users/kartikeysharma/Downloads/LLM-Canvas/frontend/public/white_logo.png
   /Users/kartikeysharma/Downloads/LLM-Canvas/frontend/public/black_logo.png
   ```

### Step 3: Verify Integration

1. **Start the application:**
   ```bash
   # Backend (in one terminal)
   cd /Users/kartikeysharma/Downloads/LLM-Canvas/backend
   ./venv/bin/python main.py

   # Frontend (in another terminal)
   cd /Users/kartikeysharma/Downloads/LLM-Canvas/frontend
   npm run dev
   ```

2. **Check these pages:**
   - Landing page: `http://localhost:3000/`
   - Login page: `http://localhost:3000/login`
   - Dashboard: `http://localhost:3000/app/dashboard`

3. **Test theme switching:**
   - Toggle between light and dark mode using the sun/moon icon
   - Verify white logo appears in dark mode
   - Verify black logo appears in light mode

4. **Test PDF reports:**
   - Run a test and download the PDF report to see black logo on cover page

---

## Fallback Behavior

If the logo file is not found or fails to load:
- A **green Shield icon** will be displayed instead
- The application will continue to work normally
- No errors will be shown to the user

This ensures the application remains functional even without a logo.

---

## Logo Design Tips for Valkyrie

Since Valkyrie is a **security testing platform**, consider these design elements:

### Theme Colors:
- **Primary:** Green (#10b981) - already used throughout the app
- **Accent:** Dark Gray/Black for contrast
- **Optional:** White/light elements for dark mode compatibility

### Design Style:
- **Minimalistic:** Clean, modern, professional
- **Security-focused:** Consider incorporating:
  - Shield shapes
  - Lock/key elements
  - Network/circuit patterns
  - Scanning/radar motifs
  - Norse mythology elements (Valkyrie theme)

### Examples of What Works:
✅ Simple shield with circuit pattern
✅ Stylized "V" with security elements
✅ Minimalist Norse wing/helmet icon
✅ Abstract network/scan visualization

### What to Avoid:
❌ Too much detail (won't scale well at small sizes)
❌ Multiple colors (keep it 2-3 max)
❌ Text in the logo (you have "Valkyrie" text separately)
❌ Complex gradients (may not work in all contexts)

---

## Different Sizes Explained

The logo appears in different sizes across the application:

| Location | Size | Purpose |
|----------|------|---------|
| Sidebar | 40×40px | Navigation branding |
| Landing Navbar | 40×40px | Page header |
| Footer | 28×28px | Subtle branding |
| Login Page | 64×64px | Main focal point |
| PDF Cover | 108×108px | Professional reports |

All sizes are automatically scaled from your source `logo.png` file, so you only need **one file** at high resolution (512×512px or larger).

---

## Testing Your Logo

### Light Mode Test:
1. Visit `http://localhost:3000/`
2. Ensure your logo is visible and looks good on white background
3. Check navigation bar, footer, and sidebar

### Dark Mode Test:
1. Click the sun/moon icon in the top-right corner
2. Verify logo looks good on dark background
3. If using a dark logo, consider creating `logo-dark.png` variant

### Multi-page Test:
Visit each page to verify logo placement:
- ✅ Landing: `/`
- ✅ Login: `/login`
- ✅ Dashboard: `/app/dashboard`
- ✅ Projects: `/app/projects`
- ✅ API Testing: `/app/api-testing`

---

## Theme-Aware Logo Switching

The application **automatically switches logos** based on the current theme:

- **Dark Mode:** Uses `white_logo.png` (light-colored logo for dark backgrounds)
- **Light Mode:** Uses `black_logo.png` (dark-colored logo for light backgrounds)
- **PDF Reports:** Always uses `black_logo.png` (optimized for printing)

This ensures optimal visibility and branding across all contexts.

### Design Tips for Theme-Aware Logos:

**White Logo (for dark mode):**
- Use white, light gray, or your brand's light color scheme
- Ensure good contrast against dark backgrounds (#0a0a0a, black)
- Test visibility with green accent color (#10b981)

**Black Logo (for light mode):**
- Use black, dark gray, or your brand's dark color scheme
- Ensure good contrast against light backgrounds (white, #f9fafb)
- Should work well when printed (used in PDF reports)

---

## Troubleshooting

### Logo not showing up?

1. **Check file paths:**
   ```bash
   ls -la frontend/public/white_logo.png
   ls -la frontend/public/black_logo.png
   ```
   Both files should exist.

2. **Check file permissions:**
   ```bash
   chmod 644 frontend/public/white_logo.png
   chmod 644 frontend/public/black_logo.png
   ```

3. **Clear browser cache:**
   - Press `Cmd + Shift + R` (Mac) or `Ctrl + Shift + R` (Windows)
   - Or open DevTools and disable cache

4. **Check browser console:**
   - Open DevTools (F12)
   - Look for 404 errors for `white_logo.png` or `black_logo.png`
   - The error will show the exact path being requested

### Logo not switching with theme?

1. **Verify both files exist** - missing one file will cause issues
2. **Check file names are exact** - `white_logo.png` and `black_logo.png` (lowercase, underscore)
3. **Restart the frontend** - `npm run dev` to reload assets

### Logo looks pixelated?

- Ensure your source file is at least 512×512px
- Use PNG format for best quality
- Consider using SVG for perfect scaling

### Logo doesn't work in PDF?

- Make sure the file path in `report_generator.py` is correct:
  ```python
  logo_path = "frontend/public/black_logo.png"
  ```
- Check that the black logo file exists and is accessible from the backend directory
- PDF reports always use the black logo (optimized for printing)

---

## Current Logo Status

**Status:** 🟡 Placeholder Ready (Awaiting Logo Files)

The application is fully configured with theme-aware logo switching. Simply add your TWO logo files to:
```
/Users/kartikeysharma/Downloads/LLM-Canvas/frontend/public/white_logo.png
/Users/kartikeysharma/Downloads/LLM-Canvas/frontend/public/black_logo.png
```

Until then, the Shield icon will serve as a placeholder in both light and dark modes.

---

## Quick Checklist

- [ ] White logo file created (PNG, square, 512×512px minimum)
- [ ] Black logo file created (PNG, square, 512×512px minimum)
- [ ] Both logos have transparent backgrounds
- [ ] White logo is visible on dark backgrounds
- [ ] Black logo is visible on light backgrounds
- [ ] Files named exactly `white_logo.png` and `black_logo.png`
- [ ] Both files placed in `frontend/public/` directory
- [ ] Frontend restarted to see changes
- [ ] Tested on Landing page (both themes)
- [ ] Tested on Login page (both themes)
- [ ] Tested in Dashboard sidebar (both themes)
- [ ] Toggled theme to verify logo switching
- [ ] Downloaded PDF report to verify black logo appears

---

**Need Help?**

If you encounter any issues with logo integration, check:
1. File exists at the correct path
2. File permissions are correct
3. Browser cache is cleared
4. Application has been restarted

The fallback Shield icon ensures the app works perfectly while you prepare your custom logo!
