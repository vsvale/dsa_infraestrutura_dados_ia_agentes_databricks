-- Criar tabela de funcionários
CREATE OR REPLACE TABLE funcionarios (
  id INT PRIMARY KEY,
  nome STRING
);

-- Inserir dados de funcionários
INSERT INTO funcionarios (id, nome)
VALUES 
  (1, 'Bob'),
  (2, 'Ana'),
  (3, 'Flavio'),
  (4, 'Marcelo'),
  (5, 'Tatiana'),
  (6, 'Leandro'),
  (7, 'Tulio'),
  (8, 'Edson'),
  (9, 'Francisco'),
  (10, 'Helio');

-- Consultar todos os funcionários
SELECT * FROM funcionarios;
