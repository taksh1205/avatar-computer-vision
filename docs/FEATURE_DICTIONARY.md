# Avatar Vision — feature dictionary

Generated from `src/avatar_vision/feature_registry.py` using `python scripts/build_feature_dictionary.py`.

## Image-derived measurements

All below are deterministic OpenCV statistics on decoded **BGR** images. They are not learned AI predictions or judgments about a person.

| Output field | Meaning | Unit / domain | Computation | Interpretation limit |
|---|---|---|---|---|
| `image_width_px` | Raster width | pixels, integer >= 2 | Decoded image width | Depends on image export size |
| `image_height_px` | Raster height | pixels, integer >= 2 | Decoded image height | Depends on image export size |
| `mean_saturation_0_255` | Mean HSV saturation | OpenCV HSV saturation [0, 255] | Mean S channel of BGR->HSV | Not a calibrated measure of perceived colorfulness |
| `mean_brightness_0_255` | Mean HSV value | OpenCV HSV V [0, 255] | Mean V channel of BGR->HSV | Sensitive to lighting and export processing |
| `contrast_sd` | Gray intensity standard deviation | gray-level standard deviation | Population SD of grayscale pixels | Global contrast proxy; no semantic content |
| `entropy_bits` | Shannon entropy of grayscale histogram | bits per pixel intensity (0–8) | Entropy over 256 intensity bins | Not a measure of model uncertainty |
| `edge_density` | Fraction of nonzero Canny edge pixels | fraction [0, 1] | Canny thresholds 60 and 140 on grayscale | Threshold-dependent, not object-boundary accuracy |
| `laplacian_variance` | Variance of grayscale Laplacian response | squared response units | OpenCV CV_64F Laplacian variance | Sharpness proxy; sensitive to noise and scaling |
| `symmetry_pixel_proxy_0_1` | Normalized left-right grayscale similarity | score [0, 1] | 1 - mean(abs(gray-flipped gray))/255 | Pixel proxy, not facial or aesthetic symmetry |
| `local_texture_proxy` | Mean absolute grayscale residual after 3x3 blur | gray-level absolute deviation | Mean abs(gray - GaussianBlur(3x3)) | Texture proxy; not a trained texture classifier |

## Filename-encoded experimental design factors

These represent **the avatar design file naming scheme**, not information inferred about participants.

| Output field | Meaning | Values / domain | Provenance | Interpretation limit |
|---|---|---|---|---|
| `design_type` | Avatar kind encoded in filename | string | Name convention | Not visually detected |
| `design_gender` | Creator-design category encoded in filename | male/female code | Name convention | Not a demographic prediction, identity or sex inference |
| `design_emotion` | Generator-design emotion label | happy/neutral code | Name convention | Not an expression-recognition model |
| `design_color` | Encoded palette label | string | Name convention | May differ from actual measured pixels |
| `design_attire` | Encoded clothing-design label | formal/informal code | Name convention | Not a clothing classifier |
| `design_logo` | Encoded logo-design label | string | Name convention | Not logo detection |
| `design_variant` | Design variant index | positive integer | Name convention | Not a numerical rank of visual quality |

## Provenance and measurement controls

- Pixel metrics are measured from decoded images; their values depend on resolution, compression, color handling and crop. Compare groups only after a consistent preprocessing policy.
- Name-derived design labels are provided by the generator and require independent verification against the original design documentation if used inferentially.
- The 54-column historical exports must not be identified with the ten new pixel measurements.
- Keep missing avatar references as missing. Never convert absence into a zero-valued image.
- Participant joins need reviewed session mappings before inferential analysis.

## Historical catalog scope

Historical catalog fields and 54-column exploratory exports are source-specific. The new pixel extractor does not claim to reproduce those columns, train a classifier, identify facial anatomy, or validate prior human annotations.
