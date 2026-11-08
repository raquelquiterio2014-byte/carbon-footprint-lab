"""V5/V6: Streamlit dashboard, filters, exports and validation."""
from datetime import date
from decimal import Decimal
import pandas as pd
import streamlit as st
from personal.calculator import calculate_emissions
from personal.database import connect, initialize, add_activity, list_activities, delete_activity
from personal.factors import FACTORS, ELECTRICITY_FACTORS, resolve_factor
from personal.v72 import import_sin_csv, fuel_components

st.set_page_config(page_title='Carbon Footprint Lab | Pessoal', page_icon='🌿', layout='wide')
st.title('🌿 Carbon Footprint Lab — Pegada Pessoal')
st.warning('V7.2: fatores mensais MCTI 2026 mediante importação verificável; combustíveis com CO₂ fóssil + CH₄/N₂O (estimativa IPCC) e CO₂ biogênico separado. Não é inventário certificado.')
st.caption('V1–V7 integradas | SQLite local | Não confundir CO₂ fóssil, CO₂ da rede e CO₂e total')
conn = connect()
initialize(conn)

with st.sidebar:
    st.header('Registrar atividade')
    with st.form('activity', clear_on_submit=True):
        activity_date = st.date_input('Data', value=date.today())
        category = st.selectbox('Categoria', list(FACTORS))
        official = st.checkbox('Usar fator documentado (quando disponível)', value=True, disabled=category not in ('Eletricidade', 'Gasolina comum (litros)', 'Gasolina premium (litros)', 'Diesel B (litros)'))
        try:
            spec = resolve_factor(category, activity_date, use_official=official)
            st.caption(f"Unidade: {spec['unit']} | Fator: {spec['factor']} {spec['factor_unit']} | {spec['source']}")
            factor_error = None
        except ValueError as exc:
            factor_error = str(exc)
            st.error(factor_error)
            spec = None
        quantity = st.number_input('Quantidade', min_value=0.0, step=1.0, format='%.3f')
        notes = st.text_input('Observações (opcional)', max_chars=200)
        submitted = st.form_submit_button('Salvar atividade', use_container_width=True)
        if submitted:
            if factor_error:
                st.error('Registro não salvo: ' + factor_error)
            else:
                add_activity(conn, activity_date, category, quantity, notes, use_official=official)
                st.success(f"Registrado: {calculate_emissions(quantity, spec['factor']):.3f} kg {spec['gas']}")
    st.info('Evite registrar gasolina e distância do mesmo trajeto simultaneamente: isso duplicaria emissões.')
    with st.expander('Importar fatores mensais MCTI 2026'):
        st.caption('Baixe a planilha Inventários Corporativos — 2026 no site do MCTI. Confira/transcreva os meses em CSV com cabeçalho year,month,factor_tco2_mwh. A importação exige o SHA-256 do XLSX original. Não importamos fatores de margem MDL.')
        official_file = st.file_uploader('Planilha oficial XLSX para calcular SHA-256', type='xlsx')
        month_csv = st.file_uploader('CSV de meses conferidos', type='csv')
        if official_file and month_csv and st.button('Importar meses conferidos'):
            import hashlib, tempfile
            from pathlib import Path
            digest = hashlib.sha256(official_file.getvalue()).hexdigest()
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / 'monthly.csv'
                path.write_bytes(month_csv.getvalue())
                try:
                    result = import_sin_csv(path, digest, official_file.name)
                    st.success(f"Importados {len(result['monthly'])} meses com rastreabilidade. Confirme que os valores foram transcritos corretamente.")
                except Exception as exc:
                    st.error(str(exc))

records = list_activities(conn)
if not records:
    st.info('Nenhuma atividade cadastrada. Use o formulário à esquerda para criar o primeiro registro.')
    st.stop()

df = pd.DataFrame(records)
df['activity_date'] = pd.to_datetime(df['activity_date'])
df['emissions_kg'] = df['emissions_kg'].map(lambda x: float(Decimal(x)))
df['quantity'] = df['quantity'].map(lambda x: float(Decimal(x)))
df['month'] = df['activity_date'].dt.strftime('%Y-%m')

months = sorted(df['month'].unique().tolist(), reverse=True)
selected_months = st.multiselect('Filtrar por mês', months, default=months)
selected_categories = st.multiselect('Filtrar por categoria', list(FACTORS), default=list(FACTORS))
filtered = df[df['month'].isin(selected_months) & df['category'].isin(selected_categories)].copy()

col1, col2, col3 = st.columns(3)
eligible = filtered[filtered['factor_quality'].fillna('').ne('didatico')]
col1.metric('Indicador parcial documentado', f"{eligible['emissions_kg'].sum():,.2f} kg")
col2.metric('Atividades', len(filtered))
col3.metric('Categorias', filtered['category'].nunique())

if not filtered.empty:
    left, right = st.columns(2)
    with left:
        st.subheader('Indicador parcial por categoria (kg; fronteiras diferentes)')
        st.bar_chart(filtered.groupby('category')['emissions_kg'].sum())
    with right:
        st.subheader('Indicador parcial mensal (kg; fronteiras diferentes)')
        st.line_chart(filtered.groupby('month')['emissions_kg'].sum())
    st.subheader('Componentes de combustíveis')
    if 'co2_biogenic_kg' in filtered:
        biogenic = pd.to_numeric(filtered['co2_biogenic_kg'], errors='coerce').fillna(0).sum()
        st.metric('CO₂ biogênico (separado, não somado ao CO₂e)', f'{biogenic:,.3f} kg')
    st.caption('Gráficos abaixo são indicadores parciais mistos e não equivalem à pegada pessoal completa; incluem valores didáticos quando cadastrados.')
    st.subheader('Registros')
    display = filtered[['id', 'activity_date', 'category', 'quantity', 'unit', 'factor', 'factor_source', 'factor_year', 'factor_quality', 'factor_url', 'gas', 'emissions_kg', 'co2_fossil_kg', 'ch4_kg', 'n2o_kg', 'nonco2_co2e_kg', 'co2_biogenic_kg', 'methodology', 'notes']].copy()
    display['activity_date'] = display['activity_date'].dt.strftime('%Y-%m-%d')
    st.dataframe(display, use_container_width=True, hide_index=True)
    csv_bytes = display.to_csv(index=False).encode('utf-8-sig')
    st.download_button('Exportar CSV filtrado', csv_bytes, file_name='carbon_footprint_personal.csv', mime='text/csv')
else:
    st.info('Nenhum registro corresponde aos filtros selecionados.')

with st.expander('Fatores utilizados e limitações'):
    st.dataframe(pd.DataFrame([{'Categoria': k, **v} for k, v in FACTORS.items()]), hide_index=True)
    st.subheader('Eletricidade SIN — fatores documentados')
    st.dataframe(pd.DataFrame([{'Ano': year, **data} for year, data in ELECTRICITY_FACTORS.items()]), hide_index=True)
    st.write('CO₂ de eletricidade e CO₂ fóssil de combustíveis não equivalem a CO₂e completo. CH₄/N₂O e CO₂ biogênico não são somados ao indicador parcial. Combustíveis: fatores componentes de 2025 aplicados a misturas 2024–2026; não são fatores oficiais finais da mistura.')
    st.write('Cobertura parcial: não inclui alimentação, bens, serviços, viagens aéreas nem todas as emissões indiretas. Valores são estimativas de exemplo.')
    st.write('Para uso real: substituir fatores por fontes oficiais com ano, região, fronteira de cálculo, combustível e metodologia compatíveis.')

with st.expander('Excluir registro incorreto'):
    to_delete = st.selectbox('ID do registro', df['id'].tolist())
    if st.button('Excluir definitivamente'):
        delete_activity(conn, int(to_delete))
        st.rerun()
