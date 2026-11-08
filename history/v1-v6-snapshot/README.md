# Carbon Footprint Lab — Módulo Pessoal (V1–V6)

Protótipo local em Python para registrar atividades pessoais, calcular emissões estimadas e visualizar gráficos.

**AVISO:** Os fatores de emissão fornecidos são **hipotéticos e exclusivamente didáticos**. Não são fatores oficiais do Brasil. Os resultados **não** constituem inventário de emissões certificado nem pegada pessoal completa.

## Iniciar no Windows / PyCharm

1. Abra a pasta `carbon_footprint_lab` no PyCharm.
2. Crie um ambiente virtual Python 3.10+ (se necessário).
3. No terminal da pasta raiz:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

4. Abra a URL local exibida no terminal (geralmente `http://localhost:8501`).

## Testes

```bash
python -m unittest discover -s tests -v
```

## Versões integradas

- **V1:** `personal/calculator.py` — cálculo decimal e validação de valores.
- **V2:** `personal/factors.py` — categorias, unidades e fatores de demonstração.
- **V3:** `personal/database.py` — registro com data, categoria, quantidade e observações.
- **V4:** `personal/database.py` — persistência SQLite e snapshots dos fatores.
- **V5:** `app.py` — Streamlit, indicadores, gráficos e filtros.
- **V6:** `app.py`, `tests/` — exportação CSV, testes e exclusão de registros.

## Dados e metodologia

Cada registro armazena atividade, unidade, fator, fonte, ano (quando disponível), emissões e data. Os cálculos são `quantidade × fator`. O sistema não mistura unidades entre categorias e mantém um snapshot do fator utilizado no momento do registro.

O arquivo `carbon_personal.sqlite3` é criado automaticamente na primeira execução. Para backup, copie esse arquivo com o aplicativo fechado.

**Atenção à dupla contagem:** não registre combustível e quilometragem do mesmo percurso como duas fontes separadas. O dashboard mostra apenas as atividades cadastradas, não uma pegada completa. Se a eletricidade é compartilhada por uma residência, será necessário definir critérios de alocação antes de atribuí-la a uma pessoa.

## Próximos passos para uso real

1. Obter fatores oficiais aplicáveis ao Brasil, com fonte, ano, região, unidade e limites de contabilização.
2. Adicionar versões e validade de fatores, bem como critérios de alocação pessoal.
3. Expandir categorias e documentar exclusões e incertezas.
4. Validar inventários de teste contra calculadoras e metodologias reconhecidas.

Referências metodológicas: https://ghgprotocolbrasil.com.br/ ; https://www.gov.br/mcti/pt-br ; https://www.ipcc.ch/
