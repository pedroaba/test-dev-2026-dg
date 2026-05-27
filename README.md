# Test DG 2026 - Calculadora de Economia de Energia

Projeto técnico desenvolvido em **Python**, **Django** e **Django REST Framework** para uma empresa de assinatura de energia, contemplando a calculadora de economia no site, a gestão de consumidores e os endpoints de API para integração (regras de desconto, regras de cobertura, atualização e exclusão de consumidores), com documentação via Swagger.

## Visão geral

O projeto implementa uma calculadora de economia para uma empresa de assinatura de energia e evolui para um sistema com:

- simulação de economia por consumo e tarifa;
- cadastro e edição de consumidores;
- validação de documento (CPF/CNPJ), sem vínculo com o tipo de consumidor;
- vinculação automática de regra de desconto;
- listagem com filtros por tipo e faixa de consumo;
- importação em lote via arquivo Excel;
- endpoints REST para suporte ao front-end e integrações.

## Funcionalidades

### 1) Calculadora de economia

Recebe:

- consumo dos últimos 3 meses;
- tarifa da distribuidora;
- tipo de tarifa/consumidor (`Residencial`, `Comercial`, `Industrial`).

Retorna:

- economia mensal;
- economia anual;
- desconto aplicado;
- cobertura.

### 2) Gestão de consumidores

- cadastro de novo consumidor por formulário;
- edição e exclusão de consumidor;
- listagem em tabela com dados e economia calculada;
- filtros por tipo de consumidor e faixa de consumo.

### 3) Importação de consumidores por Excel

- upload de planilha `.xlsx`/`.xls`;
- validação de colunas obrigatórias e dados por linha;
- criação/atualização de consumidores com base no documento;
- exibição de mensagens de erro amigáveis na interface quando houver dados inválidos.

### 4) API e documentação

- API REST com Django REST Framework;
- documentação OpenAPI via `drf-spectacular` (Swagger/ReDoc).

## Stack e versões

- **Python**: `3.10.20`
- **Django**: `4.0.3`
- **Django REST Framework**: `3.14.0`
- **drf-spectacular**: `0.29.0`
- **Banco de dados**: SQLite (desenvolvimento local)
- **Importação de planilha**: pandas + openpyxl

## Como executar o projeto

### 1) Pré-requisitos

- Python `3.10.20` instalado;
- `pip` disponível no ambiente.

### 2) Clonar e acessar o projeto

```bash
git clone <url-do-repositorio>
cd test-dev-2026-dg
```

### 3) Criar e ativar ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4) Instalar dependências

```bash
pip install -r requirements.txt
```

### 5) Aplicar migrações

```bash
python manage.py migrate
```

### 6) Iniciar servidor

```bash
python manage.py runserver
```

Aplicação web:

- [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Rotas principais

### Web

- `/` - calculadora de economia;
- `/consumers/` - listagem de consumidores;
- `/consumers/create/` - cadastro de consumidor;
- `/consumers/<id>/update/` - edição de consumidor.

### API

- `/api/v1/discount/rules/` - lista regras de desconto;
- `/api/v1/discount/coverages/` - lista coberturas por faixa;
- `/api/v1/consumer/batch-import` - importação de consumidores por Excel;
- `/api/v1/consumer/<id>/` - atualizar/excluir consumidor.

### Documentação da API

- `/api/schema/` - schema OpenAPI;
- `/api/docs/` - Swagger UI;
- `/api/redoc/` - ReDoc.

## Observações

- O projeto está configurado para ambiente de desenvolvimento (`DEBUG=True`).
- O banco SQLite é criado localmente no arquivo `db.sqlite3`.
- Arquivos estáticos são servidos a partir da pasta `static/`.
