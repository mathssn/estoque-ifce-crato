CREATE TABLE IF NOT EXISTS usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo ENUM('Admin', 'Editor', 'Leitor') NOT NULL,
    email VARCHAR(100) NOT NULL,
    senha VARCHAR(20) NOT NULL,
    data_nascimento DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS produto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo INT NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(100),
    unidade VARCHAR(10) NOT NULL,
    quantidade_minima INT NOT NULL,
    status ENUM('Disponivel', 'Não disponivel') NOT NULL
);

CREATE TABLE IF NOT EXISTS saidas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT NOT NULL,
    destino ENUM('Café da manhã', 'Lanche da manhã', 'Almoço', 'Lanche da tarde', 'Jantar', 'Ceia', 'Outros') NOT NULL,
    data_saida DATE NOT NULL,
    quantidade INT NOT NULL,
    observacao TEXT,
    usuario_id INT NOT NULL,
    FOREIGN KEY(produto_id) REFERENCES produto(id) ON DELETE CASCADE,
    FOREIGN KEY(usuario_id) REFERENCES usuario(id)
);

CREATE TABLE IF NOT EXISTS entradas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT NOT NULL,
    data_entrada DATE NOT NULL,
    quantidade INT NOT NULL,
    observacao TEXT,
    usuario_id INT NOT NULL,
    FOREIGN KEY(produto_id) REFERENCES produto(id) ON DELETE CASCADE,
    FOREIGN KEY(usuario_id) REFERENCES usuario(id)
);

CREATE TABLE IF NOT EXISTS saldo_diario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT NOT NULL,
    data DATE NOT NULL,
    quantidade_inicial INT NOT NULL,
    quantidade_entrada INT NOT NULL,
    quantidade_saida INT NOT NULL,
    quantidade_final INT NOT NULL
);

CREATE TABLE IF NOT EXISTS dias_fechados (
    data DATE PRIMARY KEY,
    fechado TINYINT(1) NOT NULL
);
