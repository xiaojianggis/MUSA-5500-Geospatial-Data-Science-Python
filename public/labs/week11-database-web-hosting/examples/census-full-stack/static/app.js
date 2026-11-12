/* Local scope avoids collisions with browser globals (for example window.location). */
(() => {
'use strict';
const $ = selector => document.querySelector(selector);
const statusElement = $('#status');
if (typeof L === 'undefined') {
  statusElement.textContent = 'Map library failed to load. Allow unpkg.com through your network, then reload.';
  return;
}
const map = L.map('map').setView([40.9, -77.5], 7);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>', maxZoom:19
}).on('tileerror', () => { $('#map-status').textContent = 'OpenStreetMap tiles failed to load. Check internet access; tract layers can still display.'; }).addTo(map);
const states = '01 Alabama|02 Alaska|04 Arizona|05 Arkansas|06 California|08 Colorado|09 Connecticut|10 Delaware|11 District of Columbia|12 Florida|13 Georgia|15 Hawaii|16 Idaho|17 Illinois|18 Indiana|19 Iowa|20 Kansas|21 Kentucky|22 Louisiana|23 Maine|24 Maryland|25 Massachusetts|26 Michigan|27 Minnesota|28 Mississippi|29 Missouri|30 Montana|31 Nebraska|32 Nevada|33 New Hampshire|34 New Jersey|35 New Mexico|36 New York|37 North Carolina|38 North Dakota|39 Ohio|40 Oklahoma|41 Oregon|42 Pennsylvania|44 Rhode Island|45 South Carolina|46 South Dakota|47 Tennessee|48 Texas|49 Utah|50 Vermont|51 Virginia|53 Washington|54 West Virginia|55 Wisconsin|56 Wyoming|72 Puerto Rico';
for (const state of states.split('|')) $('#state').add(new Option(state.slice(3), state.slice(0,2)));
$('#state').value = '42';
const colors = ['#eff3ff','#bdd7e7','#6baed6','#3182bd','#08519c'];
const breaks = {population:[0,1000,2500,5000,7500], income:[0,50000,75000,100000,150000], poverty:[0,10,20,30,40], home_value:[0,150000,250000,400000,600000]};
let config, tractLayer, currentData, selectedTract, loadVersion = 0, countiesVersion = 0;
const polygons = new Map();
async function jsonRequest(url, options) {
  const response = await fetch(url, options);
  let data;
  try { data = await response.json(); } catch { throw new Error('Expected JSON from the local API. Open the Uvicorn URL, not a static HTML file.'); }
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : `Request failed (${response.status}). Check the API parameters.`);
  return data;
}
function number(value, variable, topcoded = false) {
  if (value === null || value === undefined) return 'No data';
  const formatted = variable === 'poverty' ? `${value.toFixed(1)}%` :
    (['income','home_value'].includes(variable) ? '$' : '') + value.toLocaleString(undefined, {maximumFractionDigits:0});
  return formatted + (topcoded ? '+' : '');
}
function color(value, variable) {
  if (value === null || value === undefined) return '#c7ccd1';
  let bin = 0;
  breaks[variable].forEach((threshold, i) => { if (value >= threshold) bin = i; });
  return colors[bin];
}
function legend(variable) {
  $('#legend-title').textContent = `${config.variables[variable].label} · 2020–2024 ACS`;
  $('#legend').replaceChildren();
  [...breaks[variable], null].forEach((threshold, i) => {
    const item = document.createElement('span');
    const swatch = document.createElement('span');
    swatch.className = 'swatch'; swatch.style.background = threshold === null ? '#c7ccd1' : colors[i];
    const next = breaks[variable][i+1];
    const text = threshold === null ? 'No data' : next === undefined ? `${number(threshold,variable)}+` : `${number(threshold,variable)} to <${number(next,variable)}`;
    item.append(swatch, text); $('#legend').append(item);
  });
}
function popup(feature) {
  const p = feature.properties;
  const box = document.createElement('div');
  const heading = document.createElement('strong'); heading.textContent = `Tract ${p.geoid}`; box.append(heading);
  for (const [key, spec] of Object.entries(config.variables)) {
    const metric = p.metrics[key], line = document.createElement('p');
    line.textContent = `${spec.label}: ${number(metric.value,key,metric.topcoded)}`;
    if (spec.moe && metric.value !== null && metric.moe !== null && !metric.topcoded) line.textContent += ` (90% MOE ±${number(metric.moe,key)})`;
    if (key === 'poverty') line.textContent += `; ${number(metric.numerator,'population')} below poverty / ${number(metric.denominator,'population')} with poverty status determined. Rate MOE not calculated.`;
    box.append(line);
  }
  const note = document.createElement('small'); note.textContent = 'Whole-tract estimates for the selected county. + denotes an upper-coded estimate. ACS 2020–2024.'; box.append(note);
  return box;
}
function selectTract(polygon, zoom = false) {
  if (selectedTract) tractLayer.resetStyle(selectedTract);
  selectedTract = polygon;
  polygon.setStyle({color:'#f07818',weight:4,fillOpacity:0.8}); polygon.bringToFront();
  if (zoom) {
    map.fitBounds(polygon.getBounds(), {padding:[25,25],maxZoom:14});
    $('#map').scrollIntoView({behavior:'smooth',block:'center'});
  }
  polygon.openPopup();
}
function table(data) {
  $('#tract-table').replaceChildren();
  $('#table-title').textContent = `${data.county_name}: ${data.features.length} census tracts`;
  for (const f of data.features) {
    const row = document.createElement('tr'), name = document.createElement('td');
    const button = document.createElement('button'); button.className = 'tract-link'; button.textContent = f.properties.geoid;
    button.addEventListener('click', () => selectTract(polygons.get(f.properties.geoid), true)); name.append(button); row.append(name);
    for (const key of Object.keys(config.variables)) {
      const cell = document.createElement('td'), metric = f.properties.metrics[key];
      cell.textContent = number(metric.value,key,metric.topcoded); row.append(cell);
    }
    $('#tract-table').append(row);
  }
}
async function loadCounty() {
  const countyId = $('#prepared-county').value;
  if (!countyId) return;
  const version = ++loadVersion;
  statusElement.textContent = 'Loading prepared Census tracts…';
  const url = `/api/tracts?${new URLSearchParams({county_id:countyId,variable:$('#variable').value})}`;
  try {
    const data = await jsonRequest(url);
    if (version !== loadVersion) return;
    const changedCounty = currentData?.county_id !== data.county_id;
    if (tractLayer) map.removeLayer(tractLayer);
    selectedTract = null; polygons.clear();
    tractLayer = L.geoJSON(data, {
      style:f => ({color:'#3b526a',weight:1.2,fillOpacity:0.72,fillColor:color(f.properties.value,data.variable)}),
      onEachFeature:(f,polygon) => {
        polygons.set(f.properties.geoid,polygon);
        polygon.bindTooltip(`Tract ${f.properties.geoid}: ${number(f.properties.value,data.variable,f.properties.topcoded)}`);
        polygon.bindPopup(popup(f), {maxWidth:350});
        polygon.on('click', () => selectTract(polygon));
      }
    }).addTo(map);
    if (changedCounty) map.fitBounds(tractLayer.getBounds(), {padding:[24,24]});
    currentData = data;
    legend(data.variable); table(data);
    const downloadParams = new URLSearchParams({county_id:countyId, format:'geojson'});
    $('#download').href = `/api/dataset?${downloadParams}`; $('#download').hidden = false;
    downloadParams.set('format','csv');
    $('#download-csv').href = `/api/dataset?${downloadParams}`; $('#download-csv').hidden = false;
    const valid = data.features.filter(f => f.properties.value !== null).length;
    statusElement.textContent = `${data.county_name}: ${valid} of ${data.features.length} tracts have this estimate. Click a tract for details.`;
    $('#county-info').textContent = `Prepared ${new Date(data.prepared_at).toLocaleString()}. Census tract polygons and tract estimates only. County name selects the area; colors represent tract estimates, not county totals.`;
  } catch(error) {
    if (version !== loadVersion) return;
    // Clear the previous county so a failed selection cannot leave a misleading map.
    if (tractLayer) map.removeLayer(tractLayer);
    currentData = null; polygons.clear(); $('#tract-table').replaceChildren(); $('#legend').replaceChildren();
    $('#download').hidden = true; $('#download-csv').hidden = true;
    $('#legend-title').textContent = 'Tract data unavailable'; $('#county-info').textContent = '';
    statusElement.textContent = error.message;
  }
}
const stateLabel = countyId => states.split('|').find(s => s.slice(0,2) === countyId.slice(0,2))?.slice(3) || countyId.slice(0,2);
async function refreshCounties(preferred) {
  const saved = await jsonRequest('/api/prepared-counties');
  const previous = preferred || $('#prepared-county').value || '42043';
  $('#prepared-county').replaceChildren();
  saved.forEach(c => $('#prepared-county').add(new Option(`${c.name} · ${stateLabel(c.county_id)} · ${c.tract_count} tracts`,c.county_id)));
  $('#prepared-county').disabled = !saved.length; $('#variable').disabled = !saved.length;
  if (saved.some(c => c.county_id === previous)) $('#prepared-county').value = previous;
  if (saved.length) await loadCounty();
  else $('#prepared-county').add(new Option('No county tract datasets prepared yet',''));
}
async function loadCounties() {
  const version = ++countiesVersion;
  const state = $('#state').value;
  $('#prepare').disabled = true; $('#county').disabled = true;
  $('#county').replaceChildren(new Option('Loading county names…',''));
  $('#county-status').textContent = 'Loading counties for this state…';
  try {
    const counties = await jsonRequest(`/api/counties?${new URLSearchParams({state})}`);
    if (version !== countiesVersion) return;
    $('#county').replaceChildren();
    counties.forEach(c => $('#county').add(new Option(`${c.name} (${c.county_id})`,c.county_id)));
    if (state === '42' && counties.some(c => c.county_id === '42043')) $('#county').value = '42043';
    $('#county').disabled = !counties.length; $('#prepare').disabled = !counties.length;
    $('#county-status').textContent = counties.length ? `${counties.length} counties / county equivalents available.` : 'No counties available for this state.';
  } catch(error) {
    if (version !== countiesVersion) return;
    $('#county').replaceChildren(new Option('County list unavailable',''));
    $('#county-status').textContent = `${error.message} Use Reload county list to retry.`;
  }
}
$('#state').addEventListener('change',loadCounties);
$('#reload-counties').addEventListener('click',loadCounties);
$('#prepare').addEventListener('click', async () => {
  const countyId = $('#county').value;
  $('#prepare').disabled = true; $('#reload-counties').disabled = true; $('#state').disabled = true; $('#county').disabled = true;
  $('#prepare-status').textContent = 'Preparing census tract boundaries and tract-level ACS estimates… This may take a few minutes on the first download.';
  try {
    const result = await jsonRequest('/api/prepare',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({county_id:countyId})});
    $('#prepare-status').textContent = `Prepared ${result.name}: ${result.tract_count} census tract records. GeoJSON and CSV saved locally.`;
    await refreshCounties(result.county_id);
  } catch(error) { $('#prepare-status').textContent = error.message; }
  finally { $('#prepare').disabled = false; $('#reload-counties').disabled = false; $('#state').disabled = false; $('#county').disabled = false; }
});
$('#prepared-county').addEventListener('change',loadCounty);
$('#variable').addEventListener('change',loadCounty);
(async () => {
  try {
    config = await jsonRequest('/api/config');
    Object.entries(config.variables).forEach(([key,spec]) => $('#variable').add(new Option(spec.label,key)));
    $('#variable').value = 'income';
    await Promise.all([refreshCounties(), loadCounties()]);
  } catch(error) { statusElement.textContent = error.message; }
})();
})();
