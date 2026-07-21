# Appium Classifier Plugin — Training Labels

This directory contains training images for the `appium-classifier-plugin` (Test.ai).
Each subdirectory is a label that can be passed to `VisualLocatorPage.findByVisual()`.

## Adding a new label

1. Create a subdirectory with the label name (snake_case)
2. Add 3–5 diverse sample PNG screenshots (cropped to the element)
3. Aim for variety: different app states, dark/light mode, screen sizes

## Available labels

| Label | Usage |
|---|---|
| `shopping_cart_icon` | Cart button in TurboStore and home header |
| `checkout_button` | "Ir a pagar" button in Canasta |
| `add_to_cart_button` | "+" add button in product grids |

## Capturing sample images

```bash
# Capture full screen
adb shell screencap -p /sdcard/screen.png && adb pull /sdcard/screen.png

# Then crop to the element using any image editor
# Save as: Include/resources/classifier-labels/<label>/sample_01.png
```

## Plugin setup

```bash
# From project root:
npm install --save-dev appium-classifier-plugin

# Add to Katalon Desired Capabilities (Project → Settings → Desired Capabilities → Mobile → Android):
# customFindModules = {"test-ai": "test.ai/appium-classifier-plugin"}
# shouldUseCompactResponses = false
```
