/* The browser sends parameters, never SQL. Each response is computed in Python. */
const map = L.map('map').setView([40.9, -77.5], 7);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors', maxZoom: 18
}).addTo(map);
const category = document.querySelector('#category');
const radius = document.querySelector('#radius');
const status = document.querySelector('#status');
const colors = ['#edf5ee', '#b5d9c6', '#64ac95', '#267966', '#114b42'];
let layer, marker, location, districtVersion = 0, queryVersion = 0, firstLoad = true;
async function getJSON(url) {
  const response = await fetch(url);
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : `Request failed (${response.status})`);
  return data;
}
async function loadDistricts() {
  const version = ++districtVersion;
  status.textContent = 'Querying district counts…';
  try {
    const data = await getJSON(`/api/districts?category=${encodeURIComponent(category.value)}`);
    if (version !== districtVersion) return;
    const maximum = Math.max(1, ...data.features.map(f => f.properties.sample_dots));
    const bin = value => Math.min(4, Math.floor(value / maximum * 5));
    const next = L.geoJSON(data, {
      style: f => ({color:'#48685c', weight:1, fillOpacity:0.65, fillColor:colors[bin(f.properties.sample_dots)]}),
      onEachFeature: (feature, polygon) => polygon.bindTooltip(`2015 district ${feature.properties.district_id}: ${feature.properties.sample_dots.toLocaleString()} sample dots`)
    });
    if (layer) map.removeLayer(layer);
    layer = next.addTo(map);
    if (firstLoad) { map.fitBounds(layer.getBounds()); firstLoad = false; }
    document.querySelector('#legend').replaceChildren();
    colors.forEach((color, i) => {
      const item = document.createElement('span');
      const swatch = document.createElement('span'); swatch.className='swatch'; swatch.style.background=color;
      item.append(swatch, `${Math.ceil(i * maximum / 5).toLocaleString()}–${(i === 4 ? maximum : Math.ceil((i+1)*maximum/5)-1).toLocaleString()}`);
      document.querySelector('#legend').append(item);
    });
    status.textContent = 'Districts ready. Choose a location inside Pennsylvania.';
  } catch (error) { if(version === districtVersion) status.textContent = `Unable to load districts: ${error.message}`; }
}
async function queryLocation(latlng) {
  location = latlng;
  const version = ++queryVersion;
  status.textContent = 'Python is running the radius query…';
  document.querySelector('#total').textContent = 'Querying…';
  document.querySelector('#counts').replaceChildren();
  document.querySelector('#location').textContent = '';
  const params = new URLSearchParams({lon:latlng.lng, lat:latlng.lat, radius_m:radius.value, category:category.value});
  const url = `/api/nearby?${params}`;
  document.querySelector('#request').href = url;
  if (marker) map.removeLayer(marker);
  marker = L.circle(latlng, {radius:Number(radius.value), color:'#c16822', fillOpacity:0.08}).addTo(map);
  try {
    const data = await getJSON(url);
    if (version !== queryVersion) return;
    document.querySelector('#total').textContent = `${data.sample_dots.toLocaleString()} sample dots`;
    document.querySelector('#location').textContent = `${(data.radius_m/1000).toFixed(1)} km around ${latlng.lat.toFixed(4)}, ${latlng.lng.toFixed(4)}`;
    for(const row of data.categories) {
      const item = document.createElement('li'); item.textContent=`${row.label}: ${row.sample_dots.toLocaleString()}`;
      document.querySelector('#counts').append(item);
    }
    status.textContent = 'Live database result received.';
  } catch(error) {
    if(version !== queryVersion) return;
    document.querySelector('#total').textContent='No query result';
    status.textContent=error.message;
  }
}
map.on('click', event => queryLocation(event.latlng));
category.addEventListener('change', async () => { await loadDistricts(); if(location) queryLocation(location); });
radius.addEventListener('change', () => { if(location) queryLocation(location); });
document.querySelector('#philly').addEventListener('click', () => {
  const point = L.latLng(39.9526,-75.1636); map.setView(point,11); queryLocation(point);
});
loadDistricts();
