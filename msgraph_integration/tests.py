from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from rest_framework.test import APIRequestFactory

from django.test import SimpleTestCase

from .ai_service import CompanyAssistantService
from .api_views import AssistantChatAPIView, _graph_result_count, _search_graph_with_fallback
from .services_delegated import GraphTokenExpiredError


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
        keyword_call, synthesis_call = completion_create.call_args_list
        self.assertEqual(keyword_call.kwargs["model"], "custom/model")
        self.assertEqual(keyword_call.kwargs["reasoning_effort"], "low")
        rewrite_instructions = keyword_call.kwargs["messages"][0]["content"]
        self.assertIn(
            "Preserve words or phrases enclosed in double quotation marks verbatim",
            rewrite_instructions,
        )
        self.assertIn("do not add generic intent words", rewrite_instructions)
        self.assertEqual(synthesis_call.kwargs["model"], "custom/model")
        self.assertNotIn("reasoning_effort", synthesis_call.kwargs)

    @patch("msgraph_integration.ai_service.OpenAI")
    def test_blank_groq_model_uses_default(self, mock_openai):
        with patch.dict(
            "os.environ",
            {"GROQ_API_KEY": "test-key", "GROQ_MODEL": "   "},
            clear=True,
        ):
            service = CompanyAssistantService()

        self.assertEqual(service.model, "openai/gpt-oss-120b")


class AssistantSearchFallbackTests(SimpleTestCase):
    def _graph_response(self, hits):
        return {"value": [{"hitsContainers": [{"hits": hits}]}]}

    def test_counts_nested_graph_search_hits(self):
        response = {
            "value": [
                {"hitsContainers": [{"hits": [{"id": "1"}]}, {"hits": [{"id": "2"}]}]},
                {"hitsContainers": [{"hits": [{"id": "3"}]}]},
            ]
        }

        self.assertEqual(_graph_result_count(response), 3)

    def test_retries_original_question_when_rewrite_has_no_hits(self):
        graph_service = MagicMock()
        fallback_response = self._graph_response([{"id": "original-hit"}])
        graph_service.global_search.side_effect = [self._graph_response([]), fallback_response]

        result = _search_graph_with_fallback(
            graph_service=graph_service,
            access_token="token",
            rewritten_query='"panel anatomy"',
            original_question='what does the term "panel anatomy" mean?',
            use_ai_query=True,
            source_name="sharepoint",
        )

        self.assertIs(result, fallback_response)
        self.assertEqual(
            graph_service.global_search.call_args_list,
            [
                (("token", '"panel anatomy"'), {"size": 10}),
                (("token", 'what does the term "panel anatomy" mean?'), {"size": 10}),
            ],
        )

    def test_keeps_rewritten_results_without_fallback(self):
        graph_service = MagicMock()
        primary_response = self._graph_response([{"id": "rewritten-hit"}])
        graph_service.global_search.return_value = primary_response

        result = _search_graph_with_fallback(
            graph_service=graph_service,
            access_token="token",
            rewritten_query="project budget",
            original_question="What happened to the project budget?",
            use_ai_query=True,
            source_name="email",
            entity_types=["message"],
        )

        self.assertIs(result, primary_response)
        graph_service.global_search.assert_called_once_with(
            "token", "project budget", size=10, entity_types=["message"]
        )


class AssistantExpiredTokenTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch("msgraph_integration.api_views._log_company_assistant_search")
    @patch("msgraph_integration.api_views.GraphServiceDelegated")
    @patch("msgraph_integration.ai_service.CompanyAssistantService")
    def test_graph_expiration_is_not_swallowed_when_notion_succeeds(
        self,
        mock_assistant_class,
        mock_graph_service_class,
        _mock_log,
    ):
        assistant = mock_assistant_class.return_value
        assistant.extract_search_keywords.return_value = "project budget"
        graph_service = mock_graph_service_class.return_value
        graph_service.global_search.side_effect = GraphTokenExpiredError("expired")

        request = self.factory.post(
            "/graph/api/assistant/chat/",
            {
                "question": "What happened to the project budget?",
                "sources": ["sharepoint", "notion"],
            },
            format="json",
        )
        request.session = {
            "graph_access_token": "expired-token",
            "graph_refresh_token": "stale-refresh-token",
            "graph_token_expires_in": 3600,
        }

        with patch(
            "msgraph_integration.api_views._search_notion_rag",
            return_value={"results": [{"content": "Notion-only result"}]},
        ):
            response = AssistantChatAPIView.as_view()(request)

        self.assertEqual(response.status_code, 401)
        self.assertTrue(response.data["auth_required"])
        self.assertEqual(response.data["login_url"], "/graph/login/")
        self.assertNotIn("graph_access_token", request.session)
        self.assertNotIn("graph_refresh_token", request.session)
        self.assertNotIn("graph_token_expires_in", request.session)
        assistant.chat.assert_not_called()

    def test_missing_graph_token_returns_auth_required_marker(self):
        request = self.factory.post(
            "/graph/api/assistant/chat/",
            {"question": "What happened?", "sources": ["notion"]},
            format="json",
        )
        request.session = {}

        response = AssistantChatAPIView.as_view()(request)

        self.assertEqual(response.status_code, 401)
        self.assertTrue(response.data["auth_required"])
        self.assertEqual(response.data["login_url"], "/graph/login/")

    @patch("msgraph_integration.api_views._log_company_assistant_search")
    @patch("msgraph_integration.api_views.GraphServiceDelegated")
    @patch("msgraph_integration.ai_service.CompanyAssistantService")
    def test_non_auth_source_failure_marks_partial_answer_incomplete(
        self,
        mock_assistant_class,
        mock_graph_service_class,
        _mock_log,
    ):
        assistant = mock_assistant_class.return_value
        assistant.extract_search_keywords.return_value = "project budget"
        assistant.chat.return_value = {"answer": "Notion found a budget note.", "sources": []}
        graph_service = mock_graph_service_class.return_value
        graph_service.global_search.side_effect = RuntimeError("Graph unavailable")

        request = self.factory.post(
            "/graph/api/assistant/chat/",
            {
                "question": "What happened to the project budget?",
                "sources": ["sharepoint", "notion"],
            },
            format="json",
        )
        request.session = {"graph_access_token": "valid-token"}

        with patch(
            "msgraph_integration.api_views._search_notion_rag",
            return_value={"results": [{"content": "Notion result"}]},
        ):
            response = AssistantChatAPIView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["unavailable_sources"], ["sharepoint"])
        self.assertIn("incomplete", response.data["warning"])
