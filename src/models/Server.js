// models/Server.js
const mongoose = require('mongoose');

// Sub-schema para arquivos (usado dentro do array Client_archive)
const FileSchema = new mongoose.Schema({
    filename: String,
    path: String,
    mimetype: String
}, { _id: false });

// Sub-schema para parâmetros de treino (organização)
const TrainingParamsSchema = new mongoose.Schema({
  Training_status: { type: String, default: 'N/A' },
  Total_Rounds: { type: Number, default: 0 },
  Current_Round: { type: Number, default: 0 },
  Minimun_clients: { type: Number, default: 0 },
  fraction_fit: { type: Number, default: 0 },
  Connected_client: { type: Number, default: 0 }
}, { _id: false });

const ServerSchema = new mongoose.Schema({
  Sever_status: { 
    type: String, 
    required: true, 
    default: 'offline',
    enum: ['online', 'offline'] 
  },
  Category: String,
  Application: String,
  

  tags: [String], 
  // ---------------------

  Last_Update: { type: Date, default: Date.now },
  Completed_Rounds: { type: Number, default: 0 },  
  Average_round_duration: { type: Number, default: 0 },
  Downloads: { type: Number, default: 0 },
  
  Client_archive: [FileSchema], 
  
  Training_Parameters: { type: TrainingParamsSchema, default: () => ({}) }
});

// --- LÓGICA DE NEGÓCIO ---
ServerSchema.statics.checkInactivity = async function(timeoutSeconds = 300) {
    const now = new Date();
    const onlineServers = await this.find({ Sever_status: 'online' });
    const offlineServers = [];

    for (const server of onlineServers) {
        const lastUpdate = new Date(server.Last_Update);
        const diffSeconds = (now - lastUpdate) / 1000;
        
        let threshold = timeoutSeconds;
        const avgDuration = server.Average_round_duration;
        
        if (avgDuration && avgDuration > 0) {
            threshold = 10 * avgDuration;
        }

        if (diffSeconds > threshold) {
            server.Sever_status = 'offline';
            await server.save();
            offlineServers.push(server);
        }
    }
    
    return offlineServers;
};

module.exports = mongoose.model('Server', ServerSchema, 'servers');