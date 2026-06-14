var params = JSON.parse(value);

var event_type = params.event_type;

if (event_type === 'PROBLEM') {
    event_type = 'problem';
} else if (event_type === 'RESOLVED') {
    event_type = 'recovery';
} else {
    event_type = 'problem';
}

var data = {
    event_type: event_type,
    host: params.host,
    ip: params.ip,
    trigger: params.trigger,
    severity: params.severity,
    event_id: params.event_id,
    zabbix_url: params.zabbix_url,
    event_time: params.event_time
};

var request = new HttpRequest();
request.addHeader('Content-Type: application/json');

var response = request.post(
    'http://YOUR_MIDDLEWARE_IP:5000/webhook',
    JSON.stringify(data)
);

return response;
