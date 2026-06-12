#!/bin/bash

# Script para executar testes de endpoint contra API real no ar
# Uso: ./run_tests.sh [opção]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Diretório de testes
TEST_DIR="tests/endpoint"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         TESTES DE ENDPOINT - AGENDAMENTO MÉDICO          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Função para verificar dependências
check_dependencies() {
    echo -e "${YELLOW}📦 Verificando dependências...${NC}"
    
    if ! command -v pytest &> /dev/null; then
        echo -e "${RED}❌ pytest não encontrado${NC}"
        echo "   Instale com: pip install pytest pytest-asyncio httpx"
        exit 1
    fi
    
    if ! command -v python &> /dev/null; then
        echo -e "${RED}❌ python não encontrado${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Dependências OK${NC}"
    echo ""
}

# Função para verificar se services estão rodando
check_services() {
    echo -e "${YELLOW}🏥 Verificando services...${NC}"
    
    services=(
        "http://localhost:8000:agendaService"
        "http://localhost:8001:analyticService"
        "http://localhost:8002:authService"
        "http://localhost:8003:notificationService"
        "http://localhost:8004:usersService"
    )
    
    all_up=true
    for service in "${services[@]}"; do
        url="${service%:*}"
        name="${service#*:}"
        
        if curl -s "$url/health" > /dev/null 2>&1 || \
           curl -s "$url/api/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $name${NC}"
        else
            echo -e "${RED}❌ $name (não respondeu)${NC}"
            all_up=false
        fi
    done
    
    if [ "$all_up" = false ]; then
        echo ""
        echo -e "${YELLOW}⚠️  Alguns services não estão respondendo${NC}"
        echo "   Execute: docker compose up -d --build"
        read -p "   Continuar mesmo assim? (s/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            exit 1
        fi
    fi
    
    echo ""
}

# Função para executar testes
run_tests() {
    local option=$1
    
    case $option in
        "all")
            echo -e "${BLUE}▶ Executando TODOS OS TESTES${NC}"
            pytest "$TEST_DIR" -v
            ;;
        "flow")
            echo -e "${BLUE}▶ Executando FLUXOS E2E${NC}"
            pytest "$TEST_DIR" -v -m flow -s
            ;;
        "health")
            echo -e "${BLUE}▶ Executando HEALTH CHECKS${NC}"
            pytest "$TEST_DIR" -v -m health -s
            ;;
        "integration")
            echo -e "${BLUE}▶ Executando TESTES DE INTEGRAÇÃO${NC}"
            pytest "$TEST_DIR" -v -m integration -s
            ;;
        "agenda")
            echo -e "${BLUE}▶ Executando TESTES DO AGENDA SERVICE${NC}"
            pytest "$TEST_DIR" -v -m agenda
            ;;
        "users")
            echo -e "${BLUE}▶ Executando TESTES DO USERS SERVICE${NC}"
            pytest "$TEST_DIR" -v -m users
            ;;
        "auth")
            echo -e "${BLUE}▶ Executando TESTES DO AUTH SERVICE${NC}"
            pytest "$TEST_DIR" -v -m auth
            ;;
        "notification")
            echo -e "${BLUE}▶ Executando TESTES DO NOTIFICATION SERVICE${NC}"
            pytest "$TEST_DIR" -v -m notification
            ;;
        "analytic")
            echo -e "${BLUE}▶ Executando TESTES DO ANALYTIC SERVICE${NC}"
            pytest "$TEST_DIR" -v -m analytic
            ;;
        "verbose")
            echo -e "${BLUE}▶ Executando COM SAÍDA DETALHADA${NC}"
            pytest "$TEST_DIR" -vv -s
            ;;
        "quick")
            echo -e "${BLUE}▶ Executando QUICK (apenas health + um fluxo)${NC}"
            pytest "$TEST_DIR" -v -m "health or flow" -k "health_check or setup" --maxfail=1
            ;;
        "help")
            show_help
            ;;
        *)
            echo -e "${YELLOW}Opção não reconhecida: $option${NC}"
            show_help
            exit 1
            ;;
    esac
}

# Função para mostrar ajuda
show_help() {
    echo -e "${BLUE}Opções disponíveis:${NC}"
    echo ""
    echo -e "  ${GREEN}all${NC}           Todos os testes (padrão)"
    echo -e "  ${GREEN}flow${NC}          Fluxos E2E completos ✨"
    echo -e "  ${GREEN}health${NC}        Health checks"
    echo -e "  ${GREEN}integration${NC}   Testes de integração"
    echo -e "  ${GREEN}agenda${NC}        Apenas agendaService"
    echo -e "  ${GREEN}users${NC}         Apenas usersService"
    echo -e "  ${GREEN}auth${NC}          Apenas auth service"
    echo -e "  ${GREEN}notification${NC}  Apenas notificationService"
    echo -e "  ${GREEN}analytic${NC}      Apenas analyticService"
    echo -e "  ${GREEN}verbose${NC}       Com saída detalhada (vv -s)"
    echo -e "  ${GREEN}quick${NC}         Quick test (health + 1 fluxo)"
    echo -e "  ${GREEN}help${NC}          Esta mensagem"
    echo ""
    echo -e "Uso: ./run_tests.sh [opção]"
    echo ""
    echo -e "Exemplos:"
    echo -e "  ${YELLOW}./run_tests.sh${NC}             # Executa todos"
    echo -e "  ${YELLOW}./run_tests.sh flow${NC}        # Apenas fluxos E2E"
    echo -e "  ${YELLOW}./run_tests.sh health${NC}      # Health checks"
    echo -e "  ${YELLOW}./run_tests.sh verbose${NC}     # Com logs detalhados"
}

# Função para validar resultado
validate_result() {
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║                  ✅ TESTES PASSARAM                        ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
        exit 0
    else
        echo ""
        echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║                  ❌ ALGUNS TESTES FALHARAM                 ║${NC}"
        echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
        exit 1
    fi
}

# Main
main() {
    check_dependencies
    check_services
    
    option=${1:-all}
    run_tests "$option"
    validate_result
}

# Executar main
main "$@"
