const mongoose = require('mongoose');

const ReportSchema = new mongoose.Schema({
  Subject: { type: String, required: true },
  Type: { 
    type: String, 
    enum: ['Technical Bug', 'Malicious Server', 'Performance Issue', 'Feature Request', 'Other'],
    default: 'Other'
  },
  Target_Server_ID: { type: String }, 
  Priority: { 
    type: String, 
    enum: ['Low', 'Medium', 'High', 'Critical'],
    default: 'Medium'
  },
  Description: { type: String, required: true },
  Status: { type: String, default: 'Pending' }, // Pending, Reviewed, Resolved
  Created_At: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Report', ReportSchema);