// sockets/socketHandler.js
const ServerModel = require('../models/Server');

/**
 * Helper: Formata o documento do Mongoose para o formato plano esperado pelo Frontend.
 *
 */
function formatPayload(doc) {
    if (!doc) return null;
    return {
        id: doc._id,
        Sever_status: doc.Sever_status,
        Last_Update: doc.Last_Update,
        Completed_Rounds: doc.Completed_Rounds,
        Average_round_duration: doc.Average_round_duration,
        Downloads: doc.Downloads,
        
       
        Training_status: doc.Training_Parameters?.Training_status || 'N/A',
        Total_Rounds: doc.Training_Parameters?.Total_Rounds || 0,
        Current_Round: doc.Training_Parameters?.Current_Round || 0,
        Minimun_clients: doc.Training_Parameters?.Minimun_clients || 0,
        fraction_fit: doc.Training_Parameters?.fraction_fit || 0,
        connected_clients: doc.Training_Parameters?.Connected_client || 0
    };
}

async function handleTrainingUpdate(io, data) {
    try {
        console.log(`[Socket] Training update de ${data.id}`);
        const serverDoc = await ServerModel.findById(data.id);
        if (!serverDoc) return;

        let newAvg = serverDoc.Average_round_duration || 0;
        const oldCompleted = serverDoc.Completed_Rounds || 0;
        let incCompleted = 0;

        if (data.Round_duration && data.Round_duration > 0) {
            newAvg = Math.round(((newAvg * oldCompleted) + data.Round_duration) / (oldCompleted + 1));
            incCompleted = 1;
        }

        const updatedServer = await ServerModel.findByIdAndUpdate(
            data.id,
            {
                $set: {
                    Sever_status: data.Server_status,
                    Last_Update: new Date(data.last_update),
                    Average_round_duration: newAvg,
                    "Training_Parameters.Training_status": data.Training_status,
                    "Training_Parameters.Total_Rounds": data.Total_rounds,
                    "Training_Parameters.Current_Round": data.current_round,
                    "Training_Parameters.Minimun_clients": data.Min_clients,
                    "Training_Parameters.fraction_fit": data.Fraction_fit,
                    "Training_Parameters.Connected_client": data.connected_clients
                },
                $inc: { Completed_Rounds: incCompleted }
            },
            { new: true, upsert: true }
        );

        // Usa o formatador antes de enviar
        io.emit("statusUpdate", formatPayload(updatedServer));

    } catch (err) {
        console.error("[Socket] Erro no training_update:", err);
    }
}

async function handleClientsUpdate(io, { id, clients, Training_status }) {
    try {
        io.emit("clientsUpdate", { id, clients, Training_status });
        await ServerModel.findByIdAndUpdate(id, {
            $set: {
                "Training_Parameters.Connected_client": clients,
                "Training_Parameters.Training_status": Training_status
            }
        });
    } catch (err) {
        console.error("[Socket] Erro no clients_update:", err);
    }
}

module.exports = (io) => {
    io.on('connection', (socket) => {
        // console.log(`[Socket] Cliente conectado: ${socket.id}`);
        socket.emit('statusUpdate', { msg: 'Conectado ao Indexador' });
        socket.on("training_update", (data) => handleTrainingUpdate(io, data));
        socket.on("clients_update", (data) => handleClientsUpdate(io, data));
    });
};