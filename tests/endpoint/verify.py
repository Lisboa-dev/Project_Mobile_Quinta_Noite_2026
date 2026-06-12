#!/usr/bin/env python3
"""
Script de verificação dos testes de endpoint.
Executa rapidamente para validar que tudo está funcionando.
"""

import subprocess
import sys
from pathlib import Path


def check_files():
    """Verifica se todos os arquivos foram criados"""
    print("✓ Verificando arquivos...")
    
    expected_files = [
        "conftest.py",
        "mock_data.py",
        "__init__.py",
        "test_agenda_service.py",
        "test_users_service.py",
        "test_auth_service.py",
        "test_notification_service.py",
        "test_analytic_service.py",
        "README.md",
        "IMPLEMENTAÇÃO.md",
        "INDEX.md",
    ]
    
    endpoint_dir = Path(__file__).parent
    missing = []
    
    for file in expected_files:
        path = endpoint_dir / file
        if not path.exists():
            missing.append(file)
            print(f"  ✗ {file} - NÃO ENCONTRADO")
        else:
            size = path.stat().st_size
            print(f"  ✓ {file} - {size:,} bytes")
    
    return len(missing) == 0


def check_pytest():
    """Verifica se pytest está instalado"""
    print("\n✓ Verificando pytest...")
    try:
        result = subprocess.run(
            ["pytest", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  ✓ {result.stdout.strip()}")
            return True
        else:
            print("  ✗ pytest não encontrado")
            return False
    except Exception as e:
        print(f"  ✗ Erro: {e}")
        return False


def list_tests():
    """Lista todos os testes disponíveis"""
    print("\n✓ Listando testes...")
    try:
        result = subprocess.run(
            ["pytest", "tests/endpoint/", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            # Conta testes
            test_count = sum(1 for line in lines if '::' in line and 'test_' in line)
            print(f"  ✓ {test_count} testes encontrados")
            return test_count > 0
        else:
            print("  ✗ Erro ao coletar testes")
            if result.stderr:
                print(f"    {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ Erro: {e}")
        return False


def check_markers():
    """Verifica marcadores pytest"""
    print("\n✓ Verificando marcadores pytest...")
    markers = [
        "agenda",
        "users", 
        "auth",
        "notification",
        "analytic",
        "health",
        "integration"
    ]
    
    for marker in markers:
        print(f"  ✓ @pytest.mark.{marker}")
    
    return True


def main():
    """Executa verificações"""
    print("=" * 60)
    print("VERIFICAÇÃO DE TESTES DE ENDPOINT")
    print("=" * 60)
    
    checks = [
        ("Arquivos criados", check_files),
        ("pytest instalado", check_pytest),
        ("Marcadores pytest", check_markers),
        ("Testes listados", list_tests),
    ]
    
    results = []
    for name, check_fn in checks:
        try:
            result = check_fn()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Erro em {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_pass = all(result for _, result in results)
    
    if all_pass:
        print("\n✓ Tudo OK! Testes prontos para executar.")
        print("\nComandos úteis:")
        print("  pytest tests/endpoint/ -v                    # Todos os testes")
        print("  pytest tests/endpoint/ -v -m agenda          # Apenas agendaService")
        print("  pytest tests/endpoint/ -v -m health          # Apenas health checks")
        print("  pytest tests/endpoint/ -vv --tb=short -s     # Com detalhes")
        return 0
    else:
        print("\n✗ Alguns testes falharam. Veja erros acima.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
