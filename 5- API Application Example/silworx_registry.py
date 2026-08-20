"""Windows registry scanner for installed SILworX versions."""

from __future__ import annotations

try:
    import winreg
except ImportError:  # pragma: no cover - non-Windows test environments
    winreg = None  # type: ignore[assignment]


def discover_silworx_versions() -> list[dict[str, str]]:
    """Discover installed SILworX versions via Windows Uninstall registry."""
    results: list[dict[str, str]] = []
    if winreg is None:
        return results

    roots = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ]
    seen: set[tuple[str, str]] = set()

    try:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    except Exception:
        return results

    for subkey in roots:
        try:
            key = winreg.OpenKey(reg, subkey)
            count = winreg.QueryInfoKey(key)[0]
        except Exception:
            continue

        for index in range(count):
            try:
                software_key_name = winreg.EnumKey(key, index)
                software_key = winreg.OpenKey(key, software_key_name)
                display_name = str(winreg.QueryValueEx(software_key, "DisplayName")[0])
                if "SILworX Version " not in display_name:
                    continue
                version = display_name.replace("SILworX Version ", "V").strip()
                try:
                    install_location = str(winreg.QueryValueEx(software_key, "InstallLocation")[0])
                except Exception:
                    install_location = ""
                signature = (version, install_location)
                if signature in seen:
                    continue
                seen.add(signature)
                results.append({"version": version, "path": install_location})
            except Exception:
                continue

    return results
