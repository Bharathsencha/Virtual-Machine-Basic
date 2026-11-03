import { api } from "./api.js";
/* Copyright (C) 2026 Bharathsencha | SPDX-License-Identifier: GPL-3.0-only */
const $ = s => document.querySelector(s);
let busy = false;
function cell(row, text, cls) { const td=document.createElement('td'); td.textContent=text; if(cls) td.className=cls; row.append(td); return td; }
async function refresh() {
  try {
    const [vms, host] = await Promise.all([api('/vms'),api('/system/stats')]);
    $('#summary').replaceChildren();
    for (const [label,count] of [['Total machines',vms.length],['Running',vms.filter(v=>v.status==='running').length],['Stopped',vms.filter(v=>v.status==='stopped').length]]) {
      const card=document.createElement('div'); card.className='card'; const span=document.createElement('span');span.textContent=label;const strong=document.createElement('strong');strong.textContent=count;card.append(span,strong);$('#summary').append(card);
    }
    $('#host').textContent=`CPU ${host.cpu_percent}% / Memory ${host.memory_percent}% / Disk free ${(host.disk_free_bytes/1024**3).toFixed(1)} GB`;
    $('#warning').textContent=[host.warning, !host.qemu_available ? 'QEMU executable missing.' : '', !host.qemu_img_available ? 'qemu-img missing.' : ''].filter(Boolean).join(' ');
    $('#vms').replaceChildren();
    if(!vms.length) { const row=document.createElement('tr'); const td=cell(row,'No virtual machines. Create one to begin.');td.colSpan=7;$('#vms').append(row); }
    for(const vm of vms) {
      const row=document.createElement('tr');cell(row,vm.name);cell(row,vm.status,'badge '+vm.status);cell(row,vm.ram_mb+' MB');cell(row,vm.cpus);cell(row,vm.disk_gb+' GB');cell(row,vm.uptime_seconds===null ? '-' : vm.uptime_seconds+' s');const actions=cell(row,'');
      for(const action of (vm.status==='running' ? ['shutdown','stop','restart','console'] : ['start','delete','console'])) {
        const button=document.createElement('button');button.textContent=({shutdown:'Shut down',stop:'Force stop',restart:'Reset',console:'Console',start:'Start',delete:'Delete'})[action];button.disabled=busy;
        button.onclick=async()=>{
          if(action==='console') { $('#console-text').textContent=vm.console_instructions;$('#console-dialog').showModal();return; }
          if(['delete','stop','restart'].includes(action) && !confirm(`${action==='delete' ? 'Permanently delete this VM and its managed disk' : action==='stop' ? 'Force stop this VM (unsaved data may be lost)' : 'Reset this VM (unsaved data may be lost)'}?`)) return;
          busy=true;button.disabled=true;
          try {await api(`/vms/${vm.id}${action==='delete'?'': '/'+action}${['delete','stop','restart'].includes(action)?'?confirm=true':''}`,action==='delete'?'DELETE':'POST');$('#message').textContent=action==='shutdown'?'Shutdown requested. Guest ACPI support is required; wait for it to stop.':'Action completed.';}catch(e){$('#message').textContent=e.message;}finally{busy=false;await refresh();}
        };actions.append(button);
      }$('#vms').append(row);
    }
  } catch(e) {$('#message').textContent=e.message;}
}
$('#open-create').onclick=()=>$('#create-dialog').showModal();$('#cancel-create').onclick=()=>$('#create-dialog').close();$('#close-console').onclick=()=>$('#console-dialog').close();
$('#create-form').onsubmit=async event=>{event.preventDefault();const button=event.submitter;button.disabled=true;const data=Object.fromEntries(new FormData(event.target));for(const key of ['ram_mb','cpus','disk_gb'])data[key]=Number(data[key]);try{await api('/vms','POST',data);$('#create-dialog').close();$('#message').textContent='VM created.';await refresh();}catch(e){alert(e.message);}finally{button.disabled=false;}};
refresh();setInterval(()=>{if(!busy)refresh();},5000);
