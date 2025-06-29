#!/usr/bin/env python3
"""
Runner para CronJob - Verificação de Atualização de Séries
Projeto: GovInsights
"""
import os
import sys
from pathlib import Path

# Configurar Python path para import correto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

from services.async_service.cronJob import verificar_atualizacao_series

if __name__ == "__main__":
    print("🚀 Iniciando verificação de atualização de séries...")
    verificar_atualizacao_series()
    print("✅ Verificação concluída.")