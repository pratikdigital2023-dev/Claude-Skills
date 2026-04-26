---
name: 3d-asset-pipeline
description: Take a 3D asset from Blender / DCC tool to web-ready glTF — modeling tips, materials, baking, Draco/Meshopt compression, KTX2 texture compression, and validation. Use when shipping 3D for WebGL/Three.js scenes.
---

# 3D Asset Pipeline

A 50 MB glTF that looks great in Blender will tank your site. The
pipeline matters as much as the modeling. Goal: < 5 MB total scene,
indistinguishable from the source on screen.

## End-to-end flow

```
Blender (model + UV + bake)
   ↓ export
.glb (binary glTF 2.0)
   ↓ optimize
gltf-transform (Draco/Meshopt + KTX2)
   ↓ validate
gltf-validator
   ↓ ship
/public/models/hero.glb
```

## Modeling guidelines (web)

- **Polycount**: hero asset 30–80k tris max, supporting assets <10k
- **Quads → triangulate on export** (fewer triangles, predictable behavior)
- **Apply all transforms** before export (otherwise scale/rotation issues)
- **One mesh per logical object** (helps Three.js culling + interactivity)
- **No N-gons** — triangulator may produce ugly results
- **Smooth shading** with custom normals where needed (sharp edges)

## UVs

- Single 0–1 UV space per material (no overlapping unless intentional for tiling)
- Pack tightly — wasted UV space = wasted texture memory
- 1 UV map per mesh ideal (2 only if you need separate lightmap UVs)

## Materials (PBR / glTF spec)

glTF supports a fixed PBR material model. In Blender, use **Principled BSDF**
with:
- Base Color (diffuse) — `albedo` map
- Roughness — single channel
- Metallic — single channel
- Normal — tangent-space normal map
- Emissive — for self-lit areas

Pack roughness + metallic into one image (R = unused, G = roughness, B = metallic) — that's what glTF expects.

Avoid Blender-only nodes (procedural noise, math nodes) — bake them down.

## Baking (the secret to small scenes)

Bake complex shaders + lighting to textures:
- **Diffuse bake** — for fully baked scenes (no real-time light)
- **Combined bake** — color + AO + shadows in one map
- **Normal bake** — high-poly to low-poly transfer

Texture sizes:
- Hero textures: 2048×2048
- Supporting: 1024×1024
- Detail / props: 512×512
- Powers of 2 only (GPU friendly)

## Texture compression (KTX2 / Basis)

JPG/PNG decode to uncompressed RGBA in GPU memory. KTX2 (Basis Universal)
stays compressed on the GPU — 4–8× less VRAM.

```bash
npm i -g @gltf-transform/cli
gltf-transform uastc input.glb output-uastc.glb \
  --level 4 --rdo 1.0 --rdo-lambda 1.0
# OR for faster decode + smaller size:
gltf-transform etc1s input.glb output-etc1s.glb --quality 200
```

Three.js loads KTX2 via `KTX2Loader`:
```js
import { KTX2Loader } from 'three/examples/jsm/loaders/KTX2Loader.js'
const ktx2 = new KTX2Loader().setTranscoderPath('/basis/').detectSupport(renderer)
gltfLoader.setKTX2Loader(ktx2)
```

## Geometry compression (Draco vs Meshopt)

- **Draco** — older, great compression (~10× smaller), slow decode on mobile
- **Meshopt** — newer, slightly larger files but 2–3× faster decode + better for animations

**Meshopt is preferred for 2024+** unless extreme compression beats decode time.

```bash
gltf-transform optimize input.glb output.glb \
  --compress meshopt \
  --texture-compress webp
```

For Draco:
```bash
gltf-transform draco input.glb output.glb --quantize-position 14
```

Three.js loaders:
```js
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js'
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js'

const draco = new DRACOLoader().setDecoderPath('/draco/')
gltfLoader.setDRACOLoader(draco)
gltfLoader.setMeshoptDecoder(MeshoptDecoder)
```

## All-in-one optimize

```bash
gltf-transform optimize input.glb output.glb \
  --compress meshopt \
  --texture-compress webp \
  --texture-size 2048 \
  --simplify-error 0.001
```

This will:
- Meshopt compress geometry
- Convert textures to WebP (or specify `ktx2` for GPU compression)
- Resize oversized textures
- Simplify mesh where visually safe

## Validation

```bash
npx gltf-validator input.glb
```

Check for:
- Missing required attributes (position, normal, UV)
- Invalid texture references
- Non-power-of-2 textures (warning)
- Excessive triangle count

Drop the file in https://gltf-viewer.donmccurdy.com/ to preview.

## Animation

- Bake animation in Blender to keyframes (procedural drivers don't export)
- Use **NLA tracks** for clip-based animation
- Export with "Export Deformation Bones Only" if rigged
- Compress animations with Meshopt
- For idle loops, mark them as looping in Three.js (`AnimationAction.setLoop(THREE.LoopRepeat)`)

## Cameras + lights

Don't export Blender cameras + lights for hero scenes — set them up in
Three.js for control. Exception: a configurator with multiple preset views
can bake camera positions.

## File organization

```
/public/models/
├── hero.glb              ← optimized, ready to ship
└── /source/              ← (gitignore) raw .blend, raw exports
```

Never ship the `.blend` or unoptimized `.glb` to production.

## Performance targets

| Scene type | Target size | Tris | Textures |
|---|---|---|---|
| Hero product | < 2 MB | < 50k | 1× 2K + 2× 1K |
| Full landing | < 5 MB | < 150k | 4× 1K |
| Configurator | < 8 MB | < 300k | 6× 2K |
| Game-like | < 15 MB | depends | streaming |

## Mobile considerations

- Test on actual mid-tier Android (Chrome DevTools throttling underestimates GPU limits)
- Provide LOD versions (low/mid/high) and pick by `navigator.deviceMemory`
- Consider static poster image for low-memory devices

## Tools (full list)

- **Blender** — modeling, baking, export
- **gltf-transform** (CLI + JS API) — optimize pipeline
- **glTF Validator** — error checking
- **gltf-viewer** (Don McCurdy) — preview
- **Spector.js** — Chrome DevTools-style WebGL inspector
- **Online: glb.babylonpress.org** — quick optimization
- **Maya / 3ds Max / Houdini** — alternatives to Blender, all export glTF

## Common pitfalls

- Exporting `.gltf` + `.bin` + textures as separate files (use `.glb`)
- Forgetting to apply transforms in Blender (scale issues)
- 4K textures on a hero asset 200px tall (waste)
- Per-vertex colors instead of texture (huge file)
- Multiple UV sets when one would do
- Procedural Blender nodes that don't bake (broken in browser)
- Shipping animation clips you don't use
- Not testing on mid-tier mobile (looks fine in Blender, melts iPhone 11)

## Validation checklist

- [ ] File size < target for scene type
- [ ] Loads in Three.js without errors
- [ ] All textures present + sized correctly
- [ ] Meshopt or Draco compressed
- [ ] KTX2 textures (if appropriate)
- [ ] Validates with gltf-validator
- [ ] Tested on mid-tier Android
- [ ] LOD or fallback for low-memory devices
- [ ] License + attribution documented

## Pricing notes (for proposals)

- Optimize an existing 3D asset for web: 4–8 hrs
- Full asset creation (model + bake + optimize) hero quality: 40–80 hrs
- Full asset creation for configurator: 80–160 hrs
- Engaging a 3D artist subcontractor: $80–200/hr depending on quality

## Anti-patterns

- Shipping the `.blend` workflow file
- Skipping compression "to debug later"
- 8K textures because "we have the source"
- Same model for desktop + mobile (no LOD)
- No license documented for asset
- Letting Blender export defaults run wild (yields 80 MB files)
- Real-time everything when bake would suffice
