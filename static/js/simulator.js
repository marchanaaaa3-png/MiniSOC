/* ============================================================
   MiniSOC Event Simulator
   ============================================================ */

"use strict";

document.addEventListener("DOMContentLoaded", function () {

    const scenarioSelect =
        document.getElementById("scenario");

    const sourceInput =
        document.getElementById("source_ip");

    const destinationInput =
        document.getElementById("destination_ip");

    const eventTypeInput =
        document.getElementById("event_type");

    const severityInput =
        document.getElementById("severity");

    const messageInput =
        document.getElementById("message");


    /*
     * Scenario information.
     * The actual event is saved by Flask into SQLite.
     */

    const scenarios = {

        normal: {
            source: "10.0.0.24",
            destination: "10.0.0.10",
            type: "NORMAL",
            severity: "LOW",
            message: "Normal network activity detected."
        },

        auth_failure: {
            source: "203.0.113.44",
            destination: "10.0.0.10",
            type: "AUTH_FAILURE",
            severity: "MEDIUM",
            message: "Multiple failed authentication attempts detected."
        },

        port_scan: {
            source: "198.51.100.23",
            destination: "10.0.0.10",
            type: "PORT_SCAN",
            severity: "MEDIUM",
            message: "Network reconnaissance and port scanning activity detected."
        },

        malware: {
            source: "198.51.100.23",
            destination: "10.0.0.20",
            type: "MALWARE",
            severity: "CRITICAL",
            message: "Potential malware activity detected."
        },

        suspicious_login: {
            source: "192.0.2.55",
            destination: "10.0.0.10",
            type: "SUSPICIOUS_LOGIN",
            severity: "HIGH",
            message: "Suspicious login activity detected."
        },

        priv_esc: {
            source: "10.0.0.24",
            destination: "10.0.0.10",
            type: "PRIV_ESC",
            severity: "CRITICAL",
            message: "Possible privilege escalation activity detected."
        }
    };


    function updateScenario() {

        if (!scenarioSelect) {
            return;
        }

        const selected =
            scenarioSelect.value;

        const scenario =
            scenarios[selected];

        if (!scenario) {
            return;
        }

        if (sourceInput) {
            sourceInput.value =
                scenario.source;
        }

        if (destinationInput) {
            destinationInput.value =
                scenario.destination;
        }

        if (eventTypeInput) {
            eventTypeInput.value =
                scenario.type;
        }

        if (severityInput) {
            severityInput.value =
                scenario.severity;
        }

        if (messageInput) {
            messageInput.value =
                scenario.message;
        }
    }


    if (scenarioSelect) {

        scenarioSelect.addEventListener(
            "change",
            updateScenario
        );

        updateScenario();
    }


    /*
     * Add a small visual loading state when
     * the simulator form is submitted.
     */

    const simulatorForm =
        document.querySelector(
            ".simulator-form"
        );

    if (simulatorForm) {

        simulatorForm.addEventListener(
            "submit",
            function () {

                const button =
                    simulatorForm.querySelector(
                        'button[type="submit"]'
                    );

                if (!button) {
                    return;
                }

                button.disabled = true;

                button.dataset.originalText =
                    button.textContent;

                button.textContent =
                    "Generating Event...";
            }
        );
    }

});