if (typeof $response !== 'undefined' && $response.body) {
    try {
        let obj = JSON.parse($response.body);

        if (obj.response && obj.response.user) {
            obj.response.user.is_premium = true;
        }
        if (obj.user) {
            obj.user.is_premium = true;
        }

        $done({ body: JSON.stringify(obj) });
    } catch (e) {
        $done({});
    }
} else {
    $done({});
}