"""Carbon Footprint Lab V7.3: English-language personal emissions dashboard."""
from datetime import date
from decimal import Decimal
import hashlib
import tempfile
from pathlib import Path
import pandas as pd
import streamlit as st
from personal.calculator import calculate_emissions
from personal.database import connect, initialize, add_activity, list_activities, delete_activity
from personal.factors import FACTORS, ELECTRICITY_FACTORS, resolve_factor, normalize_category
from personal.v72 import import_sin_csv

st.set_page_config(page_title='Carbon Footprint Lab | Personal', page_icon='🌿', layout='wide')
st.title('🌿 Carbon Footprint Lab — Personal Carbon Footprint')
st.warning('V7.3: 2026 MCTI monthly factors require verified import. Fuel estimates include fossil CO₂, CH₄, and N₂O; biogenic CO₂ is reported separately. This is not a certified emissions inventory.')
st.caption('V1–V7.3 | Local SQLite storage | Keep grid CO₂, fossil CO₂, and combustion CO₂e boundaries distinct.')
connection = connect()
initialize(connection)

with st.sidebar:
    st.header('Add an activity')
    with st.form('activity', clear_on_submit=True):
        activity_date = st.date_input('Activity date', value=date.today())
        category = st.selectbox('Category', list(FACTORS))
        documented = st.checkbox('Use documented factors where available', value=True,
            disabled=category not in ('Electricity', 'Regular gasoline (liters)', 'Premium gasoline (liters)', 'Diesel B (liters)'))
        try:
            specification = resolve_factor(category, activity_date, use_official=documented)
            st.caption(f"Unit: {specification['unit']} | Factor: {specification['factor']} {specification['factor_unit']} | Source: {specification['source']}")
            factor_error = None
        except ValueError as error:
            factor_error = str(error)
            st.error(factor_error)
            specification = None
        quantity = st.number_input('Quantity', min_value=0.0, step=1.0, format='%.3f')
        notes = st.text_input('Notes (optional)', max_chars=200)
        submitted = st.form_submit_button('Save activity', use_container_width=True)
        if submitted:
            if factor_error:
                st.error('Activity not saved: ' + factor_error)
            else:
                add_activity(connection, activity_date, category, quantity, notes, use_official=documented)
                st.success('Activity saved successfully. Check the activity table for the recorded emissions components.')
    st.info('Do not record both fuel consumption and distance for the same journey: this would double-count emissions.')
    with st.expander('Import 2026 MCTI monthly factors'):
        st.caption('Obtain the official 2026 Corporate Inventories workbook from MCTI. Independently verify each monthly value and prepare a CSV with columns year,month,factor_tco2_mwh. The original XLSX SHA-256 is retained for traceability. Do not use CDM margin factors.')
        official_file = st.file_uploader('Original MCTI XLSX workbook', type='xlsx')
        month_csv = st.file_uploader('Verified monthly values CSV', type='csv')
        if official_file and month_csv and st.button('Import verified months'):
            digest = hashlib.sha256(official_file.getvalue()).hexdigest()
            with tempfile.TemporaryDirectory() as folder:
                csv_path = Path(folder) / 'monthly.csv'
                csv_path.write_bytes(month_csv.getvalue())
                try:
                    imported = import_sin_csv(csv_path, digest, official_file.name)
                    st.success(f"Imported {len(imported['monthly'])} months. Verify that the CSV matches the original workbook.")
                except (ValueError, OSError) as error:
                    st.error(str(error))

records = list_activities(connection)
if not records:
    st.info('No activities recorded yet. Use the form in the sidebar to add your first activity.')
    st.stop()

data = pd.DataFrame(records)
data['category'] = data['category'].map(normalize_category)
data['activity_date'] = pd.to_datetime(data['activity_date'])
data['emissions_kg'] = data['emissions_kg'].map(lambda value: float(Decimal(value)))
data['quantity'] = data['quantity'].map(lambda value: float(Decimal(value)))
data['month'] = data['activity_date'].dt.strftime('%Y-%m')
months = sorted(data['month'].unique().tolist(), reverse=True)
selected_months = st.multiselect('Filter by month', months, default=months)
selected_categories = st.multiselect('Filter by category', sorted(data['category'].unique().tolist()), default=sorted(data['category'].unique().tolist()))
filtered = data[data['month'].isin(selected_months) & data['category'].isin(selected_categories)].copy()

metrics = st.columns(3)
documented_rows = filtered[~filtered['factor_quality'].fillna('').isin(('illustrative', 'didatico'))]
metrics[0].metric('Documented partial indicator', f"{documented_rows['emissions_kg'].sum():,.2f} kg")
metrics[1].metric('Recorded activities', len(filtered))
metrics[2].metric('Categories', filtered['category'].nunique())

if not filtered.empty:
    left, right = st.columns(2)
    with left:
        st.subheader('Partial emissions by category (kg; mixed boundaries)')
        st.bar_chart(filtered.groupby('category')['emissions_kg'].sum())
    with right:
        st.subheader('Monthly partial emissions (kg; mixed boundaries)')
        st.line_chart(filtered.groupby('month')['emissions_kg'].sum())
    st.subheader('Fuel emissions components')
    biogenic = pd.to_numeric(filtered['co2_biogenic_kg'], errors='coerce').fillna(0).sum()
    st.metric('Biogenic CO₂ (reported separately)', f'{biogenic:,.3f} kg')
    st.caption('These charts combine partial indicators with different accounting boundaries and may include illustrative records. They do not represent a complete personal carbon footprint.')
    st.subheader('Activity records')
    columns = ['id', 'activity_date', 'category', 'quantity', 'unit', 'factor', 'factor_source', 'factor_year', 'factor_quality', 'factor_url', 'gas', 'emissions_kg', 'co2_fossil_kg', 'ch4_kg', 'n2o_kg', 'nonco2_co2e_kg', 'co2_biogenic_kg', 'methodology', 'notes']
    display = filtered[columns].copy()
    display['activity_date'] = display['activity_date'].dt.strftime('%Y-%m-%d')
    display['factor_quality'] = display['factor_quality'].replace({'didatico':'illustrative', 'oficial':'official', 'oficial_arredondado':'official_rounded', 'calculado_fontes_publicas':'derived_from_public_sources', 'publicado_conferencia_secundaria':'published_secondary_verification', 'transcrito_do_arquivo_oficial_a_conferir':'transcribed_from_official_workbook_pending_verification'})
    display['gas'] = display['gas'].replace({'CO2e combustão':'combustion CO2e', 'CO2 fóssil':'fossil CO2'})
    display['factor_source'] = display['factor_source'].replace({'EXEMPLO DIDÁTICO':'ILLUSTRATIVE EXAMPLE'})
    display['factor_source'] = display['factor_source'].fillna('').str.replace('fração biocombustível', 'biofuel share', regex=False).str.replace('média anual', 'annual average', regex=False).str.replace('conferência secundária', 'secondary verification', regex=False).str.replace('reproduzido pela', 'reproduced by', regex=False)
    display['methodology'] = display['methodology'].fillna('').str.replace('estimativa derivada', 'derived estimate', regex=False)
    display['unit'] = display['unit'].replace({'litro':'liter', 'km.passageiro':'passenger-km'})
    st.dataframe(display, use_container_width=True, hide_index=True)
    st.download_button('Export filtered CSV', display.to_csv(index=False).encode('utf-8-sig'), file_name='carbon_footprint_personal.csv', mime='text/csv')
else:
    st.info('No records match the selected filters.')

with st.expander('Emission factors and limitations'):
    st.dataframe(pd.DataFrame([{'Category': name, **values} for name, values in FACTORS.items()]), hide_index=True)
    st.subheader('SIN electricity — documented annual factors')
    st.dataframe(pd.DataFrame([{'Year': year, **values} for year, values in ELECTRICITY_FACTORS.items()]), hide_index=True)
    st.write('Grid electricity CO₂ and fossil fuel CO₂ are not the same as complete CO₂e. Fuel CH₄/N₂O are included in the combustion CO₂e estimate; biogenic CO₂ remains separate. Fuel factors are derived estimates, not official final blend factors.')
    st.write('Incomplete coverage: food, goods, services, air travel, and other indirect emissions are excluded. Some categories remain illustrative.')
    st.write('For reporting, validate factor year, geography, source, system boundaries, and methodology.')

with st.expander('Delete an incorrect record'):
    record_id = st.selectbox('Record ID', data['id'].tolist())
    if st.button('Permanently delete record'):
        delete_activity(connection, int(record_id))
        st.rerun()
