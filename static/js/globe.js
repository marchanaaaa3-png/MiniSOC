"use strict";

(function () {

    let globe = null;
    let globeContainer = null;

    const REFRESH_INTERVAL = 5000;


    /* =========================================================
       INDIA MONITORING LOCATIONS
       ========================================================= */

    const IP_LOCATIONS = {

        "203.0.113.44": {
            lat: 19.0760,
            lng: 72.8777,
            city: "Mumbai",
            state: "Maharashtra"
        },

        "198.51.100.23": {
            lat: 28.6139,
            lng: 77.2090,
            city: "New Delhi",
            state: "Delhi"
        },

        "192.0.2.55": {
            lat: 12.9716,
            lng: 77.5946,
            city: "Bengaluru",
            state: "Karnataka"
        },

        "10.0.0.24": {
            lat: 17.3850,
            lng: 78.4867,
            city: "Hyderabad",
            state: "Telangana"
        },

        "10.0.0.10": {
            lat: 17.3850,
            lng: 78.4867,
            city: "MiniSOC Target",
            state: "Telangana"
        },

        "10.0.0.20": {
            lat: 17.3850,
            lng: 78.4867,
            city: "Internal Server",
            state: "Telangana"
        },

        "10.0.0.30": {
            lat: 13.0827,
            lng: 80.2707,
            city: "Chennai",
            state: "Tamil Nadu"
        },

        "10.0.0.31": {
            lat: 18.5204,
            lng: 73.8567,
            city: "Pune",
            state: "Maharashtra"
        },

        "10.0.0.32": {
            lat: 22.5726,
            lng: 88.3639,
            city: "Kolkata",
            state: "West Bengal"
        },

        "10.0.0.33": {
            lat: 23.0225,
            lng: 72.5714,
            city: "Ahmedabad",
            state: "Gujarat"
        }

    };


    /* =========================================================
       SEVERITY
       ========================================================= */

    const SEVERITY = {

        CRITICAL: {
            color: "#d7e1e7",
            radius: 0.75,
            altitude: 0.14
        },

        HIGH: {
            color: "#9db6c6",
            radius: 0.62,
            altitude: 0.11
        },

        MEDIUM: {
            color: "#708898",
            radius: 0.48,
            altitude: 0.08
        },

        LOW: {
            color: "#4f6573",
            radius: 0.34,
            altitude: 0.055
        }

    };


    /* =========================================================
       LOAD GLOBE.GL
       ========================================================= */

    function loadGlobeLibrary() {

        return new Promise(function (resolve, reject) {

            if (window.Globe) {
                resolve();
                return;
            }

            const script =
                document.createElement("script");

            script.src =
                "https://unpkg.com/globe.gl@2.45.0/dist/globe.gl.min.js";

            script.onload = function () {

                if (window.Globe) {
                    resolve();
                } else {
                    reject(
                        new Error(
                            "Globe.gl is unavailable."
                        )
                    );
                }

            };

            script.onerror = function () {

                reject(
                    new Error(
                        "Unable to load Globe.gl."
                    )
                );

            };

            document.head.appendChild(script);

        });

    }


    /* =========================================================
       LOCATION LOOKUP
       ========================================================= */

    function getLocation(ip) {

        return IP_LOCATIONS[ip] || null;

    }


    /* =========================================================
       SEVERITY LOOKUP
       ========================================================= */

    function getSeverityConfig(severity) {

        const level =
            String(
                severity || "LOW"
            ).toUpperCase();

        return (
            SEVERITY[level] ||
            SEVERITY.LOW
        );

    }


    /* =========================================================
       CREATE GLOBE
       ========================================================= */

    function createGlobe() {

        globeContainer =
            document.getElementById(
                "globe-canvas"
            );

        if (!globeContainer) {
            return;
        }

        globeContainer.innerHTML = "";

        const width =
            globeContainer.clientWidth || 800;

        const height =
            globeContainer.clientHeight || 410;


        globe =
            Globe()(globeContainer);


        globe
            .width(width)
            .height(height)

            .backgroundColor(
                "rgba(0,0,0,0)"
            )

            .globeImageUrl(
                "https://unpkg.com/three-globe@2.41.0/example/img/earth-night.jpg"
            )

            .bumpImageUrl(
                "https://unpkg.com/three-globe@2.41.0/example/img/earth-topology.png"
            )

            .showAtmosphere(true)

            .atmosphereColor(
                "#4c86a5"
            )

            .atmosphereAltitude(
                0.07
            );


        /* No latitude/longitude grid */

        globe.showGraticules(false);


        /* =====================================================
           MARKERS
           ===================================================== */

        globe
            .pointLat("lat")
            .pointLng("lng")
            .pointAltitude("altitude")
            .pointRadius("radius")
            .pointColor("color")
            .pointResolution(16)
            .pointsMerge(false)


            .pointLabel(function (point) {

                return `
                    <div style="
                        padding:8px 10px;
                        background:#071017;
                        border:1px solid #304858;
                        color:#b8c7d0;
                        font-family:Arial,sans-serif;
                        font-size:11px;
                        line-height:1.5;
                    ">

                        <strong>
                            ${escapeHtml(point.city)}
                        </strong>

                        <br>

                        IP:
                        ${escapeHtml(point.ip)}

                        <br>

                        Event:
                        ${escapeHtml(point.event_type)}

                        <br>

                        Severity:
                        ${escapeHtml(point.severity)}

                    </div>
                `;

            })


            .onPointClick(function (point) {

                showThreatDetail(point);

            });


        /* =====================================================
           ATTACK / MONITORING ARCS
           ===================================================== */

        globe
            .arcStartLat("startLat")
            .arcStartLng("startLng")

            .arcEndLat("endLat")
            .arcEndLng("endLng")

            .arcColor("color")

            .arcAltitude("altitude")

            .arcStroke(0.45)

            .arcDashLength(0.45)

            .arcDashGap(1.2)

            .arcDashAnimateTime(1800);


        /* =====================================================
           CONTROLS
           ===================================================== */

        const controls =
            globe.controls();

        controls.autoRotate = true;

        controls.autoRotateSpeed = 0.25;

        controls.enableZoom = true;

        controls.enablePan = false;

        controls.minDistance = 180;

        controls.maxDistance = 330;


        /* Start focused around India */

        globe.pointOfView(
            {
                lat: 21,
                lng: 78,
                altitude: 2.0
            },
            0
        );


        window.addEventListener(
            "resize",
            resizeGlobe
        );


        updateGlobeData();

    }


    /* =========================================================
       RESIZE
       ========================================================= */

    function resizeGlobe() {

        if (!globe || !globeContainer) {
            return;
        }

        const width =
            globeContainer.clientWidth;

        const height =
            globeContainer.clientHeight;

        if (!width || !height) {
            return;
        }

        globe
            .width(width)
            .height(height);

    }


    /* =========================================================
       GET LIVE EVENTS
       ========================================================= */

    async function updateGlobeData() {

        if (!globe) {
            return;
        }

        try {

            const response =
                await fetch(
                    "/api/dashboard-data",
                    {
                        cache: "no-store"
                    }
                );

            if (!response.ok) {
                throw new Error(
                    "Dashboard API returned " +
                    response.status
                );
            }

            const data =
                await response.json();

            const events =
                data.recent_events || [];

            updateGlobe(events);

            updateThreatCount(data);

        } catch (error) {

            console.error(
                "MiniSOC globe update failed:",
                error
            );

        }

    }


    /* =========================================================
       UPDATE MARKERS + ARCS
       ========================================================= */

    function updateGlobe(events) {

        const points = [];

        const arcs = [];


        events.forEach(function (event) {

            const source =
                getLocation(
                    event.source_ip
                );

            const destination =
                getLocation(
                    event.destination_ip
                );


            /*
             * Unknown locations are ignored.
             * We never invent coordinates.
             */

            if (!source) {
                return;
            }


            const config =
                getSeverityConfig(
                    event.severity
                );


            /* -----------------------------------------------
               SOURCE
            ------------------------------------------------ */

            points.push({

                lat: source.lat,

                lng: source.lng,

                altitude: config.altitude,

                radius: config.radius,

                color: config.color,

                ip: event.source_ip,

                city: source.city,

                state: source.state,

                severity: event.severity,

                event_type: event.event_type,

                timestamp: event.timestamp

            });


            /* -----------------------------------------------
               DESTINATION
            ------------------------------------------------ */

            if (destination) {

                points.push({

                    lat: destination.lat,

                    lng: destination.lng,

                    altitude:
                        Math.max(
                            0.03,
                            config.altitude * 0.5
                        ),

                    radius:
                        Math.max(
                            0.22,
                            config.radius * 0.6
                        ),

                    color: "#536c7b",

                    ip: event.destination_ip,

                    city: destination.city,

                    state: destination.state,

                    severity: event.severity,

                    event_type: "DESTINATION",

                    timestamp: event.timestamp

                });


                /* -------------------------------------------
                   SOURCE → DESTINATION
                -------------------------------------------- */

                arcs.push({

                    startLat:
                        source.lat,

                    startLng:
                        source.lng,

                    endLat:
                        destination.lat,

                    endLng:
                        destination.lng,

                    color:
                        config.color,

                    altitude:
                        Math.max(
                            0.07,
                            config.altitude
                        )

                });

            }

        });


        globe.pointsData(
            points
        );

        globe.arcsData(
            arcs
        );

    }


    /* =========================================================
       THREAT COUNT
       ========================================================= */

    function updateThreatCount(data) {

        const element =
            document.getElementById(
                "globe-threat-count"
            );

        if (!element) {
            return;
        }

        const high =
            Number(
                data.high_events || 0
            );

        const critical =
            Number(
                data.critical_events || 0
            );

        element.textContent =
            high + critical;

    }


    /* =========================================================
       THREAT DETAILS
       ========================================================= */

    function showThreatDetail(point) {

        const detail =
            document.getElementById(
                "globe-threat-detail"
            );

        if (!detail) {
            return;
        }

        detail.innerHTML = `

            <strong>
                ${escapeHtml(point.event_type)}
            </strong>

            <br>

            ${escapeHtml(point.city)},
            ${escapeHtml(point.state)}

            ·

            ${escapeHtml(point.severity)}

            <br>

            ${escapeHtml(point.ip)}

        `;

        detail.classList.add(
            "active"
        );


        setTimeout(function () {

            detail.classList.remove(
                "active"
            );

        }, 5000);

    }


    /* =========================================================
       ESCAPE HTML
       ========================================================= */

    function escapeHtml(value) {

        return String(
            value === null ||
            value === undefined
                ? ""
                : value
        )
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");

    }


    /* =========================================================
       INITIALIZE
       ========================================================= */

    document.addEventListener(
        "DOMContentLoaded",
        async function () {

            try {

                await loadGlobeLibrary();

                createGlobe();


                setInterval(
                    updateGlobeData,
                    REFRESH_INTERVAL
                );

            } catch (error) {

                console.error(
                    "MiniSOC globe initialization failed:",
                    error
                );

            }

        }
    );

})();