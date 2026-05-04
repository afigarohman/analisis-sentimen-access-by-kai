from __future__ import annotations


ASPECTS: list[str] = ["Sistem", "Login", "Pembayaran", "UI/UX", "Performa", "Lainnya"]


def classify_aspect(text: str) -> str:
    """
    Simple rule-based aspect classifier.

    Category mapping:
    - Login: "login", "masuk"
    - Sistem: "error", "bug", "gagal", "crash"
    - Pembayaran: "bayar", "pembayaran"
    - Performa: "lemot", "lambat"
    - UI/UX: "ui", "tampilan", "layout", "menu", ...
    - Lainnya: default
    """

    t = (text or "").lower()

    # Priority order matters when multiple cues exist.
    login_cues = [
        "login",
        "masuk",
        "sign in",
        "signin",
        "daftar",
        "akun",
        "password",
        "username",
    ]

    system_cues = [
        "error",
        "bug",
        "gagal",
        "crash",
        "crashing",
        "tidak bisa",
        "tidak dapat",
        "server",
        "timeout",
        "server down",
    ]

    payment_cues = [
        "bayar",
        "pembayaran",
        "payment",
        "top up",
        "topup",
        "refund",
        "pengembalian",
        "transfer",
        "voucher",
        "kupon",
    ]

    ui_cues = [
        "ui",
        "tampilan",
        "layout",
        "menu",
        "button",
        "ikon",
        "design",
        "desain",
        "theme",
        "tema",
        "berantakan",
        "susah dibaca",
    ]

    performance_cues = [
        "lemot",
        "lambat",
        "slow",
        "loading",
        "nge-lag",
        "ngelag",
        "lag",
        "buffer",
        "respon lambat",
        "macet",
        "freeze",
    ]

    if any(c in t for c in login_cues):
        return "Login"
    if any(c in t for c in system_cues):
        return "Sistem"
    if any(c in t for c in payment_cues):
        return "Pembayaran"
    if any(c in t for c in ui_cues):
        return "UI/UX"
    if any(c in t for c in performance_cues):
        return "Performa"
    return "Lainnya"

