# Desktop UI review — 10 October 2026

Branch: `feature/desktop-viewport-dashboard`.

## Audit

The original Flutter page used one vertical `ListView`. At 1280 × 720, only the patient section and the first solution fields were visible. The tall field cards, section spacing, separate utility row, and stacked footer accounted for most of the page height.

The retained information and actions are: title, clear all, purpose warning, language switch, patient mass and helper, drug amount, solution volume, concentration, flow, dose mode and dose field, all unit selectors, entered/calculated/error states, validation messages, live calculation note, main result selection, other calculated values, infusion duration, calculation trace and copy action, PWA invitation when supported, and every footer link.

## Changes

- Added a three-column Flutter dashboard for viewports at least 1100 px wide and 600 px high. The existing narrow layout remains in use below that breakpoint.
- Kept all editable fields and unit selectors, with compact spacing on desktop. The current calculated fact is prominent in the result column; the remaining calculated facts and duration appear below it.
- Placed calculation details in a dialog on desktop. Field errors keep a visible red state and appear in the result column's validation summary; the field icon also has the full error as a tooltip.
- Shortened the desktop header and footer. The calculator session, solver, equations, formatting, and safety policy were not modified.

## Viewport checks at 100% zoom

Both the browser viewport and the Flutter dashboard's vertical scroll extent were checked. The filled cases were also checked after switching the interface to English. Each saved image has the stated pixel dimensions.

| Viewport | Empty | Filled reference case | Vertical or horizontal page scroll |
| --- | --- | --- | --- |
| 1280 × 720 | PASS | PASS | None |
| 1366 × 768 | PASS | PASS | None |
| 1440 × 900 | PASS | PASS | None |
| 1920 × 1080 | PASS | PASS | None |

The reference case used 70 kg, 4 mg in 50 ml, and 5 ml/h. The displayed dose was **0,095238095 µg/kg/min** and duration **10 h**. In the reverse browser check, 0,1 µg/kg/min produced **5,25 ml/h**. Changing 4 mg to µg displayed **4000 µg** while concentration stayed **80 µg/ml**. The unit list and details dialog opened without clipping, keyboard focus was visible, and the technical purpose warning remained readable.

The widget tests also checked the shortest desktop viewport with an invalid field and populated data, as well as a long numerical result. These retained zero vertical scroll extent and produced no render overflow. At unusual zoom levels or smaller windows, the page can scroll so text and warnings remain accessible.

The 390 × 844 mobile screenshot before and after is pixel-identical. The mobile layout and its scrolling behavior are unchanged.

## Automated verification

- `flutter analyze --fatal-warnings` and final `dart analyze lib test`: no issues.
- `flutter test --no-pub`: **190 passed**.
- `test/presentation/desktop_dashboard_test.dart`: four viewport scenarios plus invalid and long-value scenarios passed.

## Screenshots

- [Before, desktop 1280 × 720](before-1280x720.jpg)
- [After, empty desktop 1280 × 720](after-empty-1280x720.jpg)
- [After, filled desktop 1280 × 720](after-filled-1280x720.jpg)
- [Reverse calculation](after-reverse-1280x720.jpg)
- [Validation message](after-validation-1280x720.jpg)
- [Technical purpose warning](after-warning-1280x720.jpg)
- [Mobile before](before-mobile-390x844.jpg) and [mobile after](after-mobile-390x844.jpg)

The other three desktop sizes have corresponding `after-empty-*` and `after-filled-*` captures in this directory.
