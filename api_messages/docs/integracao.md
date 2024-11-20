# Integração

<p class="docX3">A integração acontecerá de forma automática através da execução das tarefas batch do X3.</p>

<p class="docX3">Para garantir que a execução das funções aconteça de forma ordenada, foram criadas 8 assinaturas de execução. Cada
uma delas é executada no intervalo de 30 minutos e chamam o grupo de tarefas ZINTEDI.</p>

<p class="docX3">O grupo ZINTEDI é formado pelas tarefas:</p>

1. FUNZEDI - verifica e carrega os ficheiros para o X3 e cria as faturas
2. FUNCFMINV - faz a validação das faturas
3. FUNZSAPH - busca pelas faturas existentes na tabela staging e que estejam com o status
   **6 - Enviar à Saphety**

## Estrutura do ficheiro

<p class="docX3">
Em cada ficheiro poderá haver somente uma fatura e deverá estar separado por <strong>;</strong> (ponto-e-vírgula),
 os valores decimais devem ser identificados por <strong>,</strong> (vírgula).
</p>

### Indicadores

O ficheiro deve possuir 3 blocos, sendo 2 deles obrigatórios e 1 opcional.

Os blocos obrigatórios são o de cabeçalho, identificado pela letra **A** e o de linhas, identificado pela letra **L**.

O bloco opcional refere-se aos elementos de faturação e caso existam deverão ser identificados pela letra **R**.

### Estrutura

<div class="annotate" markdown>

| Indicador | Campo       | Descrição                  | Tam máximo | Valores esperados                                                                                                                         |
| :-------: | ----------- | -------------------------- | :--------: | ----------------------------------------------------------------------------------------------------------------------------------------- |
|    `A`    | CPY         | Sociedade                  |     5      |                                                                                                                                           |
|    `A`    | SIVTYP      | Tipo fatura venda          |     5      | <ul><li>FT - Faturas</li><li>NC - Notas de crédito</li></ul>                                                                              |
|    `A`    | ZNUM        | Nr. fatura                 |     30     |                                                                                                                                           |
|    `A`    | BPCNAM1     | Razão social               |     30     |                                                                                                                                           |
|    `A`    | BPCNAM2     | Razão social               |     30     |                                                                                                                                           |
|    `A`    | ACCDAT      | Data da fatura             |     8      | DDMMAAAA                                                                                                                                  |
|    `A`    | DUDDAT      | Data vencimento            |     8      | DDMMAAAA                                                                                                                                  |
|    `A`    | INVREF      | Referência interna         |     50     |                                                                                                                                           |
|    `A`    | CUR         | Divisa                     |     3      |                                                                                                                                           |
|    `A`    | VACBPR      | Regime terceiro            |     3      | <ul><li>CON - Continente</li><li>UE - União Europeia</li><li>EXP - Exportação</li><li>IS1 - Isento</li></ul>                              |
|    `A`    | ZEECNUM     | Nº Contribuinte            |     20     |                                                                                                                                           |
|    `A`    | ZADIREF     | Referência cliente         |    250     |                                                                                                                                           |
|    `A`    | ZCOMMENT1   | Comentário                 |     50     |                                                                                                                                           |
|    `A`    | ZCOMMENT2   | Comentário                 |     50     |                                                                                                                                           |
|    `A`    | ZCOMMENT3   | Comentário                 |     50     |                                                                                                                                           |
|    `A`    | BPADD1      | Endereço 1                 |     30     |                                                                                                                                           |
|    `A`    | BPADD2      | Endereço 2                 |     30     |                                                                                                                                           |
|    `A`    | BPADD3      | Endereço 3                 |     30     |                                                                                                                                           |
|    `A`    | CITY        | Cidade                     |     20     |                                                                                                                                           |
|    `A`    | CRY         | País                       |     2      |                                                                                                                                           |
|    `A`    | ZPOSCOD     | Código postal              |     7      | NNNNNNN (sem hífen)                                                                                                                       |
|    `A`    | ZTEL        | Telefone                   |     20     |                                                                                                                                           |
|    `A`    | ZEMAIL      | Email                      |    200     |                                                                                                                                           |
|    `A`    | ZGLN        | GLN do cliente             |     50     |                                                                                                                                           |
|    `A`    | ZNUMFT      | Nr. fatura original        |     30     |                                                                                                                                           |
|    `A`    | ZCNOREN     | Motivo NC                  |     10     |                                                                                                                                           |
|    `A`    | ZFLD40REN   | Motivo Campo 40            |     10     |                                                                                                                                           |
|    `A`    | ZPERINI     | Período início             |     8      | DDMMAAAA                                                                                                                                  |
|    `A`    | ZPERFIN     | Período fim                |     8      | DDMMAAAA                                                                                                                                  |
|    `A`    | ZSWIFT      | Número SWIFT               |     10     |                                                                                                                                           |
|    `A`    | ZNIB        | NIB                        |     25     |                                                                                                                                           |
|    `A`    | ZBAN        | Nome do banco              |    200     |                                                                                                                                           |
|    `A`    | ZCRYPRINT   | País impressão             |     3      | Se PT/POR imprimir documentos em Português, caso contrário em inglês                                                                      |
|    `A`    | ZSAFTYDES   | Comentário                 |    250     | Saphety                                                                                                                                   |
|    `A`    | ZCOSTCENTER | Ref. Centro custo          |    250     | Saphety                                                                                                                                   |
|    `A`    | ZORDER      | Ref. Ordem                 |    250     | Saphety                                                                                                                                   |
|    `A`    | ZINVOICE    | Ref. Fatura                |    250     | Saphety                                                                                                                                   |
|    `A`    | ZCOMMITMENT | Ref. Commitment            |    250     | Saphety                                                                                                                                   |
|    `A`    | ZSENDMET    | Método de envio            |     1      | <ul><li>1 - EDI Saphety</li><li>2 - PDF Saphety</li><li>3 - Saphety sem envio</li><li>4 - EFAT</li><li>5 - Sem envio eletrônico</li></ul> |
|    `A`    | ZDOCPATH    | Pasta anexos               |    250     |                                                                                                                                           |
|    `L`    | ZNUM        | Nr. fatura                 |     30     |                                                                                                                                           |
|    `L`    | ZLIN        | Nr. linha fatura           |     8      |                                                                                                                                           |
|    `L`    | ITMDES      | Designação                 |     30     |                                                                                                                                           |
|    `L`    | ZADISES     | Descrição completa         |    250     |                                                                                                                                           |
|    `L`    | ZATB        | Código Tipologia Artigo    |     5      |                                                                                                                                           |
|    `L`    | ZATBDES     | Descrição Tipologia Artigo |     50     |                                                                                                                                           |
|    `L`    | VACITM      | Nível de taxa              |     3      |                                                                                                                                           |
|    `L`    | SAL         | Unidade de venda           |     2      | EA (UN)                                                                                                                                   |
|    `L`    | QTY         | Quantidade                 |     15     |                                                                                                                                           |
|    `L`    | GROPRI      | Preço bruto                |    13,2    |                                                                                                                                           |
|    `L`    | RATAXLN     | Percentagem taxa           |    7,4     |                                                                                                                                           |
|    `L`    | DISCRGVAL1  | Desconto                   |    10,4    |                                                                                                                                           |
|    `L`    | ZLINFAT     | Nr. linha fat. origem      |     5      |                                                                                                                                           |
|    `R`    | ZNUM        | Nr. fatura                 |     30     |                                                                                                                                           |
|    `R`    | ZLIN        | Nr. linha fatura           |     8      |                                                                                                                                           |
|    `R`    | DTA         | Elemento faturação         |     20     |                                                                                                                                           |
|    `R`    | DTAAMT      | % ou Mont. de fatura       |    13,2    |                                                                                                                                           |
|    `R`    | ZINC        | Incidência                 |    13,2    |                                                                                                                                           |
|    `R`    | DTANOT      | Mont. s/IVA                |    13,2    |                                                                                                                                           |

</div>
