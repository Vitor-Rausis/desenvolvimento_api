Desafio: Desenvolvimento de uma API com camada de segurança
 
Descrição:
 
Você deve desenvolver uma API em Python utilizando um framework de sua escolha (por exemplo, Flask, Django, FastAPI, etc.) com uma camada de segurança adequada para proteger os endpoints.
 
Requisitos:
 
1. A API deve ter pelo menos dois endpoints principais: `/login` e `/data` (dados).
2. O endpoint `/login` deve autenticar e fornecer um token de autenticação válido.
3. O endpoint `/data` (dados) só pode ser acessado por requisições autenticadas.
4. A API deve ter suporte para criar, ler, atualizar e deletar dados no endpoint `/data`. Os dados podem ser armazenados em memória, em um banco de dados (SQL ou NoSQL) ou em um arquivo, conforme preferência do candidato.
5. Todas as requisições para o endpoint `/data` (dados) devem estar protegidas por autenticação.
6. O token de autenticação deve ser enviado no cabeçalho da requisição.
7. A API deve retornar erros adequados com códigos de status HTTP apropriados e mensagens de erro compreensíveis.
 
Bônus (opcional):
 
- Implementar validação de permissões (por exemplo, apenas usuários autenticados com um tipo de usuário específico podem realizar determinadas ações).
- Implementar encriptação nos dados no armazenamento ou durante a transmissão.
- Implementar controle de taxa limitando o número de requisições de um cliente em um determinado período de tempo.
- Escrever testes unitários para cobrir a funcionalidade principal da API.