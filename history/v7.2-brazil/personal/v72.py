"""V7.2: traceable SIN monthly import and transparent combustion components."""
import csv
import hashlib
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

MCTI_URL = 'https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/dados-e-ferramentas/fatores-de-emissao'
IPCC_URL = 'https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_3_Ch3_Mobile_Combustion.pdf'
CATALOG = Path(__file__).resolve().parent.parent / 'data' / 'sin_2026_monthly.json'
# IPCC 2006, vol.2 ch.3 table 3.2.2; default technology assumptions.
# Values kg gas / TJ. Fuel NCV MJ/L is an explicit approximation, not official Brazilian fuel-specific measurement.
TECH = {'gasoline_1995_plus': ('3.8', '5.7'), 'diesel_heavy': ('3.9', '3.9')}
NCV = {'gasoline': Decimal('32.0'), 'ethanol': Decimal('21.1'), 'diesel': Decimal('35.8'), 'biodiesel': Decimal('33.3')}
GWP = {'CH4': Decimal('28'), 'N2O': Decimal('265')}  # IPCC AR5 100-year, no climate-carbon feedback
CO2_FOSSIL = {'gasoline': Decimal('2.212'), 'diesel': Decimal('2.603')}
# Biogenic factors are transparent STOICHIOMETRIC APPROXIMATIONS, not official factors.
CO2_BIO = {'ethanol': Decimal('1.51'), 'biodiesel': Decimal('2.50')}


def import_sin_csv(csv_path, source_xlsx_sha256, source_filename, destination=CATALOG):
    """Import independently transcribed/verified monthly rows from the official workbook.

    CSV columns: year,month,factor_tco2_mwh. Never silently invent missing months.
    A SHA-256 of the ORIGINAL official XLSX is required for provenance.
    """
    if len(source_xlsx_sha256) != 64 or any(c not in '0123456789abcdef' for c in source_xlsx_sha256.lower()):
        raise ValueError('Informe SHA-256 válido da planilha XLSX original do MCTI.')
    with open(csv_path, encoding='utf-8-sig', newline='') as file:
        rows = list(csv.DictReader(file))
    if not rows:
        raise ValueError('CSV vazio')
    values = {}
    for row in rows:
        if set(row) != {'year', 'month', 'factor_tco2_mwh'}:
            raise ValueError('Cabeçalho deve ser year,month,factor_tco2_mwh')
        year, month = int(row['year']), int(row['month'])
        factor = Decimal(row['factor_tco2_mwh'].replace(',', '.'))
        if year != 2026 or not 1 <= month <= 12 or not factor.is_finite() or not 0 <= factor <= Decimal('2'):
            raise ValueError('Ano/mês/fator inválido')
        key = f'{year}-{month:02d}'
        if key in values:
            raise ValueError('Mês duplicado')
        values[key] = str(factor)
    payload = {'source': 'MCTI/SIRENE Inventários Corporativos 2026', 'source_url': MCTI_URL,
               'source_file': source_filename, 'source_sha256': source_xlsx_sha256,
               'unit': 'tCO2/MWh = kgCO2/kWh', 'status': 'transcrito_do_arquivo_oficial_a_conferir',
               'monthly': values}
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return payload


def monthly_factor(day, catalog=CATALOG):
    if day.year != 2026:
        raise ValueError('Catálogo mensal reservado a 2026')
    path = Path(catalog)
    if not path.exists():
        raise ValueError('Planilha oficial de 2026 ainda não importada. Nenhum fator será presumido.')
    payload = json.loads(path.read_text(encoding='utf-8'))
    key = day.strftime('%Y-%m')
    if key not in payload['monthly']:
        raise ValueError(f'Fator MCTI ainda não cadastrado para {key}')
    return {'factor': payload['monthly'][key], 'source': payload['source'] + ' | ' + key,
            'url': payload['source_url'], 'quality': payload['status'], 'gas': 'CO2',
            'year': 2026, 'month': day.month}


def blend(category, day):
    if day.year not in (2024, 2025, 2026):
        raise ValueError('Composição histórica não validada')
    transition = date(2025, 8, 1)
    if category == 'Gasolina comum (litros)':
        return 'gasoline', 'ethanol', Decimal('0.30') if day >= transition else Decimal('0.27'), 'gasoline_1995_plus'
    if category == 'Gasolina premium (litros)':
        return 'gasoline', 'ethanol', Decimal('0.25'), 'gasoline_1995_plus'
    if category == 'Diesel B (litros)':
        return 'diesel', 'biodiesel', Decimal('0.15') if day >= transition else Decimal('0.14'), 'diesel_heavy'
    raise ValueError('Combustível desconhecido')


def fuel_components(category, day, litres):
    amount = Decimal(str(litres))
    if not amount.is_finite() or amount < 0:
        raise ValueError('Litros inválidos')
    fossil, bio, share, tech = blend(category, day)
    fossil_l, bio_l = amount * (1-share), amount * share
    co2_fossil = fossil_l * CO2_FOSSIL[fossil]
    co2_biogenic = bio_l * CO2_BIO[bio]
    energy_tj = (fossil_l * NCV[fossil] + bio_l * NCV[bio]) / Decimal('1000000')
    ch4_factor, n2o_factor = map(Decimal, TECH[tech])
    ch4_kg, n2o_kg = energy_tj * ch4_factor, energy_tj * n2o_factor
    nonco2 = ch4_kg * GWP['CH4'] + n2o_kg * GWP['N2O']
    return {'co2_fossil_kg': co2_fossil, 'ch4_kg': ch4_kg, 'n2o_kg': n2o_kg,
            'nonco2_co2e_kg': nonco2, 'co2e_combustion_kg': co2_fossil + nonco2,
            'co2_biogenic_kg': co2_biogenic, 'biogenic_share': share,
            'method': 'IPCC 2006 Table 3.2.2 default technology; NCV approximations; GWP AR5; biogenic CO2 estimated',
            'quality': 'estimativa_derivada_nao_fator_oficial_final', 'source_url': IPCC_URL}
