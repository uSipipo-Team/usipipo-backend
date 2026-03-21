"""
Administrative user management service for uSipipo backend.

This service is dedicated to user management from the admin panel.
"""

import logging

from usipipo_commons.domain.entities.admin_operation_result import AdminOperationResult
from usipipo_commons.domain.entities.admin_user_info import AdminUserInfo

from src.core.domain.interfaces.i_admin_service import IAdminUserService

logger = logging.getLogger(__name__)


class AdminUserService(IAdminUserService):
    """Service dedicated to user management from admin panel."""

    def __init__(
        self,
        user_repository,
        vpn_repository,
        payment_repository,
    ):
        self.user_repository = user_repository
        self.vpn_repository = vpn_repository
        self.payment_repository = payment_repository

    async def get_all_users(self, current_user_id: int) -> list[AdminUserInfo]:
        """Get list of all registered users."""
        try:
            users = await self.user_repository.get_all()

            user_list = []
            for user in users:
                user_keys = await self.vpn_repository.get_by_user_id(user.id)
                active_keys = [k for k in user_keys if k.is_active]

                # Get user balance from payments
                user_payments = await self.payment_repository.get_by_user_id(user.id)
                total_balance = sum(p.amount for p in user_payments)

                user_info = AdminUserInfo(
                    user_id=user.telegram_id,
                    username=user.username,
                    first_name=user.first_name or "Unknown",
                    last_name=user.last_name,
                    total_keys=len(user_keys),
                    active_keys=len(active_keys),
                    stars_balance=total_balance,
                    total_deposited=getattr(user, "referral_credits", 0) or 0,
                    referral_credits=getattr(user, "referral_credits", 0) or 0,
                    registration_date=user.created_at,
                    last_activity=getattr(user, "last_activity", None),
                )
                user_list.append(user_info)

            return user_list

        except Exception as e:
            logger.error(f"Error getting all users: {e}", exc_info=True)
            return []

    async def get_users_paginated(self, page: int, per_page: int, current_user_id: int) -> dict:
        """Get paginated users."""
        try:
            all_users = await self.get_all_users(current_user_id)

            total = len(all_users)
            start = (page - 1) * per_page
            end = start + per_page

            paginated_users = all_users[start:end]

            return {
                "users": [u.__dict__ for u in paginated_users],
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page,
            }

        except Exception as e:
            logger.error(f"Error getting paginated users: {e}", exc_info=True)
            return {
                "users": [],
                "total": 0,
                "page": page,
                "per_page": per_page,
                "total_pages": 0,
            }

    async def get_user_by_id(self, user_id: int) -> AdminUserInfo | None:
        """Get detailed information of a user by Telegram ID."""
        try:
            user = await self.user_repository.get_by_telegram_id(user_id)
            if not user:
                return None

            user_keys = await self.vpn_repository.get_by_user_id(user.id)
            active_keys = [k for k in user_keys if k.is_active]

            return AdminUserInfo(
                user_id=user.telegram_id,
                username=user.username,
                first_name=user.first_name or "Unknown",
                last_name=user.last_name,
                total_keys=len(user_keys),
                active_keys=len(active_keys),
                stars_balance=0,
                total_deposited=getattr(user, "referral_credits", 0) or 0,
                referral_credits=getattr(user, "referral_credits", 0) or 0,
                registration_date=user.created_at,
                last_activity=getattr(user, "last_activity", None),
            )

        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}", exc_info=True)
            return None

    async def update_user_status(self, user_id: int, status: str) -> AdminOperationResult:
        """Update user status (ACTIVE, SUSPENDED, BLOCKED)."""
        try:
            user = await self.user_repository.get_by_telegram_id(user_id)
            if not user:
                return AdminOperationResult(
                    success=False,
                    operation="update_user_status",
                    target_id=str(user_id),
                    message=f"User {user_id} not found",
                )

            if status.upper() == "BLOCKED":
                user.is_admin = False

            await self.user_repository.update(user)

            return AdminOperationResult(
                success=True,
                operation="update_user_status",
                target_id=str(user_id),
                message=f"User status updated to {status}",
                details={"new_status": status},
            )

        except Exception as e:
            logger.error(f"Error updating user status: {e}", exc_info=True)
            return AdminOperationResult(
                success=False,
                operation="update_user_status",
                target_id=str(user_id),
                message=f"Error updating user status: {str(e)}",
            )

    async def delete_user(self, user_id: int) -> AdminOperationResult:
        """Delete a user and associated keys."""
        try:
            user = await self.user_repository.get_by_telegram_id(user_id)
            if not user:
                return AdminOperationResult(
                    success=False,
                    operation="delete_user",
                    target_id=str(user_id),
                    message=f"User {user_id} not found",
                )

            user_keys = await self.vpn_repository.get_by_user_id(user.id)
            for key in user_keys:
                await self.vpn_repository.delete(key.id)

            await self.user_repository.delete(user.id)

            return AdminOperationResult(
                success=True,
                operation="delete_user",
                target_id=str(user_id),
                message=f"User {user_id} and {len(user_keys)} keys deleted successfully",
                details={"keys_deleted": len(user_keys)},
            )

        except Exception as e:
            logger.error(f"Error deleting user: {e}", exc_info=True)
            return AdminOperationResult(
                success=False,
                operation="delete_user",
                target_id=str(user_id),
                message=f"Error deleting user: {str(e)}",
            )

    async def assign_role_to_user(
        self, user_id: int, role: str, duration_days: int | None = None
    ) -> AdminOperationResult:
        """Assign role to a user."""
        try:
            user = await self.user_repository.get_by_telegram_id(user_id)
            if not user:
                return AdminOperationResult(
                    success=False,
                    operation="assign_role",
                    target_id=str(user_id),
                    message=f"User {user_id} not found",
                )

            if role.upper() == "ADMIN":
                user.is_admin = True
            elif role.upper() == "USER":
                user.is_admin = False

            await self.user_repository.update(user)

            return AdminOperationResult(
                success=True,
                operation="assign_role",
                target_id=str(user_id),
                message=f"Role {role} assigned to user {user_id}",
                details={"role": role, "duration_days": duration_days},
            )

        except Exception as e:
            logger.error(f"Error assigning role: {e}", exc_info=True)
            return AdminOperationResult(
                success=False,
                operation="assign_role",
                target_id=str(user_id),
                message=f"Error assigning role: {str(e)}",
            )

    async def block_user(self, user_id: int) -> AdminOperationResult:
        """Block a user."""
        return await self.update_user_status(user_id, "BLOCKED")

    async def unblock_user(self, user_id: int) -> AdminOperationResult:
        """Unblock a user."""
        return await self.update_user_status(user_id, "ACTIVE")
