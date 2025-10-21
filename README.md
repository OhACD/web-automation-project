# Web Automation Project

This project provides a FastAPI-based API to automate login and price retrieval for the "Sauce Labs Backpack" product on the [SauceDemo](https://www.saucedemo.com/) website. It uses Playwright for browser automation and is designed for the SauceDemo website as part of an internship project for the General Services Department.

## Overview

The project includes:
- A FastAPI server (`app.py`) with a POST `/automate` endpoint to trigger automation.
- An automation script (`main.py`) that logs into SauceDemo, checks for the "Sauce Labs Backpack" product, and retrieves its price.
- A test client in `test_api.py` to call the API.

## Prerequisites

- Python 3.8+
- Playwright browser dependencies
- Dependencies: `fastapi`, `uvicorn`, `requests`, `playwright`

## Setup

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd web-automation-project
   ```

2. **Install Dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install fastapi==0.115.0 uvicorn==0.30.6 requests==2.32.3 playwright==1.47.0
   playwright install
   ```

3. **Set Environment Variables**:
   Create a `.env` file:
   ```plaintext
   SAUCE_USER=standard_user
   SAUCE_PASS=secret_sauce
   HEADLESS=true
   ```

4. **Run the FastAPI Server**:
   ```bash
   uvicorn app:app --host 127.0.0.1 --port 8000 --reload
   ```

5. **Test the API**:
   Run the test client:
   ```bash
   python test_api.py
   ```
   Or send a POST request to `http://127.0.0.1:8000/automate` with:
   ```json
   {"run": true}
   ```

## API Documentation

### `POST /automate`

- **Description**: Triggers automation to log into SauceDemo and retrieve the price of "Sauce Labs Backpack".
- **Request Body**:
  ```json
  {"run": true}
  ```
- **Response**:
  - Success:
    ```json
    {
      "status": "success",
      "result": {
        "status": "success",
        "product": "Sauce Labs Backpack",
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
- `main.py`: Automation script (`run_automation`).
- `test_api.py`: API Test Client.
- `.env`: Environment variables (optional).
- `requirements.txt`: Dependencies (optional).

## Notes

- Designed for SauceDemo; may break if the website's HTML changes.
- The API uses a subprocess to run `main.py`.
- No authentication, not suitable for public deployment.

## Troubleshooting

- **Timeout Errors**: Check internet connection or increase timeouts in `main.py`.
- **Login Issues**: Verify `SAUCE_USER` and `SAUCE_PASS` in `.env`.
- **API Failure**: Ensure server is running and port 8000 is open.