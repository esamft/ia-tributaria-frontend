"""
Modelos para países e jurisdições tributárias.
Mapeamento e classificação de territórios fiscais.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class TaxRegimeType(str, Enum):
    """Tipos de regime tributário."""
    TERRITORIAL = "territorial"      # Tributação territorial
    WORLDWIDE = "worldwide"          # Tributação mundial (residência)
    MIXED = "mixed"                 # Sistema misto
    SPECIAL = "special"             # Regimes especiais


class JurisdictionType(str, Enum):
    """Tipos de jurisdição."""
    COUNTRY = "country"             # País soberano
    TERRITORY = "territory"         # Território/dependência
    SPECIAL_ZONE = "special_zone"   # Zona econômica especial
    TAX_HAVEN = "tax_haven"        # Paraíso fiscal tradicional
    LOW_TAX = "low_tax"            # Baixa tributação


class Country(BaseModel):
    """Modelo de país para sistema tributário."""
    
    # Identificação
    name: str = Field(..., description="Nome oficial do país")
    common_name: str = Field(..., description="Nome comum")
    iso_code_2: str = Field(..., min_length=2, max_length=2, description="Código ISO 2 letras")
    iso_code_3: str = Field(..., min_length=3, max_length=3, description="Código ISO 3 letras")
    
    # Classificação tributária
    tax_regime: TaxRegimeType = Field(..., description="Tipo de regime tributário")
    jurisdiction_type: JurisdictionType = Field(..., description="Tipo de jurisdição")
    
    # Informações fiscais básicas
    personal_income_tax_rate: Optional[float] = Field(None, ge=0, le=100, description="Taxa máxima IR pessoa física")
    corporate_tax_rate: Optional[float] = Field(None, ge=0, le=100, description="Taxa IR pessoa jurídica")
    capital_gains_tax_rate: Optional[float] = Field(None, ge=0, le=100, description="Taxa ganhos de capital")
    
    # Residência fiscal
    tax_residency_days: Optional[int] = Field(None, ge=0, le=365, description="Dias para residência fiscal")
    domicile_based: bool = Field(False, description="Sistema baseado em domicílio")
    
    # Tratados
    has_treaty_with_brazil: bool = Field(False, description="Tem tratado com Brasil")
    treaty_effective_date: Optional[str] = Field(None, description="Data efetiva do tratado")
    
    # CRS e transparência
    crs_participant: bool = Field(False, description="Participa do CRS")
    fatca_compliant: bool = Field(False, description="Compliance com FATCA")
    
    # Geográfico
    region: str = Field(..., description="Região geográfica")
    continent: str = Field(..., description="Continente")
    
    # Idiomas
    official_languages: List[str] = Field(default_factory=list, description="Idiomas oficiais")
    
    @validator('iso_code_2', 'iso_code_3')
    def normalize_iso_codes(cls, v):
        """Normaliza códigos ISO para uppercase."""
        return v.upper().strip()
    
    @validator('name', 'common_name')
    def validate_country_names(cls, v):
        """Valida nomes de países."""
        if len(v.strip()) < 2:
            raise ValueError("Nome do país deve ter pelo menos 2 caracteres")
        return v.strip().title()


class TaxJurisdiction(BaseModel):
    """Jurisdição tributária com análise estratégica."""
    
    # Base
    country: Country = Field(..., description="Informações do país")
    
    # Análise estratégica
    attractiveness_score: float = Field(..., ge=0, le=10, description="Score de atratividade (0-10)")
    complexity_level: int = Field(..., ge=1, le=5, description="Nível de complexidade (1-5)")
    
    # Público-alvo
    ideal_for_profiles: List[str] = Field(..., description="Perfis ideais de cliente")
    minimum_net_worth: Optional[int] = Field(None, ge=0, description="Patrimônio mínimo recomendado")
    
    # Vantagens e desvantagens
    advantages: List[str] = Field(..., description="Principais vantagens")
    disadvantages: List[str] = Field(..., description="Principais desvantagens")
    
    # Requisitos
    residency_requirements: List[str] = Field(..., description="Requisitos de residência")
    investment_requirements: Optional[str] = Field(None, description="Investimentos obrigatórios")
    
    # Custos estimados
    setup_cost_usd: Optional[int] = Field(None, ge=0, description="Custo setup em USD")
    annual_cost_usd: Optional[int] = Field(None, ge=0, description="Custo anual em USD")
    
    # Timing
    processing_time_months: Optional[int] = Field(None, ge=1, le=60, description="Tempo processo em meses")
    
    # Observações do estrategista
    strategist_notes: Optional[str] = Field(None, description="Notas do estrategista")
    last_updated: str = Field(..., description="Última atualização")
    
    def get_summary_card(self) -> Dict[str, Any]:
        """Retorna cartão resumo da jurisdição."""
        return {
            "country": self.country.common_name,
            "regime": self.country.tax_regime.value.title(),
            "attractiveness": f"{self.attractiveness_score}/10",
            "complexity": "★" * self.complexity_level,
            "treaty_brazil": "✅" if self.country.has_treaty_with_brazil else "❌",
            "crs": "✅" if self.country.crs_participant else "❌",
            "setup_cost": f"${self.setup_cost_usd:,}" if self.setup_cost_usd else "N/A",
            "processing_time": f"{self.processing_time_months}m" if self.processing_time_months else "N/A"
        }


# Lista de países prioritários para o sistema
PRIORITY_COUNTRIES = {
    "portugal": {"iso2": "PT", "iso3": "PRT", "region": "europa"},
    "espanha": {"iso2": "ES", "iso3": "ESP", "region": "europa"},
    "reino_unido": {"iso2": "GB", "iso3": "GBR", "region": "europa"},
    "irlanda": {"iso2": "IE", "iso3": "IRL", "region": "europa"},
    "suica": {"iso2": "CH", "iso3": "CHE", "region": "europa"},
    "malta": {"iso2": "MT", "iso3": "MLT", "region": "europa"},
    "chipre": {"iso2": "CY", "iso3": "CYP", "region": "europa"},
    "estados_unidos": {"iso2": "US", "iso3": "USA", "region": "americas"},
    "uruguai": {"iso2": "UY", "iso3": "URY", "region": "americas"},
    "panama": {"iso2": "PA", "iso3": "PAN", "region": "americas"},
    "paraguai": {"iso2": "PY", "iso3": "PRY", "region": "americas"},
    "singapura": {"iso2": "SG", "iso3": "SGP", "region": "asia"},
    "hong_kong": {"iso2": "HK", "iso3": "HKG", "region": "asia"},
    "emirados_arabes": {"iso2": "AE", "iso3": "ARE", "region": "middle_east"},
    "brasil": {"iso2": "BR", "iso3": "BRA", "region": "americas"}
}


def get_country_by_name(name: str) -> Optional[str]:
    """
    Identifica país por nome comum ou variações.
    Retorna código normalizado ou None.
    """
    name_lower = name.lower().strip()
    
    # Mapeamento de variações comuns
    variations = {
        "portugal": ["portugal", "pt", "portugues"],
        "espanha": ["espanha", "spain", "es", "espanhol"],
        "reino_unido": ["reino unido", "uk", "england", "inglaterra", "gb", "great britain"],
        "estados_unidos": ["estados unidos", "usa", "us", "america", "eua"],
        "suica": ["suiça", "switzerland", "ch", "swiss"],
        "singapura": ["singapura", "singapore", "sg"],
        "hong_kong": ["hong kong", "hk"],
        "emirados_arabes": ["emirados", "uae", "dubai", "abu dhabi"],
    }
    
    for country_code, variants in variations.items():
        if any(variant in name_lower for variant in variants):
            return country_code
    
    return None