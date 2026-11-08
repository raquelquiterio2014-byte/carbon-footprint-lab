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

## V7 — Fatores brasileiros documentados (2023–2024)

A V7 preserva V1–V6 e adiciona fatores médios anuais do SIN para eletricidade:

- **2023: 0,0385 kg CO₂/kWh**, divulgado diretamente pelo MCTI/SIRENE.
- **2024: 0,058 kg CO₂/kWh**, média anual arredondada do MCTI reproduzida no inventário CETESB 2024 (Tabela 7).

Fontes:
- https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/noticias/2024/02/fator-de-emissao-de-co2-na-geracao-de-energia-eletrica-no-brasil-em-2023-e-o-menor-em-12-anos
- https://cetesb.sp.gov.br/wp-content/uploads/2025/08/INVENTARIO-GEE-CETESB-2024-v7.pdf
- Catálogo oficial MCTI (para importar e validar anos adicionais): https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/dados-e-ferramentas/fatores-de-emissao

**Regras de integridade:** fator escolhido pelo ano da atividade; anos não validados bloqueados no modo oficial; modo didático opcional e identificado; registro guarda fonte, ano, URL, classificação e gás (CO₂ ou CO₂e). Banco existente é migrado sem excluir registros. Categorias gasolina, ônibus e carro permanecem DIDÁTICAS: não representam fatores oficiais. A soma de categorias com bases metodológicas diferentes é apenas indicativa. Não há cálculo de emissões de ciclo de vida, nem garantia de pegada pessoal completa.

Para utilizar fatores de 2025/2026, é necessário validar os valores e metodologia das planilhas oficiais do MCTI e acrescentá-los explicitamente ao catálogo. Não se deve reutilizar automaticamente o fator de um ano anterior.
