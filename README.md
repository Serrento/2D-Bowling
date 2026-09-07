# 🎳 OpenGL Bowling Game

A simple interactive **2D Bowling Game** built with **Python, PyOpenGL, and GLUT**.

The project demonstrates fundamental Computer Graphics concepts including:

- Midpoint Line Drawing Algorithm
- Midpoint Circle Drawing Algorithm
- Collision detection
- Basic game physics & curve mechanics
- Keyboard interaction
- Score tracking & limited tries system
- Start screen, pause, and game-over states

---

## 🎮 Features

- 🎳 Interactive bowling gameplay
- 🔴 Movable bowling ball with side-to-side positioning
- 🌀 **Dynamic Spin & Hook Mechanics:** Control left/right spin curve intensity
- 🎯 **Visual Trajectory Preview:** Arc line projecting the curved path of the ball
- ⚡ **Two-Tap Power Charging Meter:** Tap space to charge, tap again to release
- 🎯 Collision detection with pins
- 💥 Pin scattering physics
- 🏆 Score system with high score tracking during runtime
- 🔢 **3 Tries Round System:** 3 attempts to knock down all pins in a round
- ▶️ Start screen
- ⏸️ Pause functionality
- 🔄 Reset functionality
- ❌ Quit button
- ⌨️ Keyboard controls

---

## 🛠️ Technologies Used

- Python 3
- PyOpenGL
- PyOpenGL_accelerate
- GLUT / FreeGLUT

---

## 🚀 How to Run

[#-how-to-run](#-how-to-run)

1. **Clone the repository**
```bash
   git clone https://github.com/Serrento/2D-Bowling.git
   cd 2D-Bowling
```

2. **Install dependencies**
```bash
   pip install -r requirements.txt
```

3. **Run the game**
```bash
   python bowling_game.py
```

**Requirements:** Python 3.8+, and a system with OpenGL support (most systems have this by default).

## 📁 Project Structure

```text
opengl-bowling-game/
│
├── bowling_game.py
├── requirements.txt
├── README.md
└── .gitignore
