try:
    import requests
    requests_available = True
except:
    requests_available = False

from alerter import Alerter
from pytz import timezone
import pytz

class SlackAlerter(Alerter):
    """Send alerts to a Slack webhook."""

    def __init__(self, config_options):
        if not requests_available:
            print "Requests package is not available, cannot use SlackAlerter."
            return

        Alerter.__init__(self, config_options)
        try:
            url = config_options['url']
        except:
            raise RuntimeError("Required configuration fields missing")

        if 'channel' in config_options:
            channel = config_options['channel']
        else:
            channel = None

        if url == "":
            raise RuntimeError("missing url")

        self.url = url
        self.channel = channel

    def send_alert(self, name, monitor):
        """Send the message."""

        type = self.should_alert(monitor)
        (days, hours, minutes, seconds) = self.get_downtime(monitor)

        host = "on host %s" % self.hostname

        if self.channel is not None:
            message_json = {'channel': self.channel}
        else:
            message_json = {}

        message_json['attachments'] = [{}]

        if type == "":
            return
        elif type == "failure":
            firstFailureTime = monitor.first_failure_time()
            localized_firstFailureTime = pytz.utc.localize(firstFailureTime)
            ist_converted_time = self.format_datetime(localized_firstFailureTime.astimezone(timezone('Asia/Kolkata')))

            message_json['text'] = "CCSimpleMonitor API test run completed."

            message_json['username'] = "V18SimpleMonitor"
            message_json["icon_url"] = "http://i.imgur.com/XdABB5Z.png"

            message_json['attachments'][0]['color'] = 'danger'
            message_json['attachments'][0]['title'] = "Monitor {} failed!".format(name)
            message_json['attachments'][0]['title_link'] = "https://rpm.newrelic.com/accounts/1259793/applications/16687249/transactions#id=5b225765625472616e73616374696f6e2f416374696f6e2f73657276696365732f696e6465782f6164756c742d736561726368222c22225d"

            fields = [
                {
                    'title': 'Failed at',
                    'value': ist_converted_time,
                    'short': True
                },
                {
                    'title': 'Downtime',
                    'value': "{}+{:02d}:{:02d}:{:02d}".format(days, hours, minutes, seconds),
                    'short': True
                },
                {
                    'title': 'Virtual failure count',
                    'value': monitor.virtual_fail_count(),
                    'short': True
                },
                {
                    'title': 'Host',
                    'value': self.hostname,
                    'short': True
                },
                {
                    'title': 'Additional info',
                    'value': monitor.get_result()
                },
                {
                    'title': 'Description',
                    'value': monitor.describe()
                }
            ]

            try:
                if monitor.recover_info != "":
                    fields.append({
                        'title': 'Recovery info',
                        'value': "Recovery info: %s" % monitor.recover_info
                    })
                    message_json['attachments'][0]['color'] = 'warning'
            except AttributeError:
                pass
            message_json['attachments'][0]['fields'] = fields

        elif type == "success":
            firstFailureTime = monitor.first_failure_time()
            localized_firstFailureTime = pytz.utc.localize(firstFailureTime)
            ist_converted_time = self.format_datetime(localized_firstFailureTime.astimezone(timezone('Asia/Kolkata')))

            message_json['text'] = "CCSimpleMonitor API test run completed."

            message_json['username'] = "V18SimpleMonitor"
            message_json["icon_url"] = "http://i.imgur.com/XdABB5Z.png"
            fields = [
                {
                    'title': 'Failed at',
                    'value': ist_converted_time,
                    'short': True
                },
                {
                    'title': 'Downtime',
                    'value': "{}+{:02d}:{:02d}:{:02d}".format(days, hours, minutes, seconds),
                    'short': True
                },
                {
                    'title': 'Host',
                    'value': self.hostname,
                    'short': True
                },
                {
                    'title': 'Description',
                    'value': monitor.describe()
                }
            ]
            message_json['attachments'][0]['color'] = 'good'
            message_json['attachments'][0]['fields'] = fields
            message_json['attachments'][0]['title'] = "Monitor {} succeeded.".format(name)
            message_json['attachments'][0]['title_link'] = "https://rpm.newrelic.com/accounts/1259793/applications/16687249/transactions#id=5b225765625472616e73616374696f6e2f416374696f6e2f73657276696365732f696e6465782f6164756c742d736561726368222c22225d"

        else:
            print "Unknown alert type %s" % type
            return

        if not self.dry_run:
            try:
                r = requests.post(self.url, json=message_json)
                if not r.status_code == 200:
                    print "POST to slack webhook failed"
                    print r
            except Exception, e:
                print "Failed to post to slack webhook"
                print e
                print message_json
                self.available = False
        else:
            print "dry_run: would send slack: %s" % message_json.__repr__()
