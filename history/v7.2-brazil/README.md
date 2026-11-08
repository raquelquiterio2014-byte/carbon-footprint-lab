# Carbon Footprint Lab — V1–V7 ampliada

Execute `python -m pip install -r requirements.txt` e `python -m streamlit run app.py`. Testes: `python -m unittest discover -s tests -v`.

## V7 — Brasil
- SIN: 2023 = 0.0385; 2024 = 0.058 (arredondado); 2025 = 0.0461 kg CO₂/kWh (MCTI, valor reproduzido por fonte secundária).
- SIN 2026: **não há fator anual completo antes do fim de 2026**. Planilha mensal de 2026 publicada pelo MCTI; importação e validação dos meses ainda pendentes. Sistema bloqueia eletricidade 2026 no modo documentado para não inventar média anual.
- Misturas ANP: gasolina comum E27 até 31/07/2025, E30 desde 01/08/2025; premium E25; diesel B14 até 31/07/2025, B15 desde 01/08/2025. Aplicação limitada a 2024–2026.
- Fatores componentes de CO₂ por litro: gasolina pura 2.212; diesel puro 2.603, conforme inventário público que cita ferramenta GHG Protocol v2025.0.1. Fator de CO₂ fóssil por litro da mistura = (1 - fração de biocombustível) × fator do combustível fóssil. **É cálculo derivado de fontes públicas, não fator oficial publicado para a mistura**.
- CO₂ biogênico do etanol/biodiesel é excluído do total fóssil; CH₄, N₂O e emissões a montante não são contabilizados. Não chamar o resultado de CO₂e completo.
- Categorias antigas `Gasolina`, `Ônibus`, `Automóvel (distância)` continuam didáticas e assim identificadas; evite duplicidade de trajetos. Registros antigos mantêm os fatores históricos.

## Fontes
- MCTI: https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/dados-e-ferramentas/fatores-de-emissao
- ANP: https://www.gov.br/anp/pt-br/assuntos/distribuicao-e-revenda/revendedor/informacoes-uteis
- Fatores componentes citados de GHG Protocol 2025: https://apmp.tjal.jus.br/ApmpArquivos/Inventario2024_2.pdf
- Conferência secundária do SIN 2025: https://scrutiniums.com/setor-eletrico/aprenda/fator-de-emissao

**Limitação:** não substitui inventário verificado ou avaliação de ciclo de vida.

## V7.2 — MCTI 2026 e combustíveis (2026-11-08)

**Limitação de fonte:** a planilha XLSX do MCTI 2026 foi localizada no portal oficial, mas o arquivo não pôde ser obtido e conferido automaticamente neste ambiente (o portal apresentou bloqueio de acesso). **Nenhum fator mensal de 2026 foi inventado ou pré-carregado.** Para importar, baixe `Inventários Corporativos - 2026` da página oficial: https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/dados-e-ferramentas/fatores-de-emissao. Transcreva/valide os meses existentes para CSV com cabeçalho `year,month,factor_tco2_mwh` e valores como `2026,1,0.0123` (exemplo fictício, NÃO usar como dado). No dashboard envie o XLSX original para calcular seu SHA-256 e o CSV conferido. A importação registra a proveniência, mas **não verifica automaticamente se o CSV corresponde às células do XLSX**. A qualidade fica marcada `transcrito_do_arquivo_oficial_a_conferir`.

Combustíveis: CO₂ fóssil por fração de gasolina/diesel; CH₄ e N₂O por fatores padrão IPCC 2006, Volume 2, capítulo 3, tabela 3.2.2, usando gasolina veículo pós-1995 e diesel veículo pesado; conversão energia/litro com poderes caloríficos **aproximados**, não medidos. GWP AR5 de 100 anos CH₄=28, N₂O=265. CO₂ biogênico é **estimativa estequiométrica aproximada** e aparece separado. Não inclui upstream, mudança de uso do solo, emissões evaporativas ou especificidades do veículo. Não é um fator oficial final do combustível comercial. Para etanol/biodiesel, fatores não-CO₂ foram aproximados usando a mesma categoria tecnológica; isso adiciona incerteza.

Registros anteriores permanecem no SQLite sem recálculo retroativo. Os gráficos de todas as categorias são **indicadores parciais mistos**, não inventário total. A importação do MCTI exige revisão manual da transcrição.
