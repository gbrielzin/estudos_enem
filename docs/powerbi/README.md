# Painel do ENEM GI no Power BI

![Painel do ENEM GI no Power BI](painel.png)

Painel de desempenho de estudo lido direto das views do Snowflake
(`../snowflake/`). O projeto está salvo no formato **PBIP**, ou seja, em texto
(JSON e TMDL), e não como um `.pbix` binário. Por isso cada mudança no painel
aparece no diff do PR, como qualquer código.

| Arquivo | O que faz |
|---|---|
| `03_views_powerbi.sql` | camada semântica no warehouse: `VW_DIM_QUESTAO` (área legível, faixa TRI e o marcador antigo `sem_video_pendente` trocado por `(não classificada)`) e `VW_FATO_TENTATIVA` (data, semana e os indicadores 0/1 `ACERTOU` e `EM_BRANCO`) |
| `04_usuario_powerbi.sql` | papel `LEITOR_ENEM` e usuário `POWERBI_LEITOR` só com `USAGE` e `SELECT` (privilégio mínimo). A senha não fica no arquivo |
| `painel/enem_gi.pbip` | projeto do Power BI Desktop: modelo estrela (fato → dimensão), medidas DAX e o relatório |

A regra de negócio, como a faixa TRI e o "acertou", fica **na view**, e não em
cada painel. Assim, quem ler o warehouse (Power BI, Tableau ou uma consulta
SQL) vê o mesmo número.

## O que os dados mostraram

1. **A média de 57,6% está inflada.** As questões sem TRI têm 75,8% de acerto,
   e 170 das 182 vêm do banco de prática, que é mais fácil. Nas questões
   oficiais com TRI, o acerto é 53,9%.
2. **O desempenho acompanha a TRI.** O acerto cai conforme a dificuldade
   oficial sobe: 68,2% nas fáceis, 52,5% nas médias e 46,0% nas difíceis.
3. **Sobrou dado de uma funcionalidade descontinuada.** 451 questões oficiais
   (446 delas de Natureza) têm `sem_video_pendente` no lugar da matéria,
   resto da ideia de classificar pelo vídeo do YouTube ([ADR 0008](../../adr/0008-descontinuar-vinculo-youtube.md)). A view
   trata o caso; o próximo passo é classificar essas questões.
4. **Prioridade de estudo:** funções orgânicas (16,7%), física (37,8%) e função
   do 2º grau (40,0%), entre as matérias com 10 ou mais tentativas.

## Como abrir

1. Rode `../snowflake/01_criar_e_carregar.sql`, depois `03_views_powerbi.sql`
   e `04_usuario_powerbi.sql`, no Snowsight.
2. Nos dois arquivos `painel/enem_gi.SemanticModel/definition/tables/VW_*.tmdl`,
   troque `SUA_ORG-SUA_CONTA` pelo identificador da sua conta Snowflake. O
   endereço da conta original não é publicado.
3. Abra `painel/enem_gi.pbip` no Power BI Desktop e entre com o usuário
   `POWERBI_LEITOR`. O Power BI guarda a credencial localmente, fora do projeto.

O `.gitignore` da pasta `painel/` exclui `localSettings.json` e `cache.abf`
(cache dos dados importados), que são arquivos da máquina e não do projeto.
