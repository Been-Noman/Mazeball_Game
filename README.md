# Mazeball Game
### Project Overview: **MAZEBALL (Ultimate Edition)**

**MAZEBALL** is a fast-paced, two-player local multiplayer arcade game built in Python using the Pygame framework. It seamlessly blends the mechanical tension of classic **Football (Soccer)** with the chaotic, shifting spatial puzzles of a **Maze Crawler**.

Players control stylized cybernetic robots on a high-visibility, warm yellowish-green stadium pitch. The ultimate goal is simple: maneuver a physical, spinning soccer ball into the opposing team's goal net to score points. However, a dynamic twist elevates the core gameplay—the stadium's interior architecture structurally shifts and morphs into a brand-new maze layout every 60 seconds.

---

### Key Structural Pillars

* **Dynamic Maze Engine:** Features a procedural generation algorithm that carves out complex grid pathways over the pitch. It features strict spatial constraints that keep the player spawn territories and white-lined goal zones completely clear of obstacles, guaranteeing a fair runway for attacking plays.
* **Tactile Physics Grid:** Implements customized sub-step collision handling and elastic bounces. When a robot collides with the ball, velocity vectors translate into realistic speed boosts and visual ball spin.
* **Immersive Arcade HUD:** Employs a premium, clean futuristic user interface. It tracks real-time scoreboard states, features a countdown timer tracking the next maze structural shift, and displays a responsive control map for both competitive sides right on the terminal screen.
