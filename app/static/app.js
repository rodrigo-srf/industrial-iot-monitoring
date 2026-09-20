const labels={normal:"Normal",warning:"Advertência",critical:"Crítico"};
const fmt=n=>Number(n).toLocaleString("pt-BR",{maximumFractionDigits:1});
const time=v=>new Date(v).toLocaleString("pt-BR");

function renderMachines(items){
  const root=document.querySelector("#machines");
  if(!items.length){root.innerHTML='<p class="empty">Aguardando telemetria...</p>';return;}
  root.innerHTML=items.map(m=>`<article class="machine ${m.status}">
    <div class="machine-head"><strong>${m.machine_id}</strong><span class="badge">${labels[m.status]}</span></div>
    <div class="metrics">
      <div class="metric"><span>Temperatura</span><b>${fmt(m.temperature_c)} °C</b></div>
      <div class="metric"><span>Vibração</span><b>${fmt(m.vibration_mm_s)} mm/s</b></div>
      <div class="metric"><span>Corrente</span><b>${fmt(m.current_a)} A</b></div>
      <div class="metric"><span>Rotação</span><b>${fmt(m.rpm)} RPM</b></div>
    </div><div class="timestamp">Atualizado em ${time(m.recorded_at)}</div></article>`).join("");
  document.querySelector("#total-machines").textContent=items.length;
  ["normal","warning","critical"].forEach(s=>document.querySelector(`#${s}-machines`).textContent=items.filter(m=>m.status===s).length);
}

function renderAlarms(items){
  const root=document.querySelector("#alarms");
  if(!items.length){root.innerHTML='<tr><td colspan="4">Nenhum alarme registrado.</td></tr>';return;}
  root.innerHTML=items.map(a=>`<tr><td>${time(a.recorded_at)}</td><td><strong>${a.machine_id}</strong></td><td class="level ${a.status}">${labels[a.status]}</td><td>${a.alarm_message}</td></tr>`).join("");
}

async function refresh(){
  const dot=document.querySelector("#connection-dot"),text=document.querySelector("#connection-text");
  try{
    const [health,machines,alarms]=await Promise.all([fetch("/api/health"),fetch("/api/machines"),fetch("/api/alarms?limit=15")]);
    if(!health.ok||!machines.ok||!alarms.ok)throw new Error();
    const h=await health.json(); renderMachines(await machines.json()); renderAlarms(await alarms.json());
    dot.style.background=h.mqtt==="connected"?"#38d996":"#f2ad4b";
    text.textContent=h.mqtt==="connected"?"MQTT conectado":"API online · MQTT desconectado";
  }catch(e){dot.style.background="#ef6363";text.textContent="Sem conexão com a API";}
}
refresh();setInterval(refresh,3000);
