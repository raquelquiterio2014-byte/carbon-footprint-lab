"""Versioned factor catalog. Electricity: published Brazil SIN annual averages.
Other categories remain illustrative and are never represented as official.
"""
ELECTRICITY_FACTORS = {
    2023: {'factor': '0.0385', 'source': 'MCTI/SIRENE (média anual 2023)', 'url': 'https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/noticias/2024/02/fator-de-emissao-de-co2-na-geracao-de-energia-eletrica-no-brasil-em-2023-e-o-menor-em-12-anos', 'quality': 'oficial', 'gas': 'CO2'},
    2024: {'factor': '0.058', 'source': 'MCTI, reproduzido pela CETESB (média anual arredondada 2024)', 'url': 'https://cetesb.sp.gov.br/wp-content/uploads/2025/08/INVENTARIO-GEE-CETESB-2024-v7.pdf', 'quality': 'oficial_arredondado', 'gas': 'CO2'},
}
FACTORS = {
    'Eletricidade': {'unit': 'kWh', 'factor': '0.10', 'factor_unit': 'kg CO2e/kWh', 'source': 'EXEMPLO DIDÁTICO', 'year': None, 'quality': 'didatico', 'url': '', 'gas': 'CO2e'},
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
    return spec
