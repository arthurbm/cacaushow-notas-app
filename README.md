# API de Processamento de PDFs

API baseada em Flask para extrair e processar dados de arquivos PDF, com implantação na Vercel usando Funções de Borda (Edge Functions).

## Funcionalidades

- Upload de múltiplos arquivos PDF.
- Extração e processamento de dados dos PDFs.
- Interface web para visualização dos dados processados.

## Como Rodar Localmente

### Pré-requisitos

- Python 3.8+
- Pipenv

### Instalação

```bash
pipenv install
pipenv shell
flask run
```

Acesse http://127.0.0.1:5000 no navegador.

## Implantação na Vercel

1. Faça fork do repositório.
2. Crie um novo projeto na Vercel e vincule ao repositório.
3. A Vercel irá detectar e implantar automaticamente.

## Contribuindo

Contribuições são bem-vindas! Para contribuir, faça um fork do projeto, crie uma branch para sua funcionalidade, faça commit das suas alterações, faça push para a branch e abra um pull request.

