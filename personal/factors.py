"""Versioned factor catalog. Electricity: published Brazil SIN annual averages.
Other categories remain illustrative and are never represented as official.
"""
ELECTRICITY_FACTORS = {
    2023: {'factor': '0.0385', 'source': 'MCTI/SIRENE (2023 annual average)', 'url': 'https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/noticias/2024/02/fator-de-emissao-de-co2-na-geracao-de-energia-eletrica-no-brasil-em-2023-e-o-menor-em-12-anos', 'quality': 'official', 'gas': 'CO2'},
    2025: {'factor': '0.0461', 'source': 'MCTI/SIRENE 2025 (annual average; secondary verification)', 'url': 'https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/dados-e-ferramentas/fatores-de-emissao', 'quality': 'published_secondary_verification', 'gas': 'CO2'},
    2024: {'factor': '0.058', 'source': 'MCTI, reproduced by CETESB (rounded 2024 annual average)', 'url': 'https://cetesb.sp.gov.br/wp-content/uploads/2025/08/INVENTARIO-GEE-CETESB-2024-v7.pdf', 'quality': 'official_rounded', 'gas': 'CO2'},
}
FACTORS = {
    'Electricity': {'unit': 'kWh', 'factor': '0.10', 'factor_unit': 'kg CO2e/kWh', 'source': 'ILLUSTRATIVE EXAMPLE', 'year': None, 'quality': 'illustrative', 'url': '', 'gas': 'CO2e'},
    'Regular gasoline (liters)': {'unit': 'liter', 'factor': '0', 'factor_unit': 'kg fossil CO2/liter', 'source': 'ANP E27/E30 blend + pure gasoline component factor from GHG Protocol 2025 reproduced in a public inventory', 'year': None, 'quality': 'derived_from_public_sources', 'url': 'https://www.gov.br/anp/pt-br/assuntos/distribuicao-e-revenda/revendedor/informacoes-uteis', 'gas': 'fossil CO2'},
    'Premium gasoline (liters)': {'unit': 'liter', 'factor': '0', 'factor_unit': 'kg fossil CO2/liter', 'source': 'ANP E25 blend + pure gasoline component factor from GHG Protocol 2025 reproduced in a public inventory', 'year': None, 'quality': 'derived_from_public_sources', 'url': 'https://www.gov.br/anp/pt-br/assuntos/distribuicao-e-revenda/revendedor/informacoes-uteis', 'gas': 'fossil CO2'},
    'Diesel B (liters)': {'unit': 'liter', 'factor': '0', 'factor_unit': 'kg fossil CO2/liter', 'source': 'ANP B14/B15 blend + pure diesel component factor from GHG Protocol 2025 reproduced in a public inventory', 'year': None, 'quality': 'derived_from_public_sources', 'url': 'https://www.gov.br/anp/pt-br/assuntos/distribuicao-e-revenda/revendedor/informacoes-uteis', 'gas': 'fossil CO2'},
    'Gasoline (illustrative)': {'unit': 'liter', 'factor': '2.30', 'factor_unit': 'kg CO2e/liter', 'source': 'ILLUSTRATIVE EXAMPLE', 'year': None, 'quality': 'illustrative', 'url': '', 'gas': 'CO2e'},
    'Bus (illustrative)': {'unit': 'passenger-km', 'factor': '0.08', 'factor_unit': 'kg CO2e/passenger-km', 'source': 'ILLUSTRATIVE EXAMPLE', 'year': None, 'quality': 'illustrative', 'url': '', 'gas': 'CO2e'},
    'Car (distance)': {'unit': 'km', 'factor': '0.18', 'factor_unit': 'kg CO2e/km', 'source': 'ILLUSTRATIVE EXAMPLE', 'year': None, 'quality': 'illustrative', 'url': '', 'gas': 'CO2e'},
}


def resolve_factor(category, activity_date, use_official=True):
    if category not in FACTORS:
        raise ValueError('Unknown category')
    spec = dict(FACTORS[category])
    if category == 'Electricity' and use_official:
        if activity_date.year == 2026:
            from .v72 import monthly_factor
            spec.update(monthly_factor(activity_date))
            spec['factor_unit'] = 'kg CO2/kWh'
            return spec
        annual = ELECTRICITY_FACTORS.get(activity_date.year)
        if annual is None:
            raise ValueError(f'No validated annual SIN factor is available for {activity_date.year}. Explicitly select illustrative mode or use a supported year.')
        spec.update(annual)
        spec['year'] = activity_date.year
        spec['factor_unit'] = 'kg CO2/kWh'
    if category in ('Regular gasoline (liters)', 'Premium gasoline (liters)', 'Diesel B (liters)') and use_official:
        from decimal import Decimal
        from datetime import date
        transition = date(2025, 8, 1)
        if activity_date.year not in (2024, 2025, 2026):
            raise ValueError('Historical blend has not been validated for this date (supported: 2024–2026).')
        if category == 'Regular gasoline (liters)':
            bio = Decimal('0.30') if activity_date >= transition else Decimal('0.27')
            pure = Decimal('2.212')
        elif category == 'Premium gasoline (liters)':
            bio = Decimal('0.25')
            pure = Decimal('2.212')
        else:
            bio = Decimal('0.15') if activity_date >= transition else Decimal('0.14')
            pure = Decimal('2.603')
        spec['factor'] = str((Decimal('1') - bio) * pure)
        spec['year'] = activity_date.year
        spec['source'] += f' | biofuel share: {bio * 100}%'
        spec['factor_unit'] = 'kg fossil CO2/liter'
    elif category in ('Regular gasoline (liters)', 'Premium gasoline (liters)', 'Diesel B (liters)'):
        raise ValueError('This category requires documented mode; no illustrative substitute is available.')
    return spec


# Translate historical categories from databases created before V7.3.
LEGACY_CATEGORIES = {
    'Eletricidade': 'Electricity',
    'Gasolina comum (litros)': 'Regular gasoline (liters)',
    'Gasolina premium (litros)': 'Premium gasoline (liters)',
    'Diesel B (litros)': 'Diesel B (liters)',
    'Gasolina': 'Gasoline (illustrative)',
    'Ônibus': 'Bus (illustrative)',
    'Automóvel (distância)': 'Car (distance)',
}

def normalize_category(category):
    """Normalize historical Portuguese category labels for English display."""
    return LEGACY_CATEGORIES.get(category, category)
