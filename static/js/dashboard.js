/* ============================================================
   MINISOC DASHBOARD
   ============================================================ */

(function () {

    "use strict";


    /* --------------------------------------------------------
       HELPERS
       -------------------------------------------------------- */

    function getElement(id) {
        return document.getElementById(id);
    }


    function setText(id, value) {

        const element = getElement(id);

        if (element) {
            element.textContent = value ?? 0;
        }
    }


    function escapeHtml(value) {

        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    function severityClass(severity) {

        return String(severity || "")
            .toLowerCase();
    }


    /* --------------------------------------------------------
       SEVERITY BAR
       -------------------------------------------------------- */

    function updateSeverityBar(
        barId,
        countId,
        value,
        total
    ) {

        setText(countId, value);

        const bar = getElement(barId);

        if (!bar) {
            return;
        }

        let percentage = 0;

        if (total > 0) {
            percentage = (value / total) * 100;
        }

        percentage = Math.min(
            Math.max(percentage, 0),
            100
        );

        bar.style.width = `${percentage}%`;
    }


    /* --------------------------------------------------------
       RECENT EVENTS
       -------------------------------------------------------- */

    function updateRecentEvents(events) {

        const body = getElement(
            "recent-events-body"
        );

        if (!body) {
            return;
        }


        if (!events || events.length === 0) {

            body.innerHTML = `
                <tr>
                    <td colspan="5">
                        <div class="soc-empty-state">
                            No security events recorded
                        </div>
                    </td>
                </tr>
            `;

            return;
        }


        body.innerHTML = events.map(
            event => {

                const severity =
                    severityClass(
                        event.severity
                    );


                return `
                    <tr>

                        <td>
                            ${escapeHtml(
                                event.timestamp
                            )}
                        </td>

                        <td>
                            ${escapeHtml(
                                event.source_ip
                            )}
                        </td>

                        <td>
                            ${escapeHtml(
                                event.event_type
                            )}
                        </td>

                        <td>

                            <span
                                class="soc-severity-badge ${severity}"
                            >
                                ${escapeHtml(
                                    event.severity
                                )}
                            </span>

                        </td>

                        <td>
                            ${escapeHtml(
                                event.status
                            )}
                        </td>

                    </tr>
                `;
            }
        ).join("");
    }


    /* --------------------------------------------------------
       LOAD DASHBOARD DATA
       -------------------------------------------------------- */

    async function loadDashboardData() {

        try {

            const response = await fetch(
                "/api/dashboard-data",
                {
                    method: "GET",
                    cache: "no-store"
                }
            );


            if (!response.ok) {
                throw new Error(
                    `Dashboard API returned ${response.status}`
                );
            }


            const data =
                await response.json();


            /* ------------------------------------------------
               KPI VALUES
               ------------------------------------------------ */

            setText(
                "total-events",
                data.total_events
            );

            setText(
                "open-alerts",
                data.open_alerts
            );

            setText(
                "critical-events",
                data.critical_events
            );

            setText(
                "source-ips",
                data.source_ips
            );


            /* ------------------------------------------------
               DETECTION ENGINE
               ------------------------------------------------ */

            setText(
                "analyzed-events",
                data.analyzed_events
            );

            setText(
                "total-alerts",
                data.total_alerts
            );


            /* ------------------------------------------------
               SEVERITY
               ------------------------------------------------ */

            const totalEvents =
                Number(data.total_events) || 0;


            updateSeverityBar(
                "critical-bar",
                "critical-count",
                Number(data.critical_events) || 0,
                totalEvents
            );


            updateSeverityBar(
                "high-bar",
                "high-count",
                Number(data.high_events) || 0,
                totalEvents
            );


            updateSeverityBar(
                "medium-bar",
                "medium-count",
                Number(data.medium_events) || 0,
                totalEvents
            );


            updateSeverityBar(
                "low-bar",
                "low-count",
                Number(data.low_events) || 0,
                totalEvents
            );


            /* ------------------------------------------------
               RECENT EVENTS
               ------------------------------------------------ */

            updateRecentEvents(
                data.recent_events || []
            );


            /* ------------------------------------------------
               GLOBE COUNTERS
               ------------------------------------------------ */

            setText(
                "globe-event-count",
                data.total_events
            );


            const threatCount =
                (Number(data.critical_events) || 0) +
                (Number(data.high_events) || 0);


            setText(
                "globe-threat-count",
                threatCount
            );


            const detail =
                getElement(
                    "globe-threat-detail"
                );


            if (detail) {

                if (threatCount > 0) {

                    detail.textContent =
                        `${threatCount} active threat event(s)`;

                } else {

                    detail.textContent =
                        "Monitoring Indian telemetry";

                }

            }


        } catch (error) {

            console.error(
                "MiniSOC dashboard update failed:",
                error
            );

        }

    }


    /* --------------------------------------------------------
       INITIAL LOAD
       -------------------------------------------------------- */

    loadDashboardData();


    /* --------------------------------------------------------
       LIVE REFRESH
       -------------------------------------------------------- */

    setInterval(
        loadDashboardData,
        5000
    );


})();