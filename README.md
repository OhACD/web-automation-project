# Web Automation Project

This project automates login and price retrieval for the "Sauce Labs Backpack" product on the [SauceDemo](https://www.saucedemo.com/) website. It provides a FastAPI-based API and a standalone script, using Playwright for browser automation.

## Overview

The project includes:
- `app.py`: FastAPI server with a POST `/automate` endpoint to trigger automation.
- `main.py`: Standalone script with `run_automation` to log into SauceDemo and retrieve the product price.
- `test_api.py`: Test client to call the API.

## Prerequisites

- Python 3.8+
- Playwright browser dependencies
- Dependencies: `fastapi`, `uvicorn`, `requests`, `playwright`

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/OhACD/web-automation-project
   cd web-automation-project
   ```

2. **Install Dependencies**:
   ```bash
   python -m venv venv
   source .venv/Scripts/activate.ps1  
   pip install -r requirements.txt
   pip install -r dev-requirements.txt
   pip install "httpx>=0.27.0" "httpcore>=1.0.0"
   playwright install
   ```

3. **Set Environment Variables**:
   Create a `.env` file:
   ```plaintext
   SAUCE_USER=standard_user
   SAUCE_PASS=secret_sauce
   ITEM_TO_LOOKUP=Sauce Labs Bolt T-shirt
   HEADLESS=true
   ```

4. **Run the FastAPI Server** (for API usage):
   ```bash
   uvicorn app:app --host 127.0.0.1 --port 8000
   ```

5. **Run the Automation**:
   - **Via API**: In a separate terminal, run:
     ```bash
     python test_api.py
     ```
     Or send a POST request to `http://127.0.0.1:8000/automate`:
     ```json
     {"run": true} or
     {"run": true, "item": "{item_name}"}
     ```
   - **Directly**: Run the standalone script:
     ```bash
     python main.py
     ```

## API Documentation

### `POST /automate`

- **Description**: Triggers automation to log into SauceDemo and retrieve the price of "Sauce Labs Backpack".
- **Request Body**:
  ```json
  {"run": true, "item": "{item_name}"}
  ```
- **Response**:
  - Success:
    ```json
    {
      "status": "success",
      "result": {
        "status": "success",
        "product": "Product Name",
        "price": "$29.99"
      }
    }
    ```
  - Error:
    ```json
    {
      "status": "error",
      "result": "Error message"
    }
    ```
- **Swagger UI**: `http://127.0.0.1:8000/docs`

## Project Structure

- `app.py`: FastAPI server with `/automate` endpoint.
- `main.py`: Standalone automation script (`run_automation`).
- `test_api.py`: API testing.
- `post_request.py`: Example of sending a post request.
- `.env`: Environment variables (optional).
- `requirements.txt`: Dependencies.
- `dev-requirements.txt`: Dependencies.

## Notes

- Designed for SauceDemo; may break if the website’s HTML changes.
- No authentication; intended for local use.
- Automation takes 2–5 seconds due to browser operations.

## Troubleshooting

- **Connection Error**: If `python test_api.py` fails with a connection error, ensure the FastAPI server is running (`uvicorn app:app --host 127.0.0.1 --port 8000`) in a separate terminal.
- **Timeout Errors**: Check internet connection or increase timeouts in `main.py` (e.g., `timeout=20000`).
- **Login Issues**: Verify `SAUCE_USER` and `SAUCE_PASS` in `.env`.
