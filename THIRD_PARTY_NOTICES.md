# Third-party notices

InfusionCalc is licensed under the MIT License. The following bundled or build-time prepared components have their own licenses.

## Roboto fallback font

- Component: Roboto Regular web fallback font
- Copyright: Copyright 2011 The Roboto Project Authors
- Source artifact: `https://fonts.gstatic.com/s/roboto/v32/KFOmCnqEu92Fr1Me4GZLCzYlKw.woff2`
- Pinned SHA-256: `35b02ca266b79eb4996590f15817425a1ce9ebf48f84471843233ff614656bf2`
- Pinned size: `63464` bytes
- License: SIL Open Font License 1.1
- License copy shipped with the PWA: `web/fallback-fonts/roboto/OFL.txt`

## Noto Sans Symbols fallback font

- Component: Noto Sans Symbols web fallback font
- Copyright: Copyright 2022 The Noto Project Authors
- Source artifact: `https://fonts.gstatic.com/s/notosanssymbols/v43/rP2up3q65FkAtHfwd-eIS2brbDN6gxP34F9jRRCe4W3gfQ8gb_VFRkzrbQ.woff2`
- Pinned SHA-256: `08202e258ea583254c036cff46a7077bb5af4f82c41a6c0a6775f6e44d99f1aa`
- Pinned size: `69116` bytes
- License: SIL Open Font License 1.1
- License copy shipped with the PWA: `web/fallback-fonts/notosanssymbols/OFL.txt`

Both fonts are downloaded and checksum-verified during a web build so the installed PWA can render without requesting `fonts.gstatic.com` at runtime. The fonts remain governed by the SIL Open Font License 1.1 and are not relicensed under the project's MIT License.
