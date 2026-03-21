"""Endpoints para la gestión de paquetes de datos."""

from fastapi import APIRouter, Depends, HTTPException, status
from usipipo_commons.domain.entities.user import User

from src.core.application.services.data_package_service import DataPackageService
from src.infrastructure.api.v1.deps import get_current_user, get_data_package_service
from src.shared.schemas.data_package import (
    DataPackagePurchaseRequest,
    DataPackageResponse,
    PackageOptionResponse,
    PurchaseResponse,
    SlotOptionResponse,
    UserPackagesResponse,
)

router = APIRouter(prefix="/data-packages", tags=["data-packages"])


@router.get("/options", response_model=list[PackageOptionResponse])
async def get_package_options(
    service: DataPackageService = Depends(get_data_package_service),
):
    """Obtiene las opciones de paquetes de datos disponibles."""
    return service.get_available_packages()


@router.get("/slots/options", response_model=list[SlotOptionResponse])
async def get_slot_options(
    service: DataPackageService = Depends(get_data_package_service),
):
    """Obtiene las opciones de slots de claves disponibles."""
    return service.get_available_slots()


@router.get("/me", response_model=UserPackagesResponse)
async def get_my_packages(
    current_user: User = Depends(get_current_user),
    service: DataPackageService = Depends(get_data_package_service),
):
    """Obtiene los paquetes de datos del usuario actual."""
    packages = await service.package_repo.get_by_user(
        current_user.telegram_id, current_user.telegram_id
    )
    return {
        "packages": [DataPackageResponse.model_validate(p) for p in packages],
        "total_count": len(packages),
    }


@router.post("/purchase", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
async def purchase_package(
    request: DataPackagePurchaseRequest,
    current_user: User = Depends(get_current_user),
    service: DataPackageService = Depends(get_data_package_service),
):
    """Compra un nuevo paquete de datos."""
    try:
        package, bonuses = await service.purchase_package(
            telegram_id=current_user.telegram_id,
            package_type=request.package_type,
            telegram_payment_id=request.telegram_payment_id,
            current_user_id=current_user.telegram_id,
            is_referred_first_purchase=request.is_referred_first_purchase,
        )
        return {
            "package": DataPackageResponse.model_validate(package),
            "bonuses": bonuses,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la compra: {str(e)}",
        )
