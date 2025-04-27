# Omnis Strategy Library

<img width="729" alt="image" src="https://github.com/user-attachments/assets/080c60ca-11ed-4d1c-96b3-8df9ac0a3eeb" />
<p align="center">Visit the <a href="https://omnis-interface.vercel.app" target="_blank">demo site</a></p>
<p align="center">Read the <a href="https://omnis-labs.gitbook.io/v1" target="_blank">documentation</a></p>
<br />

**Omnis Strategy Library** provides battle-tested DeFi strategy implementations, optimized for on-chain deployment and off-chain execution environments (will move to on-chain in the future).
The current repository focuses on **AsterDex Futures strategies** — enabling scalable, automated trading across perpetual markets using structured grid systems.

---

## ✨ Strategies Included

- 🟢 **Aster Points Maximizer** — Rapid trading loops to optimize Aster reward point accumulation.
- 📈 **Normal Grid Strategy** — Equal-spaced grids for sideways or range-bound markets.
- 📈 **Logarithmic Grid Strategy** — Exponentially spaced grids to capture wide, volatile market movements.

Each strategy is engineered to be modular, transparent, and compatible with secure API key setups.

---

## 🛠️ Tech Stack

| Layer       | Tools Used                                |
| ----------- | ----------------------------------------- |
| Core Engine | Python 3.7+, Decimal Precision, Requests  |
| Secrets     | dotenv for environment-based API security |
| Exchange    | AsterDex Futures API                      |

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Omnis-Labs/Strategy.git
cd Strategy
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```dotenv
ASTER_API_KEY="YOUR_API_KEY_HERE"
ASTER_SECRET_KEY="YOUR_SECRET_KEY_HERE"
```

🔒 Make sure your `.env` is excluded from version control (`.gitignore`).

---

## ⚙️ Strategy Configuration

Each strategy script (e.g., `aster_log_grid_strategy.py`) allows simple parameter customization:

| Parameter             | Description                                   |
| ---------------------- | --------------------------------------------- |
| `TARGET_SYMBOL`        | Trading pair symbol (e.g., `CRVUSDT`)         |
| `UPPER_PRICE` & `LOWER_PRICE` | Price boundaries for grid placement    |
| `NUM_GRIDS`            | Number of grid levels                        |
| `ORDER_QTY_PER_GRID`   | Quantity allocated per order                 |
| `CHECK_INTERVAL_SECONDS` | How often the system checks and updates     |

Adjust these according to your risk appetite and market expectations.

---

## 🧠 Usage

To launch a strategy:

```bash
python aster_log_grid_strategy.py
```

The system will:
- Initialize secure API connections
- Calculate optimal grid levels
- Place and maintain dynamic buy/sell orders based on real-time market data

Logs will provide clear updates on status, fills, and error handling.

---

## 📝 License

This project is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)** license.

You are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material

Under the following terms:
- **Attribution** — You must give appropriate credit.
- **NonCommercial** — You may not use the material for commercial purposes.
- **ShareAlike** — If you remix, transform, or build upon the material, you must distribute your contributions under the same license.

🔗 [Read the full license here](https://creativecommons.org/licenses/by-nc-sa/4.0/)
