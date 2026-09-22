# ============================================================
# MiniSOC Detection Rules
# ============================================================

RULES = {
    "BRUTE_FORCE": {
        "title": "Repeated Authentication Failures",
        "severity": "HIGH",
    },

    "PORT_SCAN": {
        "title": "Port Scanning Activity",
        "severity": "MEDIUM",
    },

    "MALWARE": {
        "title": "Malware Detection",
        "severity": "CRITICAL",
    },

    "SUSPICIOUS_LOGIN": {
        "title": "Suspicious Login",
        "severity": "HIGH",
    },

    "PRIV_ESC": {
        "title": "Privilege Escalation",
        "severity": "CRITICAL",
    },
}