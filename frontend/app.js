/* Copyright (C) 2026 Bharathsencha | SPDX-License-Identifier: GPL-3.0-only */
import { api } from './api.js';
import { renderHost, renderMachines, renderDetails } from './render.js';

const $ = selector => document.querySelector(selector);
let machines = [];
let busy = false;
let refreshing = false;
let selectedId = null;

function message(text) {
  $('#message').textContent = text;
  $('#message').hidden = !text;
}

function render() {
  renderMachines(machines, $('#search').value, busy, performAction, openDetails);
  if ($('#details-dialog').open) {
    const vm = machines.find(machine => machine.id === selectedId);
    if (vm) renderDetails(vm, busy, performAction);
    else $('#details-dialog').close();
  }
}

function openDetails(vm) {
  selectedId = vm.id;
  renderDetails(vm, busy, performAction);
  if (!$('#details-dialog').open) $('#details-dialog').showModal();
}

async function refresh() {
  if (refreshing) return;
  refreshing = true;
  try {
    const [inventory, host] = await Promise.all([api('/vms'), api('/system/stats')]);
    machines = inventory;
    renderHost(host);
    render();
    $('#connection').replaceChildren(document.createTextNode('Host connected'));
    const address = document.createElement('span');
    address.textContent = location.host;
    $('#connection').append(address);
    $('#connection-dot').classList.add('online');
    $('#updated').textContent = `Updated ${new Date().toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'})}`;
  } catch (error) {
    message(`Could not refresh host: ${error.message}. Displayed data may be out of date.`);
    $('#connection').textContent = 'Host unavailable';
    $('#connection-dot').classList.remove('online');
  } finally {
    refreshing = false;
  }
}

async function performAction(vm, action) {
  if (busy) return;
  const confirmations = {
    delete: `Delete “${vm.name}” and its managed disk permanently? The original source image will be preserved.`,
    stop: `Force stop “${vm.name}”? Unsaved guest data may be lost.`,
    restart: `Reset “${vm.name}”? Unsaved guest data may be lost.`,
  };
  if (confirmations[action] && !confirm(confirmations[action])) return;
  busy = true;
  render();
  try {
    const destructive = Boolean(confirmations[action]);
    const path = `/vms/${vm.id}${action === 'delete' ? '' : '/' + action}${destructive ? '?confirm=true' : ''}`;
    await api(path, action === 'delete' ? 'DELETE' : 'POST');
    const updates = {start: 'started', stop: 'stopped', restart: 'reset', delete: 'deleted'};
    message(action === 'shutdown' ? `Shutdown requested for ${vm.name}. Waiting for the guest to power off.` : `${vm.name} ${updates[action]}.`);
  } catch (error) {
    message(error.message);
  } finally {
    busy = false;
    await refresh();
    render();
  }
}

function openCreate() {
  $('#create-error').hidden = true;
  $('#create-dialog').showModal();
}

$('#open-create').onclick = openCreate;
$('#empty-create').onclick = openCreate;
$('#cancel-create').onclick = () => $('#create-dialog').close();
$('#close-details').onclick = () => $('#details-dialog').close();
$('#search').oninput = render;
$('#image-type').onchange = event => {
  $('#image-help').textContent = event.target.value === 'iso'
    ? 'Use a prepared x86_64 ISO. The image stays attached on subsequent starts.'
    : 'Use a standalone BIOS bootable raw or QCOW2 disk. A full copy is made; choose enough disk capacity.';
};
$('#create-form').onsubmit = async event => {
  event.preventDefault();
  const submit = event.submitter;
  submit.disabled = true;
  submit.textContent = 'Creating…';
  $('#cancel-create').disabled = true;
  $('#create-error').hidden = true;
  const data = Object.fromEntries(new FormData(event.target));
  for (const key of ['ram_mb', 'cpus', 'disk_gb']) data[key] = Number(data[key]);
  try {
    await api('/vms', 'POST', data);
    $('#create-dialog').close();
    message(`${data.name} created. Start it when you are ready.`);
    await refresh();
  } catch (error) {
    $('#create-error').textContent = error.message;
    $('#create-error').hidden = false;
  } finally {
    submit.disabled = false;
    submit.textContent = 'Create machine';
    $('#cancel-create').disabled = false;
  }
};

refresh();
setInterval(() => { if (!busy && !document.hidden) refresh(); }, 5000);
