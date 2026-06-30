# Connect Four — 3D (Three.js)

A browser‑based **Connect Four** game rendered in **3D** with [Three.js](https://threejs.org/). Players drop discs into a 7‑column, 6‑row board inside a 3D scene with a glTF environment model, custom textures, and HDR sky lighting.

## Features

- Full game loop: column drops with gravity, alternating turns, reset
- **Win detection** across horizontal, vertical, and both diagonals (4 in a row)
- 3D scene with model loading (glTF), textures, and an EXR sky
- Clean split between **game logic** and **rendering**

## Project layout

| File / folder | Role |
|---|---|
| `index.html` | Landing page / menu |
| `SinglePlayer.html`, `GamePage.html` | Game screens |
| `JavaScript/logica.js` | Pure game logic — board state, `play()`, `checkWin()`, `resetGame()` |
| `JavaScript/appThree.js` | Three.js scene, rendering, and input wiring |
| `JavaScript/three.js` | Vendored Three.js library (no install needed) |
| `casa_model/` | glTF environment model |
| `textures/` | Grass texture + HDR (`.exr`) sky |
| `images/` | Backgrounds and `styles.css` |

## How to run

The game uses **ES module imports**, so it must be served over HTTP — opening the HTML directly as a `file://` will fail due to browser module/CORS rules.

```bash
# from this folder
python3 -m http.server 8000
# or
npx serve

# then open
http://localhost:8000/index.html
```

There is **no `npm install`** — Three.js is vendored in `JavaScript/three.js`.

## Skills demonstrated

- Setting up a real‑time 3D scene (camera, lights, asset loading) in Three.js
- Implementing board‑game logic and an efficient directional win‑detection scan
- Separating concerns: game rules independent of the rendering layer
