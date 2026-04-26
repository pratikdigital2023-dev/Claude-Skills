---
name: webgl-three-js
description: Build high-end WebGL hero scenes, product reveals, and interactive 3D using Three.js and React Three Fiber (R3F). Covers scene setup, camera/lighting, performance budgets, postprocessing, shader basics, and mobile/perf fallbacks. Use when a site needs Apple/Stripe-tier 3D, not a generic canvas widget.
---

# WebGL / Three.js / R3F

WebGL is what separates "very good agency site" from "Apple-tier". Use it
when the visual idea cannot be expressed in CSS/SVG/video alone — bespoke
materials, real-time interaction, scroll-driven 3D, GPU-only effects.

## When to use

- Hero scene that responds to scroll / cursor / device tilt
- Product reveal (rotate, explode, configurator)
- Particle systems, fluid sims, displacement effects
- Custom shaders for materials no CSS filter can do
- Anything where the design comp shows depth, refraction, caustics

## When NOT to use

- A static image or short MP4 would do the job
- Battery-constrained mobile is the primary audience and you have no fallback
- The team can't maintain GLSL post-launch

## Stack

For React projects, default to:
- `three` — core engine
- `@react-three/fiber` (R3F) — declarative React renderer
- `@react-three/drei` — common helpers (OrbitControls, useGLTF, Environment)
- `leva` — debug GUI (dev only)
- `@react-three/postprocessing` — Bloom, DoF, chromatic aberration
- `r3f-perf` — perf HUD in dev

For vanilla JS: `three` + your own minimal scaffold.

## Project setup (R3F)

```tsx
// app/scene.tsx
'use client'
import { Canvas } from '@react-three/fiber'
import { Environment, OrbitControls } from '@react-three/drei'
import { Suspense } from 'react'
import { Model } from './model'

export function Scene() {
  return (
    <Canvas
      dpr={[1, 2]}                    // cap pixel ratio at 2 (battery)
      gl={{ antialias: true, alpha: true }}
      camera={{ position: [0, 0, 5], fov: 35 }}
      shadows
    >
      <Suspense fallback={null}>
        <ambientLight intensity={0.2} />
        <directionalLight position={[5, 5, 5]} intensity={1} castShadow />
        <Environment preset="studio" />
        <Model />
        <OrbitControls enableZoom={false} />
      </Suspense>
    </Canvas>
  )
}
```

## Performance budgets

Target on a mid-tier laptop and a 2-year-old phone:
- 60 fps desktop, 30 fps mobile floor
- Total scene < 5 MB (compressed glTF + textures)
- Draw calls < 100, triangles < 250k
- One render target unless you really need more
- Texture atlases over many small textures

Measure with `r3f-perf` in dev and Chrome DevTools Performance tab.

## Asset pipeline

See the `3d-asset-pipeline` skill for the full Blender → glTF → Draco/Meshopt
workflow. Quick rules:
- Export `.glb` (binary glTF), not `.gltf` + bin
- Compress with Meshopt (`gltf-transform optimize`) — 60–80% smaller
- KTX2 / Basis textures for GPU-native compression
- Strip unused materials, animations, vertex attributes

## Loading

```tsx
import { useGLTF } from '@react-three/drei'
useGLTF.preload('/models/hero.glb')

function Model() {
  const { scene } = useGLTF('/models/hero.glb')
  return <primitive object={scene} />
}
```

Always preload + show a Suspense fallback. Never block first paint on a 3D
asset.

## Lighting recipes

- **Studio product**: `Environment preset="studio"` + 1 key light
- **Outdoor**: HDRI environment + `directionalLight` for sun
- **Cinematic dark**: low ambient + 2-3 colored rim lights + bloom
- Bake static lighting in Blender when possible, ship lit textures

## Camera + scroll

Tie scroll to camera with GSAP ScrollTrigger or `@react-three/drei`'s
`<ScrollControls>`:

```tsx
import { ScrollControls, useScroll } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'

function Rig() {
  const scroll = useScroll()
  useFrame(({ camera }) => {
    camera.position.z = 5 - scroll.offset * 3
    camera.lookAt(0, 0, 0)
  })
  return null
}
```

## Postprocessing (use sparingly)

Bloom + chromatic aberration is the "premium" preset. Don't stack 6 effects
— each is a full-screen pass.

```tsx
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing'
<EffectComposer>
  <Bloom intensity={0.4} luminanceThreshold={0.9} />
  <Vignette offset={0.3} darkness={0.5} />
</EffectComposer>
```

## Custom shaders (GLSL)

For one-off materials, use `shaderMaterial` from drei or write a `RawShaderMaterial`. Keep it small — most "wow" effects are 30 lines of GLSL.

Common patterns:
- Vertex displacement (waves, ripples, jelly)
- Fresnel rim light (`pow(1 - dot(normal, view), 3)`)
- Noise-based dissolve
- Gradient maps for stylized shading
- Refraction / glass via screen-space sampling

Reference: The Book of Shaders, Three.js examples, ShaderToy.

## Mobile + accessibility fallbacks

- Detect with `navigator.deviceMemory < 4` or `navigator.hardwareConcurrency < 4` → swap for poster image / video
- Respect `prefers-reduced-motion` → freeze scene or skip postprocessing
- Provide a `<picture>` fallback inside `<noscript>` for SEO/social previews
- Test with throttled CPU + 4G in DevTools

```tsx
const reduced = useReducedMotion()
if (reduced) return <img src="/hero-static.jpg" alt="" />
```

## Common pitfalls

- Loading 50 MB glTFs (compress + Draco/Meshopt)
- Re-creating geometry/materials per render (memoize with `useMemo`)
- Running heavy logic in `useFrame` without throttling
- Not capping `dpr` (retina × no cap = 4× pixels = melted GPU)
- Shipping `OrbitControls` in production hero (users zoom it into oblivion)
- Using `<mesh receiveShadow castShadow>` everywhere (shadows are expensive)
- Forgetting to call `dispose()` on unmount in vanilla three.js

## Debugging

- `r3f-perf` HUD for FPS, draw calls, GPU memory
- `three.js inspector` Chrome extension
- `gl.debug = true` to surface WebGL errors
- Spector.js for frame-by-frame GPU capture

## SEO / social

WebGL is invisible to crawlers + Open Graph. Always:
- Render a static poster image as `<img>` fallback under the canvas
- Provide an OG image of the same scene
- Don't put primary content (text, links) inside the canvas

## Reference implementations to study

- apple.com product pages (Vision Pro, AirPods)
- stripe.com homepage gradient
- linear.app feature scenes
- bruno-simon.com (the gold standard for craft)
- vercel.com hero blocks

## Pricing notes (for proposals)

- Simple R3F hero (preset model + basic interaction): 20–40 hrs
- Custom 3D hero with shader work: 60–120 hrs
- Full product configurator: 150–300 hrs
- Always include perf budget + mobile fallback in scope, not as a phase 2

## Anti-patterns

- "We'll add a 3D scene later" without budget — it's never simple
- No fallback for low-end devices (you'll lose 20% of users)
- Auto-rotating hero forever (battery drain, motion sickness)
- WebGL behind a tab the user has to find
- Shipping the dev `OrbitControls` to production
- 4K textures on a hero element 600px tall
- Not respecting `prefers-reduced-motion`
