async function fetchAdminMetrics(){
  try {
    const token = localStorage.getItem('seraphonix_token');
    if(!token) return;
    const res = await fetch('/api/admin/metrics', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if(res.ok){
      const m = await res.json();
      document.getElementById('metrics').innerText = JSON.stringify(m, null, 2);
    }
  } catch(err){ console.error(err); }
}
document.addEventListener('DOMContentLoaded', fetchAdminMetrics);
