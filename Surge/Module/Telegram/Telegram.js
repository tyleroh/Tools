const url = $request.url;

const match = url.match(/^https?:\/\/t\.me\/([^\/\?]+)/);

if (!match) {
  $done({});
}

const username = match[1];

let app = "swiftgram";

if ($argument && $argument.includes("app=")) {
  app = $argument.split("app=")[1];
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