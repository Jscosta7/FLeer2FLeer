// services/monitorService.js
const ServerModel = require('../models/Server');

/**
 * Inicia o ciclo de monitoramento de servidores inativos.
 * @param {Server} io - Instância do Socket.io para enviar alertas ao frontend.
 */
function startMonitoring(io) {
    console.log('[Monitor] Serviço de verificação de inatividade iniciado.');

    // Executa a verificação a cada 5 minutos (300.000 ms)
    setInterval(async () => {
        try {

            // O argumento '3000' é o timeout padrão em segundos (50 min)
            const offlineServers = await ServerModel.checkInactivity(3000);

            if (offlineServers.length > 0) {
                console.log(`[Monitor] ${offlineServers.length} servidores marcados como offline.`);
                
                // Avisa o frontend imediatamente sobre cada servidor que caiu
                // Isso atualiza a bolinha de "Online" para "Offline" na tela do usuário
                offlineServers.forEach(server => {
                    io.emit('statusUpdate', server);
                });
            }
        } catch (error) {
            console.error('[Monitor] Erro crítico ao verificar servidores:', error);
        }
    }, 300000); 
}

module.exports = startMonitoring;