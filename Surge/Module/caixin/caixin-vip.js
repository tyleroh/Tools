const body = $response.body;
if (!body) { $done({}); return; }

try {
  const o = JSON.parse(body);
  if (o.data?.info) {
    o.data.info.power = 1;
    o.data.info.errorCode = 0;
    o.data.info.tipsMsg = '';
  }
  $done({ body: JSON.stringify(o) });
} catch (_) {
  $done({});
}
