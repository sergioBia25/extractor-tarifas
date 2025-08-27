"""
Módulo que contiene el JSON de ejemplo con IDs estáticos para las tarifas eléctricas.
"""

# Mapeo de mercados a IDs
MERCADOS = {
    'ANTIOQUIA': 1,
    'BAJO PUTUMAYO': 3,
    'BOGOTA': 4,
    'BOYACA': 5,
    'CALDAS': 6,
    'CALI': 7,
    'CAQUETA': 8,
    'CARIBE MAR': 9,
    'CARIBE SOL': 10,
    'CARTAGO': 11,
    'CASANARE': 12,
    'CAUCA': 13,
    'CUNDINAMARCA': 16,
    'HUILA': 17,
    'META': 19,
    'NARIÑO': 20,
    'NORTE SANTANDER': 21,
    'PEREIRA': 23,
    'PUTUMAYO': 24,
    'QUINDIO': 25,
    'SANTANDER': 28,
    'TOLIMA': 29,
    'TULUA': 30,
    'VALLE': 31,
    'YUMBO': 32
}

# Mapeo de niveles de tensión a IDs
NIVELES_TENSION = {
    '1 OR': 1,
    '1 Comp': 2,
    '1 US': 3,
    '2': 4,
    '3': 5
}

# Mapeo de operadores a IDs
OPERADORES = {
    'VATIA': 1,
    'ENELX': 2,
    'QI': 3,
    'ENERTOTAL': 4,
    'NEU': 5
}

# JSON de ejemplo
EXAMPLE_JSON = {
    "id": 1223,
    "period": "2024-03-20",
    "user_email": "admin@example.com",
    "operator_id": 1,
    "operator_name": "VATIA",
    "status": "active",
    "created_at": "2024-03-20T10:00:00",
    "updated_at": "2024-03-20T10:00:00",
    "rates": [
        {
            "id": 1,
            "rate_loading_id": 1223,
            "region_id": 1,
            "region_name": "ANTIOQUIA",
            "tension_level_id": 1,
            "tension_level_name": "1 OR",
            "generation": 380.0,
            "transmission": 78.0,
            "distribution": 222.0,
            "commercialization": 29.0,
            "operation_transaction": 0.0,
            "losses": 33.0,
            "restrictions": 29.0,
            "unit_cost": 771.0,
            "unit_cost_with_contribution": 771.0,
            "status": "active",
            "created_at": "2024-03-20T10:00:00",
            "updated_at": "2024-03-20T10:00:00"
        }
    ]
} 