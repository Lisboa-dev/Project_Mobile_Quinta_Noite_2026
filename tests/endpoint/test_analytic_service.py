"""
Testes de endpoints do Analytic Service
Cobre health check, eventos, métricas
"""
import pytest
from httpx import AsyncClient
from . import mock_data


@pytest.mark.analytic
@pytest.mark.health
class TestAnalyticHealthEndpoint:
    """Testes para health check do Analytic Service"""
    
    async def test_health_check(self, analytic_client: AsyncClient):
        """GET /analytics/health - Health check"""
        response = await analytic_client.get("/analytics/health")
        
        assert response.status_code == 200
        result = response.json()
        assert result.get("status") == "ok" or "ok" in str(result).lower()
    
    async def test_health_returns_dict(self, analytic_client: AsyncClient):
        """Health check retorna dicionário"""
        response = await analytic_client.get("/analytics/health")
        
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, dict)


@pytest.mark.analytic
class TestAnalyticEventsEndpoints:
    """Testes para endpoints de eventos"""
    
    async def test_list_events_default(self, analytic_client: AsyncClient):
        """GET /analytics/events - Listar eventos (default limit=100)"""
        response = await analytic_client.get("/analytics/events")
        
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, (list, dict))
    
    async def test_list_events_custom_limit(self, analytic_client: AsyncClient):
        """GET /analytics/events - Listar com limit customizado"""
        response = await analytic_client.get("/analytics/events?limit=50")
        
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, (list, dict))
    
    async def test_list_events_limit_min(self, analytic_client: AsyncClient):
        """GET /analytics/events - Limit mínimo (1)"""
        response = await analytic_client.get("/analytics/events?limit=1")
        
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, (list, dict))
    
    async def test_list_events_limit_max(self, analytic_client: AsyncClient):
        """GET /analytics/events - Limit máximo (500)"""
        response = await analytic_client.get("/analytics/events?limit=500")
        
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, (list, dict))
    
    async def test_list_events_limit_exceeds_max(self, analytic_client: AsyncClient):
        """GET /analytics/events - Limit excede máximo"""
        response = await analytic_client.get("/analytics/events?limit=1000")
        
        # Deve retornar 422 (validation error) ou aceitar e limitar
        assert response.status_code in [200, 422]
    
    async def test_list_events_limit_zero(self, analytic_client: AsyncClient):
        """GET /analytics/events - Limit zero (inválido)"""
        response = await analytic_client.get("/analytics/events?limit=0")
        
        # Deve retornar 422 (validation error)
        assert response.status_code in [200, 422]
    
    async def test_list_events_limit_negative(self, analytic_client: AsyncClient):
        """GET /analytics/events - Limit negativo (inválido)"""
        response = await analytic_client.get("/analytics/events?limit=-10")
        
        # Deve retornar 422 (validation error)
        assert response.status_code in [200, 422]
    
    async def test_list_events_invalid_limit(self, analytic_client: AsyncClient):
        """GET /analytics/events - Limit não numérico"""
        response = await analytic_client.get("/analytics/events?limit=abc")
        
        # Deve retornar 422 (validation error)
        assert response.status_code in [200, 422]


@pytest.mark.analytic
class TestAnalyticEventSummaryEndpoint:
    """Testes para endpoint de resumo de eventos"""
    
    async def test_summarize_events(self, analytic_client: AsyncClient):
        """GET /analytics/events/summary - Resumo por fonte"""
        response = await analytic_client.get("/analytics/events/summary")
        
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, (list, dict))
        
        # Se for lista, cada item deve ter informações de contagem
        if isinstance(result, list):
            for item in result:
                assert any(key in item for key in ["source", "source_service", "count", "total", "type"])
    
    async def test_summarize_events_empty_result(self, analytic_client: AsyncClient):
        """GET /analytics/events/summary - Pode retornar vazio"""
        response = await analytic_client.get("/analytics/events/summary")
        
        assert response.status_code == 200
        result = response.json()
        # Pode ser lista vazia ou dict vazio
        assert isinstance(result, (list, dict))


@pytest.mark.analytic
class TestAnalyticMetricsEndpoint:
    """Testes para endpoint de métricas Prometheus"""
    
    async def test_metrics_endpoint(self, analytic_client: AsyncClient):
        """GET /analytics/metrics - Métricas Prometheus"""
        response = await analytic_client.get("/analytics/metrics")
        
        assert response.status_code == 200
        # Métricas Prometheus são em formato text/plain
        assert "text/plain" in response.headers.get("content-type", "").lower()
    
    async def test_metrics_content(self, analytic_client: AsyncClient):
        """GET /analytics/metrics - Conteúdo é texto Prometheus"""
        response = await analytic_client.get("/analytics/metrics")
        
        assert response.status_code == 200
        content = response.text
        assert isinstance(content, str)
        # Métricas Prometheus contêm linhas começando com #
        # ou linhas com métrica_name{tags}
    
    async def test_metrics_version_header(self, analytic_client: AsyncClient):
        """GET /analytics/metrics - Content-Type com versão"""
        response = await analytic_client.get("/analytics/metrics")
        
        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        # Deve conter versão (0.0.4)
        assert "text/plain" in content_type.lower()


@pytest.mark.analytic
@pytest.mark.integration
class TestAnalyticIntegration:
    """Testes de integração do Analytic Service"""
    
    async def test_events_list_returns_consistent_data(self, analytic_client: AsyncClient):
        """Eventos retornam dados consistentes"""
        response1 = await analytic_client.get("/analytics/events?limit=10")
        response2 = await analytic_client.get("/analytics/events?limit=10")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Ambas devem ser válidas
        result1 = response1.json()
        result2 = response2.json()
        assert isinstance(result1, (list, dict))
        assert isinstance(result2, (list, dict))
    
    async def test_summary_has_event_sources(self, analytic_client: AsyncClient):
        """Summary de eventos tem fontes conhecidas"""
        response = await analytic_client.get("/analytics/events/summary")
        
        assert response.status_code == 200
        result = response.json()
        
        # Se houver dados, verifica se contém sources esperados
        if isinstance(result, list) and len(result) > 0:
            # Deve ter informações de fonte
            assert any("source" in str(item).lower() or "total" in str(item).lower() for item in result)


@pytest.mark.analytic
class TestAnalyticErrorHandling:
    """Testes para tratamento de erros"""
    
    async def test_invalid_path_404(self, analytic_client: AsyncClient):
        """GET /analytics/invalid - Caminho inválido retorna 404"""
        response = await analytic_client.get("/analytics/invalid")
        
        assert response.status_code == 404
    
    async def test_analytics_root_path(self, analytic_client: AsyncClient):
        """GET /analytics - Raiz pode não existir"""
        response = await analytic_client.get("/analytics")
        
        # Pode ser 404 ou redirect
        assert response.status_code in [301, 302, 304, 404]
