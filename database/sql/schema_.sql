
CREATE TABLE IF NOT EXISTS produto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo INT NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(100),
    unidade VARCHAR(10) NOT NULL,
    quantidade_minima INT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Disponivel', 'Não disponivel'))
);

CREATE TABLE IF NOT EXISTS saidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INT NOT NULL,
    destino TEXT NOT NULL CHECK (destino IN ('Café da manhã', 'Lanche da manhã', 'Almoço', 'Lanche da tarde', 'Jantar', 'Ceia', 'Outros')),
    data_saida DATE NOT NULL,
    quantidade INT NOT NULL,
    observacao TEXT,
    usuario_id INT NOT NULL,
    FOREIGN KEY(produto_id) REFERENCES produto(id) ON DELETE CASCADE
    FOREIGN KEY(usuario_id) REFERENCES usuario(id)
);

CREATE TABLE IF NOT EXISTS entradas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INT NOT NULL,
    data_entrada DATE NOT NULL,
    quantidade INT NOT NULL,
    observacao TEXT,
    usuario_id INT NOT NULL,
    FOREIGN KEY(produto_id) REFERENCES produto(id) ON DELETE CASCADE
    FOREIGN KEY(usuario_id) REFERENCES usuario(id)
);

CREATE TABLE IF NOT EXISTS saldo_diario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INT NOT NULL,
    data DATE NOT NULL,
    quantidade_inicial INT NOT NULL,
    quantidade_entrada INT NOT NULL,
    quantidade_saida INT NOT NULL,
    quantidade_final INT NOT NULL
);

CREATE TABLE IF NOT EXISTS dias_fechados (
    data DATE PRIMARY KEY,
    fechado BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('Admin', 'Editor', 'Leitor')),
    email VARCHAR(100) NOT NULL,
    senha VARCHAR(20) NOT NULL,
    data_nascimento DATE NOT NULL
)