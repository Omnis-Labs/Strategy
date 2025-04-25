# AsterDex Strategies Library

<img width="729" alt="image" src="https://github.com/user-attachments/assets/080c60ca-11ed-4d1c-96b3-8df9ac0a3eeb" />


A Python-based bot for implementing a grid trading strategy on the AsterDex cryptocurrency exchange (fapi.asterdex.com).

**Disclaimer:** Trading cryptocurrencies involves significant risk. This software is provided for educational purposes and as a technical example. Use it at your own risk. The author is not responsible for any financial losses.

## Features

*   Connects to the AsterDex Futures API.
*   Implements a logarithmic grid trading strategy.
*   Places buy and sell limit orders based on calculated grid levels.
*   Periodically checks and maintains the grid orders.

## Prerequisites

*   Python 3.7+
*   pip

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-directory>
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    *   Create a file named `.env` in the project's root directory.
    *   Add your AsterDex API key and secret key to the `.env` file like this:
        ```dotenv
        ASTER_API_KEY="YOUR_API_KEY_HERE"
        ASTER_SECRET_KEY="YOUR_SECRET_KEY_HERE"
        ```
    *   **Important:** Ensure the `.env` file is included in your `.gitignore` to prevent accidentally committing your keys.

## Configuration

Strategy parameters are set directly within the main script (`aster_log_grid_strategy.py`):

*   `TARGET_SYMBOL`: The trading pair (e.g., "CRVUSDT").
*   `UPPER_PRICE`: The upper bound of the grid.
*   `LOWER_PRICE`: The lower bound of the grid.
*   `NUM_GRIDS`: The number of grid intervals.
*   `ORDER_QTY_PER_GRID`: The quantity for each buy/sell order.
*   `CHECK_INTERVAL_SECONDS`: How often the bot checks and updates orders.

Adjust these parameters according to your trading strategy and risk tolerance.

## Usage

Run the main strategy script:

```bash
python aster_log_grid_strategy.py
```

The bot will initialize, calculate grid levels, and start placing/maintaining orders based on the current market price and your configuration. Monitor the output for status updates and potential errors.

## License

This work is licensed under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License. To view a copy of this license, visit <http://creativecommons.org/licenses/by-nc-nd/4.0/> or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

[![CC BY-NC-ND 4.0](https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png)](http://creativecommons.org/licenses/by-nc-nd/4.0/) 
