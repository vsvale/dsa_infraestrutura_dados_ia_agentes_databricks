-- Criar tabela de departamentos
CREATE OR REPLACE TABLE departamentos (
  id INT PRIMARY KEY,
  departamento STRING
);

-- Inserir dados de departamentos
INSERT INTO departamentos (id, departamento)
VALUES 
  (1, 'Engenharia'),
  (2, 'Marketing'),
  (3, 'Vendas'),
  (4, 'Recursos Humanos'),
  (5, 'Financeiro'),
  (6, 'TI'),
  (7, 'Operações'),
  (8, 'Suporte Técnico'),
  (9, 'Logística'),
  (10, 'Pesquisa & Desenvolvimento');

-- Consultar todos os departamentos
SELECT * FROM departamentos;
