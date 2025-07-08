"""
Testes unitários para src/data/operacoes_bd.py
Cobertura completa das funções de operações de banco de dados.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Adicionar o caminho do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data.operacoes_bd import (
    deletar_serie,
    inserir_nova_serie,
    alterar_ultima_atualizacao,
    alterar_ultimo_alerta,
    alterar_ultima_checagem
)


class TestDeletarSerie:
    """Testes para a função deletar_serie"""
    
    @patch('src.data.operacoes_bd.supabase')
    def test_deletar_serie_sucesso(self, mock_supabase):
        """Testa deleção bem-sucedida de uma série"""
        # Configurar mock
        mock_response = MagicMock()
        mock_response.data = [{"id": 1, "codigo_serie": "TEST001", "email_usuario": "test@test.com"}]
        
        # Configurar cadeia de métodos mock
        mock_table = MagicMock()
        mock_delete = MagicMock()
        mock_eq1 = MagicMock()
        mock_eq2 = MagicMock()
        
        mock_supabase.table.return_value = mock_table
        mock_table.delete.return_value = mock_delete
        mock_delete.eq.return_value = mock_eq1
        mock_eq1.eq.return_value = mock_eq2
        mock_eq2.execute.return_value = mock_response
        
        # Executar função
        resultado = deletar_serie("test001", "test@test.com")
        
        # Verificar chamadas
        mock_supabase.table.assert_called_once_with("series")
        mock_table.delete.assert_called_once()
        
        # Verificar que os eq foram chamados corretamente
        eq_calls = mock_delete.eq.call_args_list
        assert len(eq_calls) == 1
        assert eq_calls[0][0] == ("codigo_serie", "TEST001")
        
        eq2_calls = mock_eq1.eq.call_args_list  
        assert len(eq2_calls) == 1
        assert eq2_calls[0][0] == ("email_usuario", "test@test.com")
        
        # Verificar resultado
        assert resultado == mock_response.data
    
    @patch('src.data.operacoes_bd.supabase')
    def test_deletar_serie_nao_encontrada(self, mock_supabase):
        """Testa erro quando série não é encontrada"""
        # Configurar mock para retornar lista vazia
        mock_response = MagicMock()
        mock_response.data = []
        
        mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        # Verificar que ValueError é levantado
        with pytest.raises(ValueError, match="Dados fornecidos não existem no banco de dados."):
            deletar_serie("INEXISTENTE", "test@test.com")
    
    def test_deletar_serie_codigo_vazio(self):
        """Testa erro quando código da série está vazio"""
        with pytest.raises(ValueError, match="Dados insuficientes."):
            deletar_serie("", "test@test.com")
    
    def test_deletar_serie_email_vazio(self):
        """Testa erro quando email está vazio"""
        with pytest.raises(ValueError, match="Dados insuficientes."):
            deletar_serie("TEST001", "")
    
    def test_deletar_serie_ambos_vazios(self):
        """Testa erro quando ambos os parâmetros estão vazios"""
        with pytest.raises(ValueError, match="Dados insuficientes."):
            deletar_serie("", "")
    
    @patch('src.data.operacoes_bd.supabase')
    def test_deletar_serie_erro_supabase(self, mock_supabase):
        """Testa tratamento de erro do Supabase"""
        # Configurar mock para levantar exceção
        mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.side_effect = Exception("Erro de conexão")
        
        # Verificar que a exceção é propagada
        with pytest.raises(Exception, match="Erro de conexão"):
            deletar_serie("TEST001", "test@test.com")


class TestInserirNovaSerie:
    """Testes para a função inserir_nova_serie"""
    
    @patch('src.data.operacoes_bd.supabase')
    def test_inserir_nova_serie_sucesso(self, mock_supabase):
        """Testa inserção bem-sucedida de uma nova série"""
        # Configurar mock
        mock_response = MagicMock()
        mock_response.data = [{
            "id": 1,
            "codigo_serie": "TEST001",
            "email_usuario": "test@test.com",
            "margem": "5.0",
            "ultima_atualizacao": "2025-01-01"
        }]
        
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        # Executar função
        resultado = inserir_nova_serie("TEST001", "test@test.com", "5.0", "2025-01-01")
        
        # Verificar chamadas
        mock_supabase.table.assert_called_once_with("series")
        
        # Verificar dados inseridos
        insert_call = mock_supabase.table.return_value.insert.call_args[0][0]
        assert insert_call == {
            "codigo_serie": "TEST001",
            "email_usuario": "test@test.com",
            "margem": "5.0",
            "ultima_atualizacao": "2025-01-01"
        }
        
        # Verificar resultado
        assert resultado == mock_response.data
    
    def test_inserir_nova_serie_codigo_vazio(self):
        """Testa erro quando código da série está vazio"""
        with pytest.raises(ValueError, match="Dados insuficientes."):
            inserir_nova_serie("", "test@test.com", "5.0", "2025-01-01")
    
    def test_inserir_nova_serie_email_vazio(self):
        """Testa erro quando email está vazio"""
        with pytest.raises(ValueError, match="Dados insuficientes."):
            inserir_nova_serie("TEST001", "", "5.0", "2025-01-01")
    
    def test_inserir_nova_serie_margem_invalida(self):
        """Testa erro quando margem não é um número"""
        with pytest.raises(ValueError, match="Dados insuficientes."):
            inserir_nova_serie("TEST001", "test@test.com", "não_é_número", "2025-01-01")
    
    def test_inserir_nova_serie_margem_vazia(self):
        """Testa erro quando margem está vazia"""
        with pytest.raises(ValueError, match="Dados insuficientes."):
            inserir_nova_serie("TEST001", "test@test.com", "", "2025-01-01")
    
    def test_inserir_nova_serie_ultima_atualizacao_vazia(self):
        """Testa erro quando ultima_atualizacao está vazia"""
        with pytest.raises(ValueError, match="Dados insuficientes."):
            inserir_nova_serie("TEST001", "test@test.com", "5.0", "")
    
    @patch('src.data.operacoes_bd.supabase')
    def test_inserir_nova_serie_erro_supabase(self, mock_supabase):
        """Testa tratamento de erro do Supabase"""
        # Configurar mock para levantar exceção
        mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("Erro de inserção")
        
        # Verificar que a exceção é propagada
        with pytest.raises(Exception, match="Erro de inserção"):
            inserir_nova_serie("TEST001", "test@test.com", "5.0", "2025-01-01")


class TestAlterarUltimaAtualizacao:
    """Testes para a função alterar_ultima_atualizacao"""
    
    @patch('src.data.operacoes_bd.supabase')
    def test_alterar_ultima_atualizacao_sucesso(self, mock_supabase):
        """Testa alteração bem-sucedida da última atualização"""
        # Configurar mock
        mock_response = MagicMock()
        mock_response.data = [{
            "id": "123",
            "ultima_atualizacao": "2025-01-15"
        }]
        
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
        
        # Executar função
        resultado = alterar_ultima_atualizacao("2025-01-15", "123")
        
        # Verificar chamadas
        mock_supabase.table.assert_called_once_with("series")
        mock_supabase.table.return_value.update.assert_called_once_with({"ultima_atualizacao": "2025-01-15"})
        mock_supabase.table.return_value.update.return_value.eq.assert_called_once_with("id", "123")
        
        # Verificar resultado
        assert resultado == mock_response.data
    
    def test_alterar_ultima_atualizacao_data_vazia(self):
        """Testa erro quando data está vazia"""
        with pytest.raises(ValueError, match="Dados insuficientes."):
            alterar_ultima_atualizacao("", "123")
    
    def test_alterar_ultima_atualizacao_id_vazio(self):
        """Testa erro quando ID está vazio"""
        with pytest.raises(ValueError, match="Dados insuficientes."):
            alterar_ultima_atualizacao("2025-01-15", "")
    
    def test_alterar_ultima_atualizacao_ambos_vazios(self):
        """Testa erro quando ambos os parâmetros estão vazios"""
        with pytest.raises(ValueError, match="Dados insuficientes."):
            alterar_ultima_atualizacao("", "")
    
    @patch('src.data.operacoes_bd.supabase')
    def test_alterar_ultima_atualizacao_erro_supabase(self, mock_supabase):
        """Testa tratamento de erro do Supabase"""
        # Configurar mock para levantar exceção
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception("Erro de atualização")
        
        # Verificar que a exceção é propagada
        with pytest.raises(Exception, match="Erro de atualização"):
            alterar_ultima_atualizacao("2025-01-15", "123")


class TestAlterarUltimoAlerta:
    """Testes para a função alterar_ultimo_alerta"""
    
    @patch('src.data.operacoes_bd.supabase')
    def test_alterar_ultimo_alerta_sucesso(self, mock_supabase):
        """Testa alteração bem-sucedida do último alerta"""
        # Configurar mock
        mock_response = MagicMock()
        mock_response.data = [{
            "id": "123",
            "ultimo_alerta": "2025-01-15"
        }]
        
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
        
        # Executar função
        resultado = alterar_ultimo_alerta("2025-01-15", "123")
        
        # Verificar chamadas
        mock_supabase.table.assert_called_once_with("series")
        mock_supabase.table.return_value.update.assert_called_once_with({"ultimo_alerta": "2025-01-15"})
        mock_supabase.table.return_value.update.return_value.eq.assert_called_once_with("id", "123")
        
        # Verificar resultado
        assert resultado == mock_response.data
    
    def test_alterar_ultimo_alerta_data_vazia(self):
        """Testa erro quando data está vazia"""
        with pytest.raises(ValueError, match="Dados insuficientes."):
            alterar_ultimo_alerta("", "123")
    
    def test_alterar_ultimo_alerta_id_vazio(self):
        """Testa erro quando ID está vazio"""
        with pytest.raises(ValueError, match="Dados insuficientes."):
            alterar_ultimo_alerta("2025-01-15", "")
    
    def test_alterar_ultimo_alerta_ambos_vazios(self):
        """Testa erro quando ambos os parâmetros estão vazios"""
        with pytest.raises(ValueError, match="Dados insuficientes."):
            alterar_ultimo_alerta("", "")
    
    @patch('src.data.operacoes_bd.supabase')
    def test_alterar_ultimo_alerta_erro_supabase(self, mock_supabase):
        """Testa tratamento de erro do Supabase"""
        # Configurar mock para levantar exceção
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception("Erro de atualização")
        
        # Verificar que a exceção é propagada
        with pytest.raises(Exception, match="Erro de atualização"):
            alterar_ultimo_alerta("2025-01-15", "123")


class TestAlterarUltimaChecagem:
    """Testes para a função alterar_ultima_checagem"""
    
    @patch('src.data.operacoes_bd.supabase')
    def test_alterar_ultima_checagem_sucesso(self, mock_supabase):
        """Testa alteração bem-sucedida da última checagem"""
        # Configurar mock
        mock_response = MagicMock()
        mock_response.data = [{
            "id": "123",
            "ultima_checagem": "2025-01-15"
        }]
        
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
        
        # Executar função
        resultado = alterar_ultima_checagem("2025-01-15", "123")
        
        # Verificar chamadas
        mock_supabase.table.assert_called_once_with("series")
        mock_supabase.table.return_value.update.assert_called_once_with({"ultima_checagem": "2025-01-15"})
        mock_supabase.table.return_value.update.return_value.eq.assert_called_once_with("id", "123")
        
        # Verificar resultado
        assert resultado == mock_response.data
    
    def test_alterar_ultima_checagem_data_vazia(self):
        """Testa erro quando data está vazia"""
        with pytest.raises(ValueError, match="Dados insuficientes."):
            alterar_ultima_checagem("", "123")
    
    def test_alterar_ultima_checagem_id_vazio(self):
        """Testa erro quando ID está vazio"""
        with pytest.raises(ValueError, match="Dados insuficientes."):
            alterar_ultima_checagem("2025-01-15", "")
    
    def test_alterar_ultima_checagem_ambos_vazios(self):
        """Testa erro quando ambos os parâmetros estão vazios"""
        with pytest.raises(ValueError, match="Dados insuficientes."):
            alterar_ultima_checagem("", "")
    
    @patch('src.data.operacoes_bd.supabase')
    def test_alterar_ultima_checagem_erro_supabase(self, mock_supabase):
        """Testa tratamento de erro do Supabase"""
        # Configurar mock para levantar exceção
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception("Erro de atualização")
        
        # Verificar que a exceção é propagada
        with pytest.raises(Exception, match="Erro de atualização"):
            alterar_ultima_checagem("2025-01-15", "123")


class TestParametrosEspeciais:
    """Testes para casos especiais e edge cases"""
    
    @patch('src.data.operacoes_bd.supabase')
    def test_deletar_serie_codigo_minusculo(self, mock_supabase):
        """Testa se código em minúsculo é convertido para maiúsculo"""
        # Configurar mock
        mock_response = MagicMock()
        mock_response.data = [{"id": 1, "codigo_serie": "TEST001"}]
        
        # Configurar cadeia de métodos mock
        mock_table = MagicMock()
        mock_delete = MagicMock()
        mock_eq1 = MagicMock()
        mock_eq2 = MagicMock()
        
        mock_supabase.table.return_value = mock_table
        mock_table.delete.return_value = mock_delete
        mock_delete.eq.return_value = mock_eq1
        mock_eq1.eq.return_value = mock_eq2
        mock_eq2.execute.return_value = mock_response
        
        # Executar função com código em minúsculo
        deletar_serie("test001", "test@test.com")
        
        # Verificar que o código foi convertido para maiúsculo
        eq_calls = mock_delete.eq.call_args_list
        assert len(eq_calls) == 1
        assert eq_calls[0][0] == ("codigo_serie", "TEST001")
    
    def test_inserir_nova_serie_margem_numero_valido(self):
        """Testa inserção com margem válida (número)"""
        # Este teste verifica que números válidos passam na validação
        with patch('src.data.operacoes_bd.supabase') as mock_supabase:
            mock_response = MagicMock()
            mock_response.data = [{"id": 1}]
            mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
            
            # Deveria funcionar sem erro
            resultado = inserir_nova_serie("TEST001", "test@test.com", "10.5", "2025-01-01")
            assert resultado == mock_response.data
    
    def test_inserir_nova_serie_margem_zero(self):
        """Testa inserção com margem zero"""
        with patch('src.data.operacoes_bd.supabase') as mock_supabase:
            mock_response = MagicMock()
            mock_response.data = [{"id": 1}]
            mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
            
            # Margem zero deveria ser válida
            resultado = inserir_nova_serie("TEST001", "test@test.com", "0", "2025-01-01")
            assert resultado == mock_response.data
    
    def test_inserir_nova_serie_margem_negativa(self):
        """Testa inserção com margem negativa"""
        with patch('src.data.operacoes_bd.supabase') as mock_supabase:
            mock_response = MagicMock()
            mock_response.data = [{"id": 1}]
            mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
            
            # Margem negativa deveria ser válida se for número
            resultado = inserir_nova_serie("TEST001", "test@test.com", "-5.0", "2025-01-01")
            assert resultado == mock_response.data


class TestCasosLimite:
    """Testes para casos limite e validações especiais"""
    
    def test_inserir_nova_serie_margem_string_numerica(self):
        """Testa inserção com margem como string numérica"""
        with patch('src.data.operacoes_bd.supabase') as mock_supabase:
            mock_response = MagicMock()
            mock_response.data = [{"id": 1}]
            mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
            
            # String numérica deveria funcionar
            resultado = inserir_nova_serie("TEST001", "test@test.com", "15.75", "2025-01-01")
            assert resultado == mock_response.data
    
    def test_inserir_nova_serie_margem_inteiro(self):
        """Testa inserção com margem como inteiro"""
        with patch('src.data.operacoes_bd.supabase') as mock_supabase:
            mock_response = MagicMock()
            mock_response.data = [{"id": 1}]
            mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
            
            # Inteiro deveria funcionar
            resultado = inserir_nova_serie("TEST001", "test@test.com", "10", "2025-01-01")
            assert resultado == mock_response.data
    
    @patch('src.data.operacoes_bd.supabase')
    def test_funcoes_update_com_ids_numericos(self, mock_supabase):
        """Testa funções de update com IDs numéricos"""
        mock_response = MagicMock()
        mock_response.data = [{"id": 123}]
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
        
        # Testar com ID numérico como string
        resultado = alterar_ultima_atualizacao("2025-01-15", "123")
        assert resultado == mock_response.data
        
        # Verificar chamada
        mock_supabase.table.return_value.update.return_value.eq.assert_called_with("id", "123")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
