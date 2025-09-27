# skyscraper-surfers

An endless runner game built with **Python**, **Pygame**, and **Numba** for [PyWeek 20th anniversary](https://pyweek.org/40/)

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/RedDoughnut/skyscraper-surfers.git
cd skyscraper-surfers
```
### 2. Create a virtual environment
```bash
python -m venv venv
```
### 3. Activate the virtual environment
Windows (CMD):
```bash
.\venv\Scripts\Activate.bat
```
Linux/macOS:
```bash
source venv/bin/activate
```
### 4. Install dependencies
```bash
pip install -r requirements.txt
```
Dependancies: [pygame](https://www.pygame.org/news), [numba](https://numba.pydata.org/) & [numpy](https://numpy.org/) (all are in `requirements.txt` file)
### 5. Run the game
```bash
python main.py
```
---
### Notes
- The first run will be slower and you may experience some lag due to Numba JIT warmup.
- After the first run, cached compilation makes the game much faster.
