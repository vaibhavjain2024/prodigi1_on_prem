from ..repositories.msil_variant_repository import MSILVariantRepository
from ..repositories.models.msil_variant import MSILVariant
from .service import Service

class MSILVariantService(Service):
    def __init__(self, repository : MSILVariantRepository):
        self.repository = repository