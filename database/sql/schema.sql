
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
    FOREIGN KEY(produto_id) REFERENCES produto(id)
);

CREATE TABLE IF NOT EXISTS entradas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INT NOT NULL,
    data_entrada DATE NOT NULL,
    quantidade INT NOT NULL,
    FOREIGN KEY(produto_id) REFERENCES produto(id)
);
