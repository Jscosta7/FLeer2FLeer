const express = require('express');
const router = express.Router();
const path = require('path');
const Server = require('../models/Server'); // Usa Model centralizado

router.get('/download/:id/:filename', async (req, res) => {
  const { id, filename } = req.params;
  const io = req.app.get("io");

  try {
    // 1. Busca o servidor
    const serverItem = await Server.findById(id);
    if (!serverItem) return res.status(404).send("Servidor não encontrado.");

    // 2. Verifica se o arquivo existe na lista
    const clientFile = serverItem.Client_archive.find(file => file.filename === filename);
    if (!clientFile) return res.status(404).send("Arquivo não encontrado.");

    // 3. Atualiza o contador de downloads 
    const updatedServer = await Server.findByIdAndUpdate(
        id,
        { $inc: { Downloads: 1 } },
        { new: true } // Retorna o documento já atualizado
    );

    // 4. Caminho do arquivo
    const filePath = path.join(__dirname, '..', clientFile.path); 

    // 5. Envia o arquivo
    res.download(filePath, (err) => {
        if (err) {
            console.error("Erro ao enviar arquivo:", err);
            return;
        }

        if (io) {
            // Monta o payload manualmente no mesmo padrão do formatPayload
            const payload = {
                id: updatedServer._id,
                Sever_status: updatedServer.Sever_status,
                Last_Update: updatedServer.Last_Update,
                Completed_Rounds: updatedServer.Completed_Rounds,
                Downloads: updatedServer.Downloads, 
                Average_round_duration: updatedServer.Average_round_duration,
                
                // Dados de treino (só para manter compatibilidade, não mudaram no download)
                Training_status: updatedServer.Training_Parameters?.Training_status,
                Total_Rounds: updatedServer.Training_Parameters?.Total_Rounds,
                Current_Round: updatedServer.Training_Parameters?.Current_Round
            };

            // Emite o MESMO evento que o socketHandler usa
            io.emit("statusUpdate", payload);
            
            console.log(`[Download] Arquivo baixado. Novos downloads: ${updatedServer.Downloads}`);
        }
    });

  } catch (error) {
    console.error("Erro na rota de download:", error);
    res.status(500).send("Erro interno.");
  }
});

module.exports = router;