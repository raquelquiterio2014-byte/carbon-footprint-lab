"""V5/V6: Streamlit dashboard, filters, exports and validation."""
from datetime import date
from decimal import Decimal
import pandas as pd
import streamlit as st
from personal.calculator import calculate_emissions
from personal.database import connect, initialize, add_activity, list_activities, delete_activity
from personal.factors import FACTORS, ELECTRICITY_FACTORS, resolve_factor

st.set_page_config(page_title='Carbon Footprint Lab | Pessoal', page_icon='🌿', layout='wide')
st.title('🌿 Carbon Footprint Lab — Pegada Pessoal')
st.warning('V7: eletricidade 2023/2024 usa fatores anuais do SIN documentados (CO₂); transporte continua DIDÁTICO. Não é uma pegada pessoal completa nem inventário certificado.')
st.caption('V1–V7 integradas | SQLite local | Eletricidade em kg CO₂; demais categorias em kg CO₂e ilustrativos')
conn = connect()
initialize(conn)

with st.sidebar:
    st.header('Registrar atividade')
    with st.form('activity', clear_on_submit=True):
        activity_date = st.date_input('Data', value=date.today())
        category = st.selectbox('Categoria', list(FACTORS))
        official = st.checkbox('Usar fator SIN documentado (somente eletricidade)', value=True, disabled=category != 'Eletricidade')
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
col1.metric('Total misto indicativo', f"{filtered['emissions_kg'].sum():,.2f} kg")
col2.metric('Atividades', len(filtered))
col3.metric('Categorias', filtered['category'].nunique())

if not filtered.empty:
    left, right = st.columns(2)
    with left:
        st.subheader('Emissões por categoria (kg CO₂e)')
        st.bar_chart(filtered.groupby('category')['emissions_kg'].sum())
    with right:
        st.subheader('Evolução mensal (kg CO₂e)')
        st.line_chart(filtered.groupby('month')['emissions_kg'].sum())
    st.subheader('Registros')
    display = filtered[['id', 'activity_date', 'category', 'quantity', 'unit', 'factor', 'factor_source', 'factor_year', 'factor_quality', 'factor_url', 'gas', 'emissions_kg', 'notes']].copy()
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
    st.write('CO₂ de eletricidade não é o mesmo que CO₂e de ciclo de vida. O total combinado é apenas indicativo e não é inventário completo.')
    st.write('Cobertura parcial: não inclui alimentação, bens, serviços, viagens aéreas nem todas as emissões indiretas. Valores são estimativas de exemplo.')
    st.write('Para uso real: substituir fatores por fontes oficiais com ano, região, fronteira de cálculo, combustível e metodologia compatíveis.')

with st.expander('Excluir registro incorreto'):
    to_delete = st.selectbox('ID do registro', df['id'].tolist())
    if st.button('Excluir definitivamente'):
        delete_activity(conn, int(to_delete))
        st.rerun()
