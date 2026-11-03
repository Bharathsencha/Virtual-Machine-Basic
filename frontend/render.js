/* Copyright (C) 2026 Bharathsencha | SPDX-License-Identifier: GPL-3.0-only */
const $ = selector => document.querySelector(selector);

function cell(row, text, className = '') {
  const element = document.createElement('td');
  element.textContent = text;
  element.className = className;
  row.append(element);
  return element;
}

function button(text, handler, className = '') {
  const element = document.createElement('button');
  element.textContent = text;
  element.className = className;
  element.onclick = handler;
  return element;
}

export function formatUptime(seconds) {
  if (seconds === null) return '—';
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
  return `${Math.floor(seconds / 3600)}h ${Math.floor(seconds % 3600 / 60)}m`;
}

export function renderHost(host) {
  $('#host-cpu').textContent = `${host.cpu_percent.toFixed(1)}%`;
  $('#cpu-meter').value = host.cpu_percent;
  $('#host-memory').textContent = `${host.memory_percent.toFixed(1)}%`;
  $('#memory-meter').value = host.memory_percent;
  $('#host-disk').textContent = `${(host.disk_free_bytes / 1024 ** 3).toFixed(1)} GB`;
  $('#acceleration').textContent = host.kvm_available ? 'KVM' : 'Software';
  $('#acceleration-note').textContent = host.kvm_available ? 'Hardware acceleration available' : 'QEMU TCG emulation';
  const warnings = [host.warning, !host.qemu_available && 'QEMU is missing. Install qemu-system-x86.', !host.qemu_img_available && 'Disk creation unavailable. Install qemu-utils.'].filter(Boolean);
  $('#warning').textContent = warnings.join(' ');
  $('#warning').hidden = !warnings.length;
}

export function renderMachines(machines, query, busy, onAction, onDetails) {
  const running = machines.filter(vm => vm.status === 'running').length;
  $('#summary').textContent = `${running} running · ${machines.length - running} stopped`;
  $('#machine-count').textContent = machines.length;
  const filtered = machines.filter(vm => vm.name.toLowerCase().includes(query.toLowerCase()));
  $('#result-count').textContent = `${filtered.length} of ${machines.length} machine${machines.length === 1 ? '' : 's'}`;
  $('#vms').replaceChildren();
  $('#empty').hidden = machines.length !== 0;
  if (!filtered.length && machines.length) {
    const row = document.createElement('tr');
    cell(row, 'No machines match your filter.').colSpan = 7;
    $('#vms').append(row);
  }
  for (const vm of filtered) {
    const row = document.createElement('tr');
    const name = cell(row, '');
    name.append(button(vm.name, () => onDetails(vm), 'machine-name'));
    const id = document.createElement('span');
    id.className = 'machine-id';
    id.textContent = vm.id.slice(0, 8);
    name.append(id);
    const state = document.createElement('span');
    state.className = `state ${vm.status}`;
    state.textContent = vm.status === 'running' ? 'Running' : 'Stopped';
    cell(row, '').append(state);
    cell(row, `${vm.ram_mb / 1024} GB`);
    cell(row, vm.cpus);
    cell(row, `${vm.disk_gb} GB`);
    cell(row, formatUptime(vm.uptime_seconds));
    const controls = cell(row, '', 'actions');
    const action = vm.status === 'running' ? 'shutdown' : 'start';
    const power = button(action === 'start' ? 'Start' : 'Shut down', () => onAction(vm, action), 'power-action');
    power.disabled = busy;
    controls.append(power, button('Details', () => onDetails(vm)));
    $('#vms').append(row);
  }
}

export function renderDetails(vm, busy, onAction) {
  $('#details-title').textContent = vm.name;
  $('#details-state').textContent = vm.status === 'running' ? 'Running · QEMU process active' : 'Stopped';
  const config = $('#details-config');
  config.replaceChildren();
  for (const [label, value] of [
    ['Machine ID', vm.id], ['Memory allocated', `${vm.ram_mb} MB`], ['vCPUs', vm.cpus],
    ['Disk capacity', `${vm.disk_gb} GB`], ['Boot source', vm.image_type === 'iso' ? 'Linux ISO' : 'Imported disk'],
    ['Source path', vm.image_path], ['Console', vm.console === 'graphical' ? 'Local QEMU window' : 'Local serial socket'],
  ]) {
    const row = document.createElement('div');
    row.className = 'detail-row';
    const term = document.createElement('dt');
    const detail = document.createElement('dd');
    term.textContent = label;
    detail.textContent = value;
    row.append(term, detail);
    config.append(row);
  }
  $('#console-text').textContent = vm.console_instructions;
  const footer = $('#details-dialog footer');
  footer.querySelectorAll('[data-action]').forEach(element => element.remove());
  const actions = vm.status === 'running' ? [['Reset', 'restart'], ['Force stop', 'stop']] : [['Delete machine', 'delete']];
  for (const [text, action] of actions) {
    const control = button(text, () => onAction(vm, action));
    control.dataset.action = action;
    control.disabled = busy;
    footer.prepend(control);
  }
}
