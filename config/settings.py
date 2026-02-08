import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32).hex())
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Samba AD connection settings
    SAMBA_REALM = os.environ.get("SAMBA_REALM", "EXAMPLE.LOCAL")
    SAMBA_DOMAIN = os.environ.get("SAMBA_DOMAIN", "EXAMPLE")
    SAMBA_DC_HOST = os.environ.get("SAMBA_DC_HOST", "localhost")
    SAMBA_ADMIN_USER = os.environ.get("SAMBA_ADMIN_USER", "Administrator")

    # LDAP settings derived from realm
    @property
    def LDAP_BASE_DN(self):
        return ",".join(f"DC={part}" for part in self.SAMBA_REALM.split("."))

    @property
    def LDAP_URI(self):
        return f"ldap://{self.SAMBA_DC_HOST}"

    # samba-tool path
    SAMBA_TOOL_PATH = os.environ.get("SAMBA_TOOL_PATH", "/usr/bin/samba-tool")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
