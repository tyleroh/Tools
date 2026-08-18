const url = $request.url;

// 支持 t.me / telegram.me / telegram.dog
const match = url.match(/^https?:\/\/(?:t\.me|telegram\.me|telegram\.dog)\/([^\/\?]+)/);

if (!match) {
  $done({});
}

const username = match[1];

// 解析模块参数，默认 swiftgram
let app = "swiftgram";
if ($argument) {
  const params = new URLSearchParams($argument);
  app = params.get("app") || "swiftgram";
}

let scheme;
switch (app.toLowerCase()) {
  case "telegram":
    scheme = "tg://resolve?domain=";
    break;
  case "turrit":
    scheme = "turrit://resolve?domain=";
    break;
  case "swiftgram":
  default:
    scheme = "sg://resolve?domain=";
    break;
}

$done({
  response: {
    status: 302,
    headers: {
      Location: scheme + username
    }
  }
});