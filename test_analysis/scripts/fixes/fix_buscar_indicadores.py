#!/usr/bin/env python3
"""
Script para corrigir chamadas buscar_indicadores para search no test_end_to_end_workflow.py
"""

import re

def fix_buscar_indicadores_calls():
    file_path = "tests/integration/test_end_to_end_workflow.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrões para buscar e substituir
    patterns = [
        # Padrão 1: buscar_indicadores com tema
        (
            r'self\.search_service\.buscar_indicadores\(\s*tema="([^"]+)"[^)]*\)',
            r'self.search_service.search(frequency="Mensal", fonte_list=["IBGE"], tema_list=[{"THEME CODE": 1, "THEME NAME": "\1"}])'
        ),
        # Padrão 2: buscar_indicadores genérico
        (
            r'self\.search_service\.buscar_indicadores\([^)]+\)',
            r'self.search_service.search(frequency="Mensal", fonte_list=["IBGE"], tema_list=[{"THEME CODE": 1, "THEME NAME": "Economia"}])'
        )
    ]
    
    original_content = content
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Arquivo corrigido com sucesso!")
        print("Mudanças realizadas:")
        
        # Mostrar diferenças
        old_lines = original_content.split('\n')
        new_lines = content.split('\n')
        
        for i, (old, new) in enumerate(zip(old_lines, new_lines)):
            if old != new:
                print(f"Linha {i+1}:")
                print(f"  - {old}")
                print(f"  + {new}")
    else:
        print("ℹ️  Nenhuma mudança necessária")

if __name__ == "__main__":
    fix_buscar_indicadores_calls()
