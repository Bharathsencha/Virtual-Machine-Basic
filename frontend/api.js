/* Copyright (C) 2026 Bharathsencha | SPDX-License-Identifier: GPL-3.0-only */
export async function api(path, method='GET', body) {
  const response = await fetch('/api'+path, {method, headers: body ? {'Content-Type':'application/json'} : {}, body: body ? JSON.stringify(body) : undefined});
  if (!response.ok) { const error = await response.json(); throw new Error(typeof error.detail === 'string' ? error.detail : JSON.stringify(error.detail)); }
  return response.status === 204 ? null : response.json();
}
