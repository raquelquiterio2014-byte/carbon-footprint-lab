"""V2: Explicitly illustrative factors; replace with sourced factors for real inventories."""
FACTORS = {
    'Eletricidade': {'unit': 'kWh', 'factor': '0.10', 'factor_unit': 'kg CO2e/kWh', 'source': 'EXEMPLO DIDÁTICO', 'year': None},
    'Gasolina': {'unit': 'litro', 'factor': '2.30', 'factor_unit': 'kg CO2e/litro', 'source': 'EXEMPLO DIDÁTICO', 'year': None},
    'Ônibus': {'unit': 'km.passageiro', 'factor': '0.08', 'factor_unit': 'kg CO2e/km.passageiro', 'source': 'EXEMPLO DIDÁTICO', 'year': None},
    'Automóvel (distância)': {'unit': 'km', 'factor': '0.18', 'factor_unit': 'kg CO2e/km', 'source': 'EXEMPLO DIDÁTICO', 'year': None},
}
# Avoid double-counting gasoline and automobile-distance for the same journey.
