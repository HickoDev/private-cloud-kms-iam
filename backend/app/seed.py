from app.core.database import Base, SessionLocal, engine
from app.core.permissions import ROLE_PERMISSIONS, Permission as PermissionEnum
from app.core.security import hash_password
from app.iam.models import Permission, Role, User
import app.models  # noqa: F401

ROLE_DESCRIPTIONS = {
    "ADMIN": "Full access to the academic KMS platform.",
    "KEY_MANAGER": "Can create, disable, and rotate cryptographic keys.",
    "KEY_USER": "Can encrypt and decrypt data with active keys.",
    "AUDITOR": "Can read audit logs and key metadata.",
}

PERMISSION_DESCRIPTIONS = {
    PermissionEnum.USER_READ: "View users.",
    PermissionEnum.USER_CREATE: "Create users.",
    PermissionEnum.USER_UPDATE: "Update users.",
    PermissionEnum.ROLE_ASSIGN: "Assign roles to users.",
    PermissionEnum.KEY_READ: "View key metadata.",
    PermissionEnum.KEY_CREATE: "Create cryptographic keys.",
    PermissionEnum.KEY_DISABLE: "Disable cryptographic keys.",
    PermissionEnum.KEY_ROTATE: "Rotate cryptographic keys.",
    PermissionEnum.DATA_ENCRYPT: "Encrypt data.",
    PermissionEnum.DATA_DECRYPT: "Decrypt data.",
    PermissionEnum.AUDIT_READ: "View audit logs.",
}


def seed() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        permission_by_name: dict[str, Permission] = {}

        for permission in PermissionEnum:
            model = (
                db.query(Permission)
                .filter(Permission.name == permission.value)
                .one_or_none()
            )
            if model is None:
                model = Permission(
                    name=permission.value,
                    description=PERMISSION_DESCRIPTIONS[permission],
                )
                db.add(model)
            permission_by_name[permission.value] = model

        db.flush()

        role_by_name: dict[str, Role] = {}
        for role_name, permissions in ROLE_PERMISSIONS.items():
            role = db.query(Role).filter(Role.name == role_name).one_or_none()
            if role is None:
                role = Role(
                    name=role_name,
                    description=ROLE_DESCRIPTIONS[role_name],
                )
                db.add(role)

            role.permissions = [
                permission_by_name[permission.value] for permission in permissions
            ]
            role_by_name[role_name] = role

        admin = db.query(User).filter(User.email == "admin@example.com").one_or_none()
        if admin is None:
            admin = User(
                username="admin",
                email="admin@example.com",
                password_hash=hash_password("admin123"),
                is_active=True,
                roles=[role_by_name["ADMIN"]],
            )
            db.add(admin)
        elif role_by_name["ADMIN"] not in admin.roles:
            admin.roles.append(role_by_name["ADMIN"])

        db.commit()


if __name__ == "__main__":
    seed()

