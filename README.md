# AI Workflow & Report Generator

This application allows non-technical users to upload a CSV file and receive instant AI-generated insights into Trends, Anomalies, and Strategic Actions using Streamlit and Gemini 2.5 Flash.

## Features

*   **CSV Upload**: Easily upload your data.
*   **Trends Analysis**: Get AI-powered summaries of key trends and growth.
*   **Anomaly Detection**: Identify significant outliers and unusual patterns.
*   **Strategic Actions**: Receive actionable recommendations based on your data.
*   **Speed-First**: Designed for rapid insights (under 5 seconds response time).
*   **User-Friendly**: Intuitive interface for non-technical managers.

## Quickstart

This guide will help you set up and run the AI Workflow & Report Generator application locally.

### Prerequisites

*   Python 3.12+
*   Git (for cloning the repository)

### Setup Instructions

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd ai_report_generator/
    ```
    *(Note: Replace `<repository-url>` with your actual repository URL)*

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: `.\venv\Scripts\activate`
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up API Key**:
    The application uses Gemini 2.5 Flash via OpenAI Agents SDK. You need to provide your API key.
    ```bash
    export OPENAI_API_KEY="your_gemini_api_key_here"
    # Or, for local development, create a .env file in the `ai_report_generator/` directory with:
    # OPENAI_API_KEY="your_gemini_api_key_here"
    ```
    *(Note: Replace `your_gemini_api_key_here` with your actual API key)*

### Running the Application

1.  **Ensure your virtual environment is active** and API key is set.
2.  **Navigate to the `ai_report_generator` directory**.
3.  **Run the Streamlit application**:
    ```bash
    streamlit run app.py
    ```
4.  The application will open in your web browser, typically at `http://localhost:8501`.

### Usage

1.  Upload a CSV file using the file uploader component.
2.  Click one of the three buttons ("Trends", "Anomalies", "Actions") to generate AI-powered insights.
3.  The insights will be displayed on the page.

---
