"""Versioned factor catalog. Electricity: published Brazil SIN annual averages.
Other categories remain illustrative and are never represented as official.
"""
ELECTRICITY_FACTORS = {
    2023: {'factor': '0.0385', 'source': 'MCTI/SIRENE (média anual 2023)', 'url': 'https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/noticias/2024/02/fator-de-emissao-de-co2-na-geracao-de-energia-eletrica-no-brasil-em-2023-e-o-menor-em-12-anos', 'quality': 'oficial', 'gas': 'CO2'},
    2025: {'factor': '0.0461', 'source': 'MCTI/SIRENE 2025 (média anual; conferência secundária)', 'url': 'https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/dados-e-ferramentas/fatores-de-emissao', 'quality': 'publicado_conferencia_secundaria', 'gas': 'CO2'},
    2024: {'factor': '0.058', 'source': 'MCTI, reproduzido pela CETESB (média anual arredondada 2024)', 'url': 'https://cetesb.sp.gov.br/wp-content/uploads/2025/08/INVENTARIO-GEE-CETESB-2024-v7.pdf', 'quality': 'oficial_arredondado', 'gas': 'CO2'},
}
FACTORS = {
    'Eletricidade': {'unit': 'kWh', 'factor': '0.10', 'factor_unit': 'kg CO2e/kWh', 'source': 'EXEMPLO DIDÁTICO', 'year': None, 'quality': 'didatico', 'url': '', 'gas': 'CO2e'},
    'Gasolina comum (litros)': {'unit': 'litro', 'factor': '0', 'factor_unit': 'kg CO2 fóssil/litro', 'source': 'ANP mistura E27/E30 + fator componente gasolina pura GHG Protocol 2025 reproduzido em inventário público', 'year': None, 'quality': 'calculado_fontes_publicas', 'url': 'https://www.gov.br/anp/pt-br/assuntos/distribuicao-e-revenda/revendedor/informacoes-uteis', 'gas': 'CO2 fóssil'},
    'Gasolina premium (litros)': {'unit': 'litro', 'factor': '0', 'factor_unit': 'kg CO2 fóssil/litro', 'source': 'ANP E25 + fator componente gasolina pura GHG Protocol 2025 reproduzido em inventário público', 'year': None, 'quality': 'calculado_fontes_publicas', 'url': 'https://www.gov.br/anp/pt-br/assuntos/distribuicao-e-revenda/revendedor/informacoes-uteis', 'gas': 'CO2 fóssil'},
    'Diesel B (litros)': {'unit': 'litro', 'factor': '0', 'factor_unit': 'kg CO2 fóssil/litro', 'source': 'ANP B14/B15 + fator componente diesel puro GHG Protocol 2025 reproduzido em inventário público', 'year': None, 'quality': 'calculado_fontes_publicas', 'url': 'https://www.gov.br/anp/pt-br/assuntos/distribuicao-e-revenda/revendedor/informacoes-uteis', 'gas': 'CO2 fóssil'},
    'Gasolina': {'unit': 'litro', 'factor': '2.30', 'factor_unit': 'kg CO2e/litro', 'source': 'EXEMPLO DIDÁTICO', 'year': None, 'quality': 'didatico', 'url': '', 'gas': 'CO2e'},
    'Ônibus': {'unit': 'km.passageiro', 'factor': '0.08', 'factor_unit': 'kg CO2e/km.passageiro', 'source': 'EXEMPLO DIDÁTICO', 'year': None, 'quality': 'didatico', 'url': '', 'gas': 'CO2e'},
    'Automóvel (distância)': {'unit': 'km', 'factor': '0.18', 'factor_unit': 'kg CO2e/km', 'source': 'EXEMPLO DIDÁTICO', 'year': None, 'quality': 'didatico', 'url': '', 'gas': 'CO2e'},
}


def resolve_factor(category, activity_date, use_official=True):
    if category not in FACTORS:
        raise ValueError('Categoria desconhecida')
    spec = dict(FACTORS[category])
    if category == 'Eletricidade' and use_official:
        annual = ELECTRICITY_FACTORS.get(activity_date.year)
        if annual is None:
            raise ValueError(f'Não há fator anual SIN validado no catálogo para {activity_date.year}. Escolha modo didático explicitamente ou use 2023/2024.')
        spec.update(annual)
        spec['year'] = activity_date.year
        spec['factor_unit'] = 'kg CO2/kWh'
    if category in ('Gasolina comum (litros)', 'Gasolina premium (litros)', 'Diesel B (litros)') and use_official:
        from decimal import Decimal
        from datetime import date
        transition = date(2025, 8, 1)
        if activity_date.year not in (2024, 2025, 2026):
            raise ValueError('Mistura histórica não validada para esta data (suporte: 2024–2026).')
        if category == 'Gasolina comum (litros)':
            bio = Decimal('0.30') if activity_date >= transition else Decimal('0.27')
            pure = Decimal('2.212')
        elif category == 'Gasolina premium (litros)':
            bio = Decimal('0.25')
            pure = Decimal('2.212')
        else:
            bio = Decimal('0.15') if activity_date >= transition else Decimal('0.14')
            pure = Decimal('2.603')
        spec['factor'] = str((Decimal('1') - bio) * pure)
        spec['year'] = activity_date.year
        spec['source'] += f' | fração biocombustível: {bio * 100}%'
        spec['factor_unit'] = 'kg CO2 fóssil/litro'
    elif category in ('Gasolina comum (litros)', 'Gasolina premium (litros)', 'Diesel B (litros)'):
        raise ValueError('Esta categoria exige o modo documentado; não há fator didático substituto.')
    return spec
