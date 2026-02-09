"""Service layer for interacting with Samba AD via samba-tool CLI."""

import subprocess
import shlex
from flask import current_app


class SambaError(Exception):
    """Raised when a samba-tool command fails."""

    def __init__(self, message, returncode=None):
        super().__init__(message)
        self.returncode = returncode


def _run_samba_tool(args, password=None):
    """Execute a samba-tool command and return stdout.

    Args:
        args: List of arguments to pass to samba-tool.
        password: If provided, passed via --password flag.

    Returns:
        stdout as a string.

    Raises:
        SambaError on non-zero exit.
    """
    samba_tool = current_app.config.get("SAMBA_TOOL_PATH", "/usr/bin/samba-tool")
    cmd = [samba_tool] + args

    if password:
        cmd += ["--password", password]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode != 0:
        error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
        raise SambaError(error_msg, result.returncode)

    return result.stdout


# ---------------------------------------------------------------------------
# User operations
# ---------------------------------------------------------------------------

def list_users():
    """Return a list of AD user account names."""
    output = _run_samba_tool(["user", "list"])
    return [line.strip() for line in output.splitlines() if line.strip()]


def get_user(username):
    """Return details for a single user as a dict."""
    output = _run_samba_tool(["user", "show", username])
    return _parse_ldif_output(output)


def create_user(username, password, given_name=None, surname=None,
                mail=None, must_change_at_next_login=False):
    """Create a new AD user."""
    args = ["user", "create", username, password]
    if given_name:
        args += ["--given-name", given_name]
    if surname:
        args += ["--surname", surname]
    if mail:
        args += ["--mail-address", mail]
    if must_change_at_next_login:
        args += ["--must-change-at-next-login"]
    return _run_samba_tool(args)


def delete_user(username):
    """Delete an AD user."""
    return _run_samba_tool(["user", "delete", username])


def disable_user(username):
    """Disable an AD user account."""
    return _run_samba_tool(["user", "disable", username])


def enable_user(username):
    """Enable an AD user account."""
    return _run_samba_tool(["user", "enable", username])


def reset_password(username, new_password):
    """Reset a user's password."""
    return _run_samba_tool(["user", "setpassword", username,
                            "--newpassword", new_password])


def set_user_expiry(username, days=None, no_expiry=False):
    """Set account expiry for a user."""
    if no_expiry:
        return _run_samba_tool(["user", "setexpiry", username, "--noexpiry"])
    if days is not None:
        return _run_samba_tool(["user", "setexpiry", username, "--days", str(days)])


# ---------------------------------------------------------------------------
# Group operations
# ---------------------------------------------------------------------------

def list_groups():
    """Return a list of AD group names."""
    output = _run_samba_tool(["group", "list"])
    return [line.strip() for line in output.splitlines() if line.strip()]


def get_group(groupname):
    """Return details for a group."""
    output = _run_samba_tool(["group", "show", groupname])
    return _parse_ldif_output(output)


def create_group(groupname, description=None, group_type=None):
    """Create a new AD group."""
    args = ["group", "create", groupname]
    if description:
        args += ["--description", description]
    if group_type:
        args += ["--group-type", group_type]
    return _run_samba_tool(args)


def delete_group(groupname):
    """Delete an AD group."""
    return _run_samba_tool(["group", "delete", groupname])


def add_group_members(groupname, members):
    """Add members to a group. members is a comma-separated string."""
    return _run_samba_tool(["group", "addmembers", groupname, members])


def remove_group_members(groupname, members):
    """Remove members from a group. members is a comma-separated string."""
    return _run_samba_tool(["group", "removemembers", groupname, members])


def list_group_members(groupname):
    """List members of a group."""
    output = _run_samba_tool(["group", "listmembers", groupname])
    return [line.strip() for line in output.splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# Computer / machine account operations
# ---------------------------------------------------------------------------

def list_computers():
    """Return a list of computer account names."""
    output = _run_samba_tool(["computer", "list"])
    return [line.strip() for line in output.splitlines() if line.strip()]


def get_computer(computer_name):
    """Return details for a computer account."""
    output = _run_samba_tool(["computer", "show", computer_name])
    return _parse_ldif_output(output)


def create_computer(computer_name, description=None, ip_address=None):
    """Create a new computer account for domain joining."""
    args = ["computer", "create", computer_name]
    if description:
        args += ["--description", description]
    if ip_address:
        args += ["--ip-address", ip_address]
    return _run_samba_tool(args)


def delete_computer(computer_name):
    """Delete a computer account."""
    return _run_samba_tool(["computer", "delete", computer_name])


# ---------------------------------------------------------------------------
# DNS operations (supplementary)
# ---------------------------------------------------------------------------

def list_dns_zones():
    """List DNS zones managed by Samba."""
    output = _run_samba_tool(["dns", "zonelist", "localhost", "--username",
                              current_app.config.get("SAMBA_ADMIN_USER", "Administrator")])
    return output


# ---------------------------------------------------------------------------
# Domain info
# ---------------------------------------------------------------------------

def domain_level():
    """Get the domain functional level."""
    return _run_samba_tool(["domain", "level", "show"])


def domain_info():
    """Get basic domain information."""
    output = _run_samba_tool(["domain", "info", current_app.config["SAMBA_DC_HOST"]])
    return output


# ---------------------------------------------------------------------------
# Authentication helper
# ---------------------------------------------------------------------------

def authenticate_user(username, password):
    """Attempt to authenticate a user against Samba AD.

    Uses samba-tool to verify credentials. Returns True on success.
    """
    try:
        ldap_uri = current_app.config.get("LDAP_URI", "ldap://localhost")
        _run_samba_tool(
            ["user", "show", username, "-H", ldap_uri, "--username", username],
            password=password,
        )
        return True
    except SambaError:
        return False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_ldif_output(output):
    """Parse samba-tool LDIF-style output into a dict.

    Multi-valued attributes are stored as lists.
    """
    result = {}
    for line in output.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if key in result:
            if isinstance(result[key], list):
                result[key].append(value)
            else:
                result[key] = [result[key], value]
        else:
            result[key] = value
    return result
