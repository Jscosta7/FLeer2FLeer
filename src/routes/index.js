const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const Server = require('../models/Server'); 
const Report = require('../models/Report'); // Importa o novo model

// --- CONFIGURAÇÃO DO MULTER (UPLOAD) ---
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'uploads/'); // Salva na pasta uploads
  },
  filename: function (req, file, cb) {
    // Evita nomes duplicados adicionando timestamp
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, uniqueSuffix + '-' + file.originalname);
  }
});

// Filtro para aceitar apenas arquivos .py 
const fileFilter = (req, file, cb) => {
  if (file.originalname.endsWith('.py')) {
    cb(null, true);
  } else {
    cb(new Error('Apenas arquivos Python (.py) são permitidos!'), false);
  }
};

const upload = multer({ storage: storage, fileFilter: fileFilter });

// --- ROTAS GET (PÁGINAS) ---

/* GET home page. */
router.get('/', async(req, res, next) => {
  try {
    const docs = await Server.find({});
    res.render('index', { results: false, list: docs });
  } catch (err) {
    next(err);
  }
});

/* GET be a server page */
router.get('/be_a_server', (req, res) => {
  res.render('be_a_server');
});

/* GET report page */
router.get('/report', (req, res) => {
  res.render('report');
});

/* GET search page. */
router.get('/search', async (req, res, next) => {
  try {
    const queryStr = req.query.query || '';
    const searchParams = queryStr.toUpperCase().split(' ');
    const docs = await Server.find({ tags: { $all: searchParams } });
    res.render('index', { results: true, search: queryStr, list: docs });
  } catch (err) {
    next(err);
  }
});

/* GET training page */
router.get('/training/:id', async (req, res, next) => {
  try {
    const { id } = req.params;
    const offline = req.query.offline === 'true';
    const serverDoc = await Server.findById(id);

    if (!serverDoc) return res.status(404).send("Servidor não encontrado");

    res.render('training', { server: serverDoc, offline });
  } catch (err) {
    next(err);
  }
});


// --- ROTAS POST (AÇÃO DOS FORMULÁRIOS) ---

/* POST be a server (Recebe o formulário) */
router.post('/be_a_server', upload.single('clientFile'), async (req, res, next) => {
  try {
    const { category, application, hardware, description } = req.body;
    
    // Cria o objeto do novo servidor
    const newServer = new Server({
      Category: category,
      Application: application,
      Sever_status: 'offline', 
      tags: [category.toUpperCase(), application.toUpperCase()], 
      
      Client_archive: []
    });

    // Se houve upload de arquivo, salva os dados dele
    if (req.file) {
      newServer.Client_archive.push({
        filename: req.file.originalname, // Nome original para exibição
        path: 'uploads/' + req.file.filename, // Caminho real salvo
        mimetype: req.file.mimetype
      });
    }

    await newServer.save();
    console.log("Novo servidor cadastrado:", newServer._id);
    
    // Redireciona para a home
    res.redirect('/');
    
  } catch (err) {
    console.error("Erro ao cadastrar servidor:", err);
    res.status(500).send("Erro ao cadastrar servidor: " + err.message);
  }
});

/* POST report (Recebe a denúncia) */
router.post('/report', async (req, res, next) => {
  try {
    const { subject, type, targetId, priority, description } = req.body;

    const newReport = new Report({
      Subject: subject,
      Type: type,
      Target_Server_ID: targetId,
      Priority: priority,
      Description: description
    });

    await newReport.save();
    console.log("Novo report recebido:", newReport._id);

    // Redireciona para home ou mostra mensagem de sucesso
    res.redirect('/');

  } catch (err) {
    console.error("Erro ao salvar report:", err);
    res.status(500).send("Erro ao enviar report.");
  }
});

module.exports = router;