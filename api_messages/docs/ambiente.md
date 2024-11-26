# Ambiente

Foi criada uma estrutura de pasta no servidor do X3 onde deverão ser colocados os ficheiros
a serem processados.

Os ficheiros deverão ser separados por ; (ponto-e-vírgula) e possuir a extensão CSV.

## Dossier X3

{{ folders.dossier }}

Os ficheiros serão depositados no dossier _{{ folders.dossier }}_, que está no caminho `D:\Sage\SAGEX3V12\Folders\{{ folders.dossier }}`

As pastas utilizadas para a integração serão:

```
D:\Sage\SAGEX3V12\Folders\{{ folders.dossier }}
+---HAVAS
|   +---ANEXOS
|   |   +---202407
|   |   |   +---0000001400
|   |   |   |       DocumentoTeste1.pdf
|   |   |   |       DocumentoTeste3.pdf
|   |   |   |
|   |   +---202410
|   |   |   +---1000006601
|   |   |   |       z.txt
|   |   |   |
|   |   +---202411
|   |       +---1000001400
|   |               DocumentoTeste1.pdf
|   |               DocumentoTeste3.pdf
|   |
|   +---ARCHIVE
|       +---INVOICES
|       |   +---202410
|       |   |       ZFH1000006601.csv
|       |   |
|       |   +---202411
|       |           ZFH0000039301.CSV
|       |           ZFH0000039302.CSV
|       |
|       +---PDF
|       |   +---202411
|       |           FT-0142300037.pdf
|       |           FT-0142300038.pdf
|       |           NC-0132300004.pdf
|       |           NC-0142300005.pdf
|       |
|       +---XML
|           +---202411
|                   FT-0132400003.xml
|                   FT-0132400008.xml
|                   FT-0132400011.xml
```

### Pasta ANEXOS

Nesta pasta deverão ser colocados os ficheiros que irão seguir como anexos da fatura.

Sob a pasta **ANEXOS** deverão existir sub-pastas referenciadas com o Ano/mes no formato **AAAAMM**.

### Pasta ARCHIVE

Esta é a pasta final do processo:

- **_INVOICES_**: nesta pasta serão armazenados os ficheiros de faturas já processados
- **_PDF_**: nesta pasta serão armazenados os pdfs gerados das faturas
- **_XML_**: nesta pasta serão armazenados os xmls gerados das faturas enviadas à Saphety
