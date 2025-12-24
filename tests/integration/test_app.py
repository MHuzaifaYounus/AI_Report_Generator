import pytest
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest

# Mocking the external dependencies
@pytest.fixture(autouse=True)
def mock_dependencies():
    with patch('ai_report_generator.src.data_processor.process_csv') as mock_process_csv, \
         patch('ai_report_generator.src.agent_engine.get_ai_insight') as mock_get_ai_insight:
        
        # Configure mock_process_csv to return a sample stats dictionary
        mock_process_csv.return_value = {
            "overall_summary": {"row_count": 5, "column_count": 2},
            "numeric_columns": {"sales": {"mean": 100.0}},
            "non_numeric_columns": {}
        }
        
        # Configure mock_get_ai_insight to return specific responses based on insight_type
        mock_get_ai_insight.side_effect = lambda stats, insight_type: f"Mocked {insight_type} Insight"

        yield mock_process_csv, mock_get_ai_insight

def test_app_initial_state():
    at = AppTest.from_file("ai_report_generator/app.py")
    at.run()
    
    assert at.title[0].value == "AI Workflow & Report Generator"
    assert at.file_uploader[0].label == "Upload your CSV file"
    assert at.info[0].value == "Please upload a CSV file to get started."

def test_app_upload_and_process_csv(mock_dependencies):
    at = AppTest.from_file("ai_report_generator/app.py")
    at.run()

    # Simulate file upload
    csv_content = "col1,col2\n1,10\n2,20"
    at.file_uploader[0].upload(csv_content.encode('utf-8'), "test.csv", "text/csv")
    at.run() # Rerun app after upload

    assert at.success[0].value == "CSV file processed successfully!"
    assert at.subheader[0].value == "Generate AI Insights"
    mock_dependencies[0].assert_called_once() # Verify process_csv was called

def test_app_trends_button_click(mock_dependencies):
    at = AppTest.from_file("ai_report_generator/app.py")
    at.run()

    # Simulate file upload
    csv_content = "col1,col2\n1,10\n2,20"
    at.file_uploader[0].upload(csv_content.encode('utf-8'), "test.csv", "text/csv")
    at.run()

    # Click the "Trends" button
    at.button[0].click().run() # Assuming "📈 Get Trends" is the first button

    assert at.markdown[0].value == "### Trends Insight"
    assert at.write[1].value == "Mocked Trends Insight"
    mock_dependencies[1].assert_called_with(mock_dependencies[0].return_value, "Trends")

def test_app_anomalies_button_click(mock_dependencies):
    at = AppTest.from_file("ai_report_generator/app.py")
    at.run()

    csv_content = "col1,col2\n1,10\n2,20"
    at.file_uploader[0].upload(csv_content.encode('utf-8'), "test.csv", "text/csv")
    at.run()

    at.button[1].click().run() # Assuming "Anomaly Detection" is the second button

    assert at.markdown[1].value == "### Anomalies Insight"
    assert at.write[2].value == "Mocked Anomalies Insight"
    mock_dependencies[1].assert_called_with(mock_dependencies[0].return_value, "Anomalies")

def test_app_actions_button_click(mock_dependencies):
    at = AppTest.from_file("ai_report_generator/app.py")
    at.run()

    csv_content = "col1,col2\n1,10\n2,20"
    at.file_uploader[0].upload(csv_content.encode('utf-8'), "test.csv", "text/csv")
    at.run()

    at.button[2].click().run() # Assuming "Strategic Actions" is the third button

    assert at.markdown[2].value == "### Strategic Actions Insight"
    assert at.write[3].value == "Mocked Actions Insight"
    mock_dependencies[1].assert_called_with(mock_dependencies[0].return_value, "Actions")

def test_app_error_on_file_processing(mock_dependencies):
    mock_dependencies[0].side_effect = ValueError("Test processing error")
    
    at = AppTest.from_file("ai_report_generator/app.py")
    at.run()

    csv_content = "invalid csv content"
    at.file_uploader[0].upload(csv_content.encode('utf-8'), "bad.csv", "text/csv")
    at.run()

    assert at.error[0].value == "Error: Test processing error"
    assert at.info[0].value == "Please ensure you upload a valid CSV file."
    assert at.session_state['stats_dict'] is None
