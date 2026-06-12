#!/usr/bin/env python3
"""
Script para verificar e executar testes E2E.
Fornece interface amigável para rodar testes contra API real.
"""

import subprocess
import sys
from pathlib import Path
from typing import List
import os


class TestRunner:
    """Gerenciador de execução de testes"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.root_dir = self.test_dir.parent.parent.parent
    
    def check_deps(self) -> bool:
        """Verifica dependências"""
        print("\n📦 Verificando dependências...")
        deps = ["pytest", "httpx"]
        
        for dep in deps:
            try:
                __import__(dep.replace("-", "_"))
                print(f"  ✅ {dep}")
            except ImportError:
                print(f"  ❌ {dep} - Instale com: pip install {dep}")
                return False
        
        return True
    
    def check_services(self) -> bool:
        """Verifica se services estão respondendo"""
        print("\n🏥 Verificando services...")
        
        services = {
            "agendaService": "http://localhost:8000",
            "analyticService": "http://localhost:8001",
            "authService": "http://localhost:8002",
            "notificationService": "http://localhost:8003",
            "usersService": "http://localhost:8004",
        }
        
        all_up = True
        for name, url in services.items():
            try:
                import httpx
                with httpx.Client(timeout=2.0) as client:
                    r = client.get(f"{url}/health")
                    if r.status_code == 200:
                        print(f"  ✅ {name}")
                    else:
                        print(f"  ⚠️  {name} (status {r.status_code})")
            except Exception as e:
                print(f"  ❌ {name}")
                all_up = False
        
        if not all_up:
            print("\n  💡 Inicie com: docker compose up -d --build")
            return False
        
        return True
    
    def run_tests(self, test_type: str = "all") -> int:
        """Executa testes"""
        
        commands = {
            "all": ["pytest", "tests/endpoint/", "-v"],
            "flow": ["pytest", "tests/endpoint/", "-v", "-m", "flow", "-s"],
            "health": ["pytest", "tests/endpoint/", "-v", "-m", "health"],
            "integration": ["pytest", "tests/endpoint/", "-v", "-m", "integration"],
            "quick": ["pytest", "tests/endpoint/", "-v", "-m", "health", "--maxfail=1"],
        }
        
        if test_type not in commands:
            print(f"❌ Tipo desconhecido: {test_type}")
            self.show_help()
            return 1
        
        os.chdir(self.root_dir)
        cmd = commands[test_type]
        
        print(f"\n▶️  Executando: {' '.join(cmd)}\n")
        
        try:
            result = subprocess.run(cmd)
            return result.returncode
        except KeyboardInterrupt:
            print("\n⚠️  Testes interrompidos")
            return 1
    
    def show_help(self):
        """Mostra ajuda"""
        print("""
╔═══════════════════════════════════════════════════════════╗
║         TESTES E2E - AGENDAMENTO MÉDICO                  ║
╚═══════════════════════════════════════════════════════════╝

Tipos de testes:
  all          - Todos os testes
  flow         - Fluxos E2E completos ✨
  health       - Health checks
  integration  - Testes de integração
  quick        - Health + um fluxo

Uso:
  python run_e2e.py [tipo]

Exemplos:
  python run_e2e.py          # Todos os testes
  python run_e2e.py flow     # Apenas fluxos
  python run_e2e.py health   # Health checks

Requisitos:
  - docker compose up -d --build  (services rodando)
  - pip install pytest pytest-asyncio httpx

Documentação:
  - GUIDE.md         - Guia completo
  - IMPLEMENTAÇÃO.md - Detalhes técnicos
  - INDEX.md         - Índice de testes
""")
    
    def main(self):
        """Execução principal"""
        test_type = sys.argv[1] if len(sys.argv) > 1 else "all"
        
        if test_type in ["-h", "--help", "help"]:
            self.show_help()
            return 0
        
        if not self.check_deps():
            print("\n❌ Dependências faltam")
            return 1
        
        if not self.check_services():
            print("\n⚠️  Alguns services não estão respondendo")
            try:
                response = input("  Continuar mesmo assim? (s/n): ")
                if response.lower() != "s":
                    return 1
            except KeyboardInterrupt:
                return 1
        
        print("\n" + "="*60)
        return self.run_tests(test_type)


if __name__ == "__main__":
    runner = TestRunner()
    sys.exit(runner.main())
