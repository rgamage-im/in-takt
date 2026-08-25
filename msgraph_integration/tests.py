from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from .ai_service import CompanyAssistantService


class CompanyAssistantServiceTests(SimpleTestCase):
    def _mock_completion(self, content):
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
        )

    @patch("msgraph_integration.ai_service.OpenAI")
    def test_uses_gpt_oss_120b_by_default(self, mock_openai):
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}, clear=True):
            service = CompanyAssistantService()

        self.assertEqual(service.model, "openai/gpt-oss-120b")
        mock_openai.assert_called_once_with(
            base_url="https://api.groq.com/openai/v1",
            api_key="test-key",
        )

    @patch("msgraph_integration.ai_service.OpenAI")
    def test_uses_groq_model_override_for_all_completions(self, mock_openai):
        completion_create = MagicMock()
        mock_openai.return_value.chat.completions.create = completion_create

        with patch.dict(
            "os.environ",
            {"GROQ_API_KEY": "test-key", "GROQ_MODEL": "custom/model"},
            clear=True,
        ):
            service = CompanyAssistantService()

        completion_create.side_effect = [
            self._mock_completion("project budget"),
            self._mock_completion("The budget is approved."),
        ]

        self.assertEqual(
            service.extract_search_keywords("What happened to the project budget?"),
            "project budget",
        )
        self.assertEqual(
            service.synthesize_answer("Was it approved?", "[1] Budget memo"),
            "The budget is approved.",
        )
        self.assertEqual(completion_create.call_count, 2)
        for call in completion_create.call_args_list:
            self.assertEqual(call.kwargs["model"], "custom/model")

    @patch("msgraph_integration.ai_service.OpenAI")
    def test_blank_groq_model_uses_default(self, mock_openai):
        with patch.dict(
            "os.environ",
            {"GROQ_API_KEY": "test-key", "GROQ_MODEL": "   "},
            clear=True,
        ):
            service = CompanyAssistantService()

        self.assertEqual(service.model, "openai/gpt-oss-120b")
