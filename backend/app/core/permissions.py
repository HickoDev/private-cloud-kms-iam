from enum import StrEnum


class Permission(StrEnum):
    USER_READ = "USER_READ"
    USER_CREATE = "USER_CREATE"
    USER_UPDATE = "USER_UPDATE"
    ROLE_ASSIGN = "ROLE_ASSIGN"
    KEY_READ = "KEY_READ"
    KEY_CREATE = "KEY_CREATE"
    KEY_DISABLE = "KEY_DISABLE"
    KEY_ROTATE = "KEY_ROTATE"
    DATA_ENCRYPT = "DATA_ENCRYPT"
    DATA_DECRYPT = "DATA_DECRYPT"
    AUDIT_READ = "AUDIT_READ"


ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    "ADMIN": set(Permission),
    "KEY_MANAGER": {
        Permission.KEY_READ,
        Permission.KEY_CREATE,
        Permission.KEY_DISABLE,
        Permission.KEY_ROTATE,
    },
    "KEY_USER": {
        Permission.KEY_READ,
        Permission.DATA_ENCRYPT,
        Permission.DATA_DECRYPT,
    },
    "AUDITOR": {
        Permission.KEY_READ,
        Permission.AUDIT_READ,
    },
}

