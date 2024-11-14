#!/bin/bash

# Defina o nome do seu container
CONTAINER_NAME="evolution_api"

# Função para reiniciar o container
restart_container() {
    # Verifica se o container existe e está rodando
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Reiniciando container ${CONTAINER_NAME}"
        
        # Tenta parar o container gracefully
        docker stop ${CONTAINER_NAME}
        
        # Aguarda alguns segundos
        sleep 5
        
        # Inicia o container
        docker start ${CONTAINER_NAME}
        
        # Verifica se o container está rodando
        if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Container reiniciado com sucesso"
        else
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERRO: Falha ao reiniciar o container"
        fi
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERRO: Container ${CONTAINER_NAME} não encontrado"
    fi
}

# Executa a função
restart_container >> /home/bot/glpi/restart_evolution.log 2>&1
