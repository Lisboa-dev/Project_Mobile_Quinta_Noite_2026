
from __future__ import annotations

import enum
import uuid

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    String, Integer, DateTime, Date, Numeric, ForeignKey, Text,
    Enum as SAEnum, UniqueConstraint, Index, func, Boolean
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ============================================================
# BASE
# ============================================================

class Base(DeclarativeBase):
    pass


# ============================================================
# ENUMS
# ============================================================

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    STAFF = "STAFF"


class ProductStatus(str, enum.Enum):
    IN_STOCK = "IN_STOCK"
    RESERVED = "RESERVED"
    SOLD = "SOLD"


class PaymentType(str, enum.Enum):
    CASH = "CASH"
    PIX = "PIX"
    CARD = "CARD"
    PROMISSORY = "PROMISSORY"
    FINANCING = "FINANCING"


class SaleStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    CANCELED = "CANCELED"


class PromissoryStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    CANCELED = "CANCELED"
    PAID = "PAID"


class InstallmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELED = "CANCELED"


class FinanceStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELED = "CANCELED"


class WppSendStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENDING = "SENDING"
    SENT = "SENT"
    FAILED = "FAILED"

# ============================================================
# TENANT
# ============================================================

class TenantORM(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    cnpj: Mapped[Optional[str]] = mapped_column(String(14))
    owner_whatsapp: Mapped[Optional[str]] = mapped_column(String(20))

    # 🔥 NOVO
    pix_key: Mapped[Optional[str]] = mapped_column(String(120))

    offers_group_ids: Mapped[Optional[str]] = mapped_column(Text)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    blocked_reason: Mapped[Optional[str]] = mapped_column(String(200))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    users: Mapped[List["UserORM"]] = relationship(back_populates="tenant")

# ============================================================
# USERS
# ============================================================

class UserORM(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(160), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.STAFF,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    tenant: Mapped["TenantORM"] = relationship(back_populates="users")
    sales: Mapped[List["SaleORM"]] = relationship(back_populates="user")


# ============================================================
# CLIENTS
# ============================================================

class ClientORM(Base):
    __tablename__ = "clients"
    __table_args__ = (Index("ix_clients_phone", "phone"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(140), nullable=False)
    phone: Mapped[str] = mapped_column(String(11), nullable=False)
    cpf: Mapped[Optional[str]] = mapped_column(String(11))
    address: Mapped[Optional[str]] = mapped_column(String(255))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    sales: Mapped[List["SaleORM"]] = relationship(back_populates="client")
    promissories: Mapped[List["PromissoryORM"]] = relationship(back_populates="client")


# ============================================================
# PRODUCTS
# ============================================================

class ProductORM(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("tenant_id", "plate", name="uq_products_tenant_plate"),
        UniqueConstraint("tenant_id", "chassi", name="uq_products_tenant_chassi"),
        Index("ix_products_status", "status"),
        Index("ix_products_brand_model", "brand", "model"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )

    brand: Mapped[str] = mapped_column(String(60), nullable=False)
    model: Mapped[str] = mapped_column(String(80), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    plate: Mapped[Optional[str]] = mapped_column(String(7), nullable=True, unique=True)
    chassi: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    km: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    color: Mapped[str] = mapped_column(String(30), nullable=False)

    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    sale_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    status: Mapped[ProductStatus] = mapped_column(
        SAEnum(ProductStatus, name="product_status"),
        nullable=False,
        default=ProductStatus.IN_STOCK,
    )

    # ✅ NOVO: snapshot/auditoria do vendedor (origem da compra) por produto
    purchase_seller_name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    purchase_seller_phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    purchase_seller_cpf: Mapped[Optional[str]] = mapped_column(String(14), nullable=True)  # pode guardar com máscara ou sem
    purchase_seller_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    sale: Mapped[Optional["SaleORM"]] = relationship(back_populates="product", uselist=False)
    promissories: Mapped[List["PromissoryORM"]] = relationship(back_populates="product")

    # ✅ imagens do produto
    images: Mapped[List["ProductImageORM"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImageORM.position",
    )
    costs: Mapped[List["ProductCostORM"]] = relationship(
    back_populates="product",
    cascade="all, delete-orphan",
    )

# ============================================================
# PRODUCT COSTS
# ============================================================

class ProductCostORM(Base):
    __tablename__ = "product_costs"
    __table_args__ = (
        Index("ix_product_costs_product", "product_id"),
        Index("ix_product_costs_tenant", "tenant_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    product: Mapped["ProductORM"] = relationship(back_populates="costs")

# ============================================================
# PRODUCT IMAGES
# ============================================================

class ProductImageORM(Base):
    __tablename__ = "product_images"
    __table_args__ = (
        Index("ix_product_images_product", "product_id"),
        Index("ix_product_images_tenant", "tenant_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    url: Mapped[str] = mapped_column(String(500), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product: Mapped["ProductORM"] = relationship(back_populates="images")

# ============================================================
# SALES
# ============================================================

class SaleORM(Base):
    __tablename__ = "sales"
    __table_args__ = (
        UniqueConstraint("tenant_id", "public_id", name="uq_sales_tenant_public_id"),
        UniqueConstraint("tenant_id", "product_id", name="uq_sales_tenant_product_id"),
        Index("ix_sales_status", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )

    public_id: Mapped[str] = mapped_column(String(32), nullable=False)

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)

    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    # ✅ ADICIONAR
    entry_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    entry_amount_type: Mapped[Optional[PaymentType]] = mapped_column(
        SAEnum(PaymentType, name="payment_type"),
        nullable=True,
    )

    payment_type: Mapped[PaymentType] = mapped_column(
        SAEnum(PaymentType, name="payment_type"),
        nullable=False,
        default=PaymentType.CASH,
    )

    status: Mapped[SaleStatus] = mapped_column(
        SAEnum(SaleStatus, name="sale_status"),
        nullable=False,
        default=SaleStatus.DRAFT,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    client: Mapped["ClientORM"] = relationship(back_populates="sales")
    user: Mapped["UserORM"] = relationship(back_populates="sales")
    product: Mapped["ProductORM"] = relationship(back_populates="sale")
    alert_sent: Mapped[bool] = mapped_column(
    Boolean,
    nullable=False,
    default=False,
    )
# ============================================================
# PROMISSORIES
# ============================================================

class PromissoryORM(Base):
    __tablename__ = "promissories"
    __table_args__ = (
        UniqueConstraint("tenant_id", "public_id", name="uq_promissory_tenant_public_id"),
        UniqueConstraint("tenant_id", "sale_id", name="uq_promissory_tenant_sale_id"),
        Index("ix_promissories_status", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )

    public_id: Mapped[str] = mapped_column(String(32), nullable=False)

    sale_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sales.id"))
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id"))

    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    entry_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    daily_late_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    status: Mapped[PromissoryStatus] = mapped_column(
        SAEnum(PromissoryStatus, name="promissory_status"),
        nullable=False,
        default=PromissoryStatus.DRAFT,
    )

    issued_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    snapshot_json: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    sale: Mapped[Optional["SaleORM"]] = relationship(backref="promissory", uselist=False)
    client: Mapped["ClientORM"] = relationship(back_populates="promissories")
    product: Mapped[Optional["ProductORM"]] = relationship(back_populates="promissories")

    installments: Mapped[List["InstallmentORM"]] = relationship(
        back_populates="promissory",
        cascade="all, delete-orphan",
        lazy="selectin",  # 🔥 IMPORTANTE
        order_by="InstallmentORM.number",
    )


# ============================================================
# INSTALLMENTS
# ============================================================

class InstallmentORM(Base):
    __tablename__ = "installments"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "promissory_id",
            "number",
            name="uq_installment_tenant_promissory_number",
        ),
        Index("ix_installments_due", "due_date", "status"),
        Index("ix_installments_wpp_due", "wa_due_status", "wa_due_next_retry_at"),
        Index("ix_installments_wpp_overdue", "wa_overdue_status", "wa_overdue_next_retry_at"),
        Index("ix_installments_wpp_today", "wa_today_status", "wa_today_next_retry_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )

    promissory_id: Mapped[int] = mapped_column(
        ForeignKey("promissories.id"),
        nullable=False,
    )

    number: Mapped[int] = mapped_column(Integer, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    status: Mapped[InstallmentStatus] = mapped_column(
        SAEnum(InstallmentStatus, name="installment_status"),
        nullable=False,
        default=InstallmentStatus.PENDING,
    )

    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    paid_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    note: Mapped[Optional[str]] = mapped_column(Text)

    late_days: Mapped[Optional[int]] = mapped_column(Integer)
    late_fee_charged: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))

    # WHATSAPP CONTROLE

    wa_due_status: Mapped[WppSendStatus] = mapped_column(
        SAEnum(WppSendStatus, name="wpp_installment_due_status"),
        nullable=False,
        default=WppSendStatus.PENDING,
    )
    wa_due_tries: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wa_due_last_error: Mapped[Optional[str]] = mapped_column(Text)
    wa_due_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    wa_due_next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    wa_overdue_status: Mapped[WppSendStatus] = mapped_column(
        SAEnum(WppSendStatus, name="wpp_installment_overdue_status"),
        nullable=False,
        default=WppSendStatus.PENDING,
    )
    wa_overdue_tries: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wa_overdue_last_error: Mapped[Optional[str]] = mapped_column(Text)
    wa_overdue_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    wa_overdue_next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    wa_today_status: Mapped[WppSendStatus] = mapped_column(
        SAEnum(WppSendStatus, name="wpp_installment_today_status"),
        nullable=False,
        default=WppSendStatus.PENDING,
    )
    wa_today_tries: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wa_today_last_error: Mapped[Optional[str]] = mapped_column(Text)
    wa_today_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    wa_today_next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    promissory: Mapped["PromissoryORM"] = relationship(back_populates="installments")


# ============================================================
# FINANCE
# ============================================================

class FinanceORM(Base):
    __tablename__ = "finance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )

    company: Mapped[str] = mapped_column(String(120), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)

    status: Mapped[FinanceStatus] = mapped_column(
        SAEnum(FinanceStatus, name="finance_status"),
        nullable=False,
        default=FinanceStatus.PENDING,
    )

    description: Mapped[Optional[str]] = mapped_column(String(200))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    wpp_status: Mapped[WppSendStatus] = mapped_column(
        SAEnum(WppSendStatus, name="wpp_finance_status"),
        nullable=False,
        default=WppSendStatus.PENDING,
    )

    wpp_tries: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wpp_last_error: Mapped[Optional[str]] = mapped_column(Text)
    wpp_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    wpp_next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


# ============================================================
# INTEGRATION TOKENS
# ============================================================

class IntegrationTokenORM(Base):
    __tablename__ = "integration_tokens"
    __table_args__ = (
        UniqueConstraint("tenant_id", "provider", name="uq_tenant_provider"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(String(50), nullable=False)

    access_token: Mapped[Optional[str]] = mapped_column(Text)
    token_type: Mapped[Optional[str]] = mapped_column(String(20))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    base_url: Mapped[Optional[str]] = mapped_column(String(255))

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )