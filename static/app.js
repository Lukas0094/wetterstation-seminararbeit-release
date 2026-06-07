async function getFullData() {
    await fetch("/api/full_data")
                .then(response => response.json())
                .then(data => {
                    console.log(data)

                    /* Stadt */
                    document.getElementById("city").textContent = (data.location && data.location.city) ? data.location.city : "Wetterstation"
                    
                    /* Aktuellste Wetterdaten */
                    if(data.latest) {
                        document.getElementById("daily_origin").textContent = `${data.latest.timestamp}`
                        document.getElementById("daily_temperature").textContent = `${data.latest.temp}°C`
                        document.getElementById("min_max_temperature").textContent = `${data.latest.min_temp}°C / ${data.latest.max_temp}°C`
                        document.getElementById("daily_humidity").textContent = `${data.latest.hum}%`
                        document.getElementById("min_max_humidity").textContent = `${data.latest.min_hum}% / ${data.latest.max_hum}%`
                        document.getElementById("daily_pressure").textContent = `${data.latest.pre} hPa`
                        document.getElementById("min_max_pressure").textContent = `${data.latest.min_pre} hPa / ${data.latest.max_pre} hPa`
                    } else {
                        document.getElementById("daily_origin").textContent = "Keine Daten verfügbar."
                    }

                    /* Letzte zwölf Stunden */
                    var hours = data.past_hours || []
                    var hoursContainer = document.getElementById("past_hours")
                    var hoursOuter = hoursContainer.parentElement

                    if(hours.length === 0) {
                        hoursContainer.textContent = "Keine stündlichen Daten vorhanden."
                        hoursOuter.style.background = "transparent";
                    } else {
                        hoursContainer.textContent = ""
                        hoursOuter.style.background = ""

                        for(let i = 1; i <= hours.length; i++) {
                            var dataset = hours[data.past_hours.length - i]
                            var div = document.querySelector(`#ph-${i}.sequence-element`)

                            if(!div) {
                                div = document.createElement("div")
                                div.classList.add("sequence-element")
                                div.id = `ph-${i}`
                                document.getElementById("past_hours").appendChild(div)

                                for(let j = 0; j < 4; j++) {
                                    div.appendChild(document.createElement("p"))
                                }
                            }

                            const paragraphs = div.querySelectorAll("p")
                            paragraphs[0].classList.add("bold")
                            paragraphs[0].textContent = `${dataset.hour}:00`
                            paragraphs[1].textContent = `${dataset.temp}°C`
                            paragraphs[2].textContent = `${dataset.hum}%`
                            paragraphs[3].textContent = `${dataset.pre} hPa`
                        }
                    }

                    /* Letzte sieben Tage */
                    var days = data.past_days || []
                    var daysContainer = document.getElementById("past_days")
                    var daysOuter = daysContainer.parentElement

                    if(days.length === 0) {
                        daysContainer.textContent = "Keine Daten für den 7-Tage-Verlauf vorhanden."
                        daysOuter.style.background = "transparent"
                    } else {
                        daysContainer.textContent = ""
                        daysOuter.style.background = ""

                        for(let i = 1; i <= days.length; i++) {
                            var dataset = data.past_days[days.length - i]
                            var div = document.querySelector(`#pd-${i}.sequence-element`)

                            if(!div) {
                                div = document.createElement("div")
                                div.classList.add("sequence-element")
                                div.id = `pd-${i}`
                                document.getElementById("past_days").appendChild(div)

                                div.appendChild(document.createElement("p"))
                                for(let j = 0; j < 6; j++) {
                                    var p = document.createElement("p")
                                    p.classList.add(j %2 == 0 ? "value-display-top" : "value-display-bottom")
                                    div.appendChild(p)
                                }
                            }

                            const paragraphs = div.querySelectorAll("p")

                            paragraphs[0].classList.add("bold")
                            paragraphs[0].textContent = `${dataset.date}`

                            paragraphs[1].textContent = `${dataset.avg_temp}°C`
                            paragraphs[2].textContent = `${dataset.min_temp}°C / ${dataset.max_temp}°C`

                            paragraphs[3].textContent = `${dataset.avg_hum}%`
                            paragraphs[4].textContent = `${dataset.min_hum}% / ${dataset.max_hum}%`

                            paragraphs[5].textContent = `${dataset.avg_pre} hPa`
                            paragraphs[6].textContent = `${dataset.min_pre} hPa / ${dataset.max_pre} hPa`
                        }
                    }

                    /* Raspberry Pi Informationen */
                    if(data.pi_info) {
                        var infos = data.pi_info
                        document.getElementById("cpu_info").textContent = `CPU - Temperatur / Last / Takt: ${infos.cpu_temp}°C / ${infos.cpu_load}% / ${infos.cpu_freq} Mhz`
                        document.getElementById("ram_info").textContent = `RAM - Benutzt / Frei: ${infos.ram_used} GB / ${infos.ram_total} GB`
                        document.getElementById("disk_info").textContent = `Festplatte - Benutzt / Frei: ${infos.disk_used} GB / ${infos.disk_total} GB`
                        document.getElementById("uptime_info").textContent = `Laufzeit: ${infos.uptime}`
                    }
                })
                .catch(err => console.error("Fehler beim Abrufen der Wetterdaten:", err))
}
getFullData()
setInterval(getFullData, 60 * 1 * 1000)

function scrollToElement(elementId) {
    const element = document.getElementById(elementId)
    element.scrollIntoView()
}