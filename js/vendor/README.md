# QR encoder

`qrcodegen.js` is the unmodified JavaScript build published by Project Nayuki:
https://www.nayuki.io/res/qr-code-generator-library/qrcodegen.js

Retrieved October 20, 2026. SHA-256 of the distributed bytes:
`2511bc17f40a3c41d4a0578995db956b38997334d3d20113a5d4dc5c49c69480`

Documentation/source: https://www.nayuki.io/page/qr-code-generator-library
Upstream repository: https://github.com/nayuki/QR-Code-generator
Upstream master at review: `3c6d0b3cefb4e049dc337e82237c9644399716a8`.
The web build is pinned by its own hash; upstream commit equivalence is not assumed.

The MIT copyright/license notice is retained in the file. The encoder has no
runtime network or package dependencies. Application code renders numeric QR
modules into a local SVG data URI with four-module quiet borders and medium
error correction. It never inserts source text into SVG markup. Do not replace
this file with a live CDN dependency or remove the license notice.
