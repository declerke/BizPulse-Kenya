import sys
sys.path.insert(0, ".")

from unittest.mock import patch, MagicMock


def test_generate_returns_required_keys():
    mock_choice = MagicMock()
    mock_choice.message.content = "Kenya's business environment remains resilient this week."
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("briefing.generator.Groq", return_value=mock_client):
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            from briefing.generator import generate
            result = generate(
                sentiment_summary={"positive_count": 10, "negative_count": 3, "neutral_count": 7},
                top_headlines=["Kenya GDP grows 5%", "Shilling stabilises"],
                cbk_data={"cbr_rate": 8.75, "usd_kes": 129.5},
            )

    assert "id" in result
    assert "week_start" in result
    assert "briefing_text" in result
    assert "model_used" in result
    assert len(result["id"]) == 64


def test_generate_briefing_text_nonempty():
    mock_choice = MagicMock()
    mock_choice.message.content = "Strong sentiment this week driven by positive economic signals."
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("briefing.generator.Groq", return_value=mock_client):
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            from briefing.generator import generate
            result = generate({}, [], {})

    assert len(result["briefing_text"]) > 0
