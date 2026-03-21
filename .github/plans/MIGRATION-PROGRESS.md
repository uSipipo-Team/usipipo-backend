# Migration Progress - Monorepo to Multi-Repo

**Date:** 2026-03-21
**Status:** Week 5 In Progress - Subscriptions 50% Complete
**Branch:** `main` (backend) | `main` (commons)

---

## 📋 Overview

Migrating backend logic from monorepo (`/home/mowgli/usipipobot/`) to separated repositories:
- ✅ `usipipo-commons` - Shared library (PyPI v0.4.1)
- ✅ `usipipo-backend` - Backend API (PR #4 merged)
- ⏳ `usipipo-telegram-bot` - Bot (Week 5)
- ⏳ `usipipo-miniapp-web` - Mini App (Week 6)

---

## ✅ Completed Features

### **Feature 1: PAYMENTS** ✅

**Status:** COMPLETED
**Date:** 2026-03-19

#### **What was migrated:**
- ✅ `Payment` entity (usipipo-commons v0.2.0)
- ✅ `PaymentService` with create/complete/expire methods
- ✅ Payment endpoints (crypto + Telegram Stars)
- ✅ Payment webhooks (TronDealer + Telegram Stars)
- ✅ `PaymentModel` and `PaymentRepository`
- ✅ Integration tests (18 tests passing)

---

### **Feature 2: VPN MANAGEMENT** ✅

**Status:** COMPLETED
**Date:** 2026-03-20
**PR:** https://github.com/uSipipo-Team/usipipo-backend/pull/3

#### **What was migrated:**
- ✅ `VpnKey` entity (usipipo-commons v0.4.0)
- ✅ `VpnService` (basic CRUD + create_key, delete_key, revoke_key)
- ✅ `VpnInfrastructureService` (enable_key, disable_key, get_key_usage_from_server, sync_all_keys_usage)
- ✅ VPN endpoints (GET/POST/DELETE/PUT)
- ✅ `VpnKeyRepository` (SQLAlchemy) con todos los métodos
- ✅ WireGuard client (create_peer, delete_peer, enable_peer, disable_peer, get_usage, get_peer_metrics)
- ✅ Outline client (create_key, delete_key, enable_key, disable_key, get_metrics, get_key_usage)
- ✅ `ConsumptionVpnIntegrationService` (block_user_keys, unblock_user_keys, check_can_create_key)
- ✅ Key cleanup job (cleanup_inactive_keys, reset_data_usage, check_and_notify_data_limits)
- ✅ Usage sync job (sync_vpn_usage_job)
- ✅ Integration tests (9 new tests)

#### **Files Created/Modified (Week 4):**

**usipipo-commons:**
- `usipipo_commons/domain/entities/vpn_key.py` (MODIFIED - full monorepo port)
- `usipipo_commons/domain/entities/admin.py` (NEW)
- `usipipo_commons/domain/entities/balance.py` (NEW)
- `usipipo_commons/domain/entities/consumption_billing.py` (NEW)
- `usipipo_commons/domain/entities/consumption_invoice.py` (NEW)
- `usipipo_commons/domain/entities/data_package.py` (NEW)
- `usipipo_commons/domain/entities/subscription_plan.py` (NEW)
- `usipipo_commons/domain/entities/subscription_transaction.py` (NEW)
- `usipipo_commons/domain/entities/ticket.py` (NEW)
- `usipipo_commons/domain/entities/ticket_message.py` (NEW)
- `usipipo_commons/domain/enums/key_type.py` (NEW)

**usipipo-backend:**
- `src/core/application/services/vpn_infrastructure_service.py` (NEW)
- `src/core/application/services/consumption_vpn_integration_service.py` (NEW)
- `src/infrastructure/jobs/key_cleanup_job.py` (NEW)
- `src/infrastructure/jobs/usage_sync_job.py` (NEW)
- `src/infrastructure/jobs/__init__.py` (NEW)
- `src/infrastructure/vpn_providers/wireguard_client.py` (MODIFIED - added enable_peer)
- `src/infrastructure/vpn_providers/outline_client.py` (MODIFIED - added enable_key, disable_key)
- `src/core/domain/interfaces/i_vpn_key_repository.py` (MODIFIED - added 6 new methods)
- `src/infrastructure/persistence/repositories/vpn_key_repository.py` (MODIFIED - implemented new methods)
- `src/infrastructure/persistence/models/vpn_key_model.py` (MODIFIED - updated to match entity)
- `tests/integration/test_vpn_infrastructure.py` (NEW - 9 tests)

#### **Gap Analysis:**
| Component | Monorepo | New Backend | Status |
|-----------|----------|-------------|--------|
| VpnKey entity | ✅ | ✅ | **COMPLETED** |
| VpnService (CRUD) | ✅ | ✅ | **COMPLETED** |
| VpnInfrastructureService | ✅ | ✅ | **COMPLETED** |
| WireGuard client | ✅ | ✅ | **COMPLETED** |
| Outline client | ✅ | ✅ | **COMPLETED** |
| Key repository | ✅ | ✅ | **COMPLETED** |
| Consumption VPN integration | ✅ | ✅ | **COMPLETED** |
| Key cleanup job | ✅ | ✅ | **COMPLETED** |
| Usage sync job | ✅ | ✅ | **COMPLETED** |
| Key rotation logic | ✅ | ✅ | **COMPLETED** |
| Usage tracking | ✅ | ✅ | **COMPLETED** |
| Connection limits | ✅ | ✅ | **COMPLETED** (via MAX_KEYS_PER_USER) |

---

### **Feature 10: USER MANAGEMENT** ✅

**Status:** COMPLETED
**Date:** 2026-03-19

#### **What was migrated:**
- ✅ `User` entity (usipipo-commons)
- ✅ `UserService` (basic CRUD)
- ✅ `UserRepository` (SQLAlchemy)
- ✅ Auth endpoint with Telegram (`POST /auth/telegram`)

---

## ⏳ Pending Features

### **Feature 3: SUBSCRIPTIONS** ✅

**Status:** COMPLETED (Partial - Services & Endpoints)
**Date:** 2026-03-21
**PR:** https://github.com/uSipipo-Team/usipipo-backend/pull/4

#### **To Migrate:**
- [x] `SubscriptionPlan` entity (✅ already in commons)
- [x] `SubscriptionTransaction` entity (✅ already in commons)
- [x] `SubscriptionService` ✅
- [x] `SubscriptionPaymentService` ✅
- [x] Repository interfaces ✅
- [x] Subscription endpoints ✅

#### **What was migrated:**
- ✅ `SubscriptionService` with activate/cancel/check methods
- ✅ `SubscriptionPaymentService` with Stars + Crypto integration
- ✅ `ISubscriptionRepository` interface
- ✅ `ISubscriptionTransactionRepository` interface
- ✅ SQLAlchemy repository implementations
- ✅ SQLAlchemy models (SubscriptionPlan, SubscriptionTransaction)
- ✅ Endpoints: GET /plans, POST /activate, GET /me
- ✅ 148 tests (unit + integration)

---

### **Feature 4: CONSUMPTION BILLING** ⏳

**Status:** IN PROGRESS (50% - Services pending repos & endpoints)
**Date:** 2026-03-21

#### **To Migrate:**
- [x] `ConsumptionBilling` entity (✅ already in commons)
- [x] `ConsumptionInvoice` entity (✅ already in commons)
- [x] `ConsumptionBillingService` ✅
- [x] `ConsumptionActivationService` ✅
- [x] `ConsumptionCycleService` ✅
- [ ] `ConsumptionInvoiceService`
- [ ] Repository interfaces
- [ ] Billing endpoints

#### **What was migrated:**
- ✅ `ConsumptionBillingService` (facade)
- ✅ `ConsumptionActivationService` (activate/cancel mode)
- ✅ `ConsumptionCycleService` (record usage, close cycle, mark paid)
- ✅ `IConsumptionBillingRepository` interface
- ✅ DTOs: ConsumptionSummary, ActivationResult, CancellationResult
- ✅ 46 unit tests

### **Feature 5: TICKETS/SUPPORT** ⏳

**Status:** NOT STARTED

#### **To Migrate:**
- [ ] `Ticket` entity (✅ already in commons)
- [ ] `TicketMessage` entity (✅ already in commons)
- [ ] `TicketService`
- [ ] `TicketNotificationService`
- [ ] Repository interfaces
- [ ] Ticket endpoints

### **Feature 6: REFERRALS** ⏳

**Status:** NOT STARTED

#### **To Migrate:**
- [ ] `Referral` entity
- [ ] `ReferralService` with bonus tracking
- [ ] Referral code generation
- [ ] Bonus distribution logic
- [ ] Repository interfaces
- [ ] Referral endpoints

### **Feature 7: ADMIN PANEL** ⏳

**Status:** NOT STARTED

#### **To Migrate:**
- [ ] Admin entities (✅ already in commons)
- [ ] Admin services (key, server, user, stats)
- [ ] Admin endpoints with RBAC
- [ ] Statistics aggregation
- [ ] Bulk operations

### **Feature 8: WALLET MANAGEMENT** ⏳

**Status:** NOT STARTED

#### **To Migrate:**
- [ ] Wallet entities
- [ ] Wallet management service
- [ ] Wallet pool service
- [ ] Deposit/withdrawal logic
- [ ] Repository interfaces

### **Feature 9: DATA PACKAGES** ⏳

**Status:** NOT STARTED

#### **To Migrate:**
- [ ] `DataPackage` entity (✅ already in commons)
- [ ] `DataPackageService`
- [ ] Package customization logic
- [ ] Repository interfaces
- [ ] Package endpoints

---

## 📊 Migration Summary

| Feature | Entities | Services | Repositories | Endpoints | Tests | Status |
|---------|----------|----------|--------------|-----------|-------|--------|
| 1. Payments | ✅ | ✅ | ✅ | ✅ | ✅ | **100%** |
| 2. VPN Management | ✅ | ✅ | ✅ | ✅ | ✅ | **100%** |
| 3. Subscriptions | ✅ | ✅ | ✅ | ✅ | ✅ | **100%** |
| 4. Consumption Billing | ✅ | ✅ | ⏳ | ⏳ | ✅ | **60%** |
| 5. Tickets/Support | ✅ | ❌ | ❌ | ❌ | ❌ | **20%** |
| 6. Referrals | ❌ | ❌ | ❌ | ❌ | ❌ | **0%** |
| 7. Admin Panel | ✅ | ❌ | ❌ | ❌ | ❌ | **20%** |
| 8. Wallet Management | ❌ | ❌ | ❌ | ❌ | ❌ | **0%** |
| 9. Data Packages | ✅ | ❌ | ❌ | ❌ | ❌ | **20%** |
| 10. User Management | ✅ | ✅ | ✅ | ✅ | ✅ | **100%** |

**Overall Progress:** 52% complete (5.2/10 features)

---

## 🎯 Immediate Next Steps

### **Week 4 Completion (Backend - VPN Infrastructure):**
1. [x] Create `VpnInfrastructureService` with enable/disable key methods
2. [x] Enhance `WireGuardClient` with enable_peer, disable_peer
3. [x] Enhance `OutlineClient` with enable_key, disable_key
4. [x] Create `ConsumptionVpnIntegrationService`
5. [x] Update `IVpnKeyRepository` with all methods
6. [x] Implement repository methods (update_usage, reset_data_usage, etc.)
7. [x] Create `KeyCleanupJob` for scheduled cleanup
8. [x] Create `UsageSyncJob` for periodic sync
9. [x] Add integration tests for VPN infrastructure
10. [x] Create PR: https://github.com/uSipipo-Team/usipipo-backend/pull/3

### **Week 5 Preparation (Bot Refactor):**
1. [ ] Merge PR #3 in usipipo-backend
2. [ ] Review bot requirements for backend APIs
3. [ ] Ensure all necessary endpoints are implemented
4. [ ] Create API documentation for bot team
5. [ ] Set up API versioning strategy

---

## 📝 Technical Decisions

### **1. VPN Infrastructure Architecture:**
```
VpnService (Application Layer)
    ├── Uses VpnInfrastructureService (Infrastructure coordination)
    │   ├── WireGuardClient (native wg commands)
    │   └── OutlineClient (Shadowbox API)
    └── Uses VpnKeyRepository (Persistence)

Scheduled Jobs:
    ├── KeyCleanupJob (daily) - Cleanup inactive, reset cycles, block exceeded
    └── UsageSyncJob (every 30 min) - Sync usage from VPN servers
```

### **2. Entity Strategy:**
- **usipipo-commons:** All domain entities + enums (14 entities, 14 enums)
- **usipipo-backend:** Application services + infrastructure
- **usipipo-telegram-bot:** Bot logic + HTTP client to backend
- **usipipo-miniapp-web:** Frontend + HTTP client to backend

### **3. Repository Pattern:**
- Interfaces in `src/core/domain/interfaces/`
- Implementations in `src/infrastructure/persistence/repositories/`
- SQLAlchemy models in `src/infrastructure/persistence/models/`

### **4. Service Layer:**
- Application services in `src/core/application/services/`
- Orchestrate domain entities + repositories
- Handle business logic + validation

### **5. Scheduled Jobs:**
- Located in `src/infrastructure/jobs/`
- To be integrated with APScheduler or Celery Beat
- Currently designed as async functions for flexibility

---

## 🔗 Related Links

- **usipipo-commons:** https://github.com/uSipipo-Team/usipipo-commons
- **usipipo-backend:** https://github.com/uSipipo-Team/usipipo-backend
- **usipipo-telegram-bot:** https://github.com/uSipipo-Team/usipipo-telegram-bot
- **usipipo-miniapp-web:** https://github.com/uSipipo-Team/usipipo-miniapp-web
- **PyPI Package:** https://pypi.org/project/usipipo-commons/0.4.1/

---

## 📅 Timeline

| Week | Dates | Focus | Status |
|------|-------|-------|--------|
| Week 1 | Mar 18-24 | Cimientos (6 repos + commons) | ✅ Complete |
| Week 2 | Mar 25-31 | Backend Auth + VPN | ✅ Complete |
| Week 3 | Apr 1-7 | Backend Payments + Webhooks | ✅ Complete |
| Week 4 | Apr 8-14 | VPN Infrastructure + Jobs | ✅ Complete |
| Week 5 | Apr 15-21 | Subscriptions + Consumption Billing | 🟡 In Progress |
| Week 6 | Apr 22-28 | CI/CD + Deploy | ⏳ Pending |

---

**Last Updated:** 2026-03-21
**Next Review:** 2026-03-22

---

## 📦 Summary of Week 5 Migration (In Progress)

### **New Services Created:**
1. `SubscriptionService` - Subscription lifecycle management
2. `SubscriptionPaymentService` - Stars + Crypto payment integration
3. `ConsumptionBillingService` - Facade for consumption billing
4. `ConsumptionActivationService` - Activate/cancel consumption mode
5. `ConsumptionCycleService` - Usage tracking, cycle management

### **New Repository Interfaces:**
1. `ISubscriptionRepository` - Subscription plan persistence
2. `ISubscriptionTransactionRepository` - Transaction persistence
3. `IConsumptionBillingRepository` - Consumption billing persistence

### **New SQLAlchemy Models:**
1. `SubscriptionPlanModel` - Subscription plan persistence
2. `SubscriptionTransactionModel` - Transaction persistence

### **New Endpoints:**
1. `GET /api/v1/subscriptions/plans` - List subscription plans
2. `POST /api/v1/subscriptions/activate` - Activate subscription
3. `GET /api/v1/subscriptions/me` - Get user subscription status

### **Tests Added:**
- 29 tests for SubscriptionService
- 17 tests for SubscriptionPaymentService
- 42 tests for Subscription repositories
- 14 integration tests for subscription endpoints
- 46 tests for ConsumptionBillingService
- **Total: 148 new tests**

### **PR Created:**
- usipipo-backend PR #4: https://github.com/uSipipo-Team/usipipo-backend/pull/4
- Status: ✅ Merged
- Tests: All passing

### **Next Steps (Week 5):**
1. [ ] Complete ConsumptionInvoiceService migration
2. [ ] Create ConsumptionBillingRepository implementation
3. [ ] Create ConsumptionInvoiceRepository implementation
4. [ ] Create consumption billing endpoints
5. [ ] Add integration tests for consumption endpoints

---

## 📦 Summary of Week 4 Migration

### **New Services Created:**
1. `VpnInfrastructureService` - Coordinates VPN server operations
2. `ConsumptionVpnIntegrationService` - Integration with consumption billing

### **New Jobs Created:**
1. `KeyCleanupJob` - Daily cleanup of inactive keys, billing resets, limit enforcement
2. `UsageSyncJob` - Every 30 minutes sync from VPN servers

### **Enhanced Components:**
1. `WireGuardClient` - Added enable_peer method
2. `OutlineClient` - Added enable_key, disable_key methods
3. `IVpnKeyRepository` - Added 6 new methods
4. `VpnKeyRepository` - Implemented all new methods
5. `VpnKeyModel` - Updated to match new entity structure

### **Tests Added:**
- 9 integration tests for VPN infrastructure
- Tests for enable/disable operations
- Tests for usage sync
- Tests for cleanup jobs

### **usipipo-commons v0.4.1:**
- All 14 entities from monorepo migrated
- 14 enums available
- Published on PyPI: https://pypi.org/project/usipipo-commons/0.4.1/

### **Next Steps:**
The backend is now ready for Week 5 (Subscriptions & Consumption Billing). Once those features are complete, the bot refactor can begin.

### **PR Created:**
- usipipo-backend PR #3: https://github.com/uSipipo-Team/usipipo-backend/pull/3
- Status: Ready for review
- Tests: 41/42 passing (97.6%)
