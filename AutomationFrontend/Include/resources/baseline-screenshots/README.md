# Visual Baseline Screenshots

This directory stores baseline screenshots for visual regression testing via `ScreenshotPage.groovy`.

## How it works

1. **First run:** `ScreenshotPage.captureAndCompare("screen_name")` saves the current screen as the baseline (file: `screen_name.png`). Test passes with log "Baseline saved."
2. **Subsequent runs:** The current screen is compared against the baseline. If pixel difference exceeds the threshold (default 2%), the test fails with the diff percentage.
3. **After intentional UI change:** Call `ScreenshotPage.updateBaseline("screen_name")` from a maintenance script, then commit the updated baseline.

## Baseline files (established on first run)

| File | Captured at | Test Case |
|---|---|---|
| `home_screen.png` | Rappi Home tab visible | TC_CompraProductosTurboDev |
| `cart_badge_visible.png` | After adding products to TurboStore cart | TC_CompraProductosTurboDev |
| `checkout_payment_screen.png` | Payment method selection screen | TC_CompraProductosTurboDev |
| `order_tracking_success.png` | Order Tracking screen after purchase | TC_CompraProductosTurboDev |

## Device dependency

Baselines are device-specific (resolution, density, UI scaling).
Current device: **Samsung Galaxy S24 Ultra (SM-S928B)** — 1080×2340 px, 480 dpi.

If running on a different device, update the device subfolder logic in `ScreenshotPage.groovy`
or re-capture baselines.

## Ignoring actual screenshots in version control

Add this to `.gitignore`:
```
Include/resources/baseline-screenshots/actual_*.png
```
